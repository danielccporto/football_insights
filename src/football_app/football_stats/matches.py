import json
import pandas as pd
import numpy as np

from copy import copy
from statsbombpy import sb
from typing import List
import requests 


class PlayerStatsError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def to_json(df: pd.DataFrame) -> str:
    return json.dumps(df, indent=2)


def get_events(match_id: int) -> str:
    """
    Retrieve all events of a match and format them in JSON.

    Args:
        match_id (int): The ID of the match.

    Returns:
        str: JSON string with all match events.
    """
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return json.dumps([
        {k: v for k, v in event.items() if v is not np.nan}
        for event in full_events.sort_values(by="minute").to_dict(orient='records')
    ])


def filter_main_events(events: pd.DataFrame) -> dict:
    """
    Filter main events (goals, assists, and cards) from the match events.

    Args:
        events (pd.DataFrame): DataFrame with all match events.

    Returns:
        dict: Filtered main events (goals, assists, and cards).
    """
    goals = events[(events['type'] == 'Shot') & (events['shot_outcome'] == 'Goal')]
    assists = events[(events['type'] == 'Pass') & (events.get('pass_assist', False) == True)]

    # Filter cards only if 'card_type' exists in the DataFrame
    if 'card_type' in events.columns:
        cards = events[events['type'] == 'Card']
        cards = cards[['player', 'team', 'minute', 'card_type']]
    else:
        cards = pd.DataFrame(columns=['player', 'team', 'minute', 'card_type'])

    return {
        "goals": goals[['player', 'team', 'minute']].to_dict(orient='records'),
        "assists": assists[['player', 'team', 'minute']].to_dict(orient='records'),
        "cards": cards[['player', 'team', 'minute', 'card_type']].to_dict(orient='records'),
    }


def get_main_events(match_id: int) -> str:
    """
    Retrieve and filter main events (goals, assists, and cards) from a match.

    Args:
        match_id (int): The ID of the match.

    Returns:
        str: JSON string with main events (goals, assists, and cards).
    """
    try: 
        events = sb.events(match_id=match_id)
        if isinstance(events, str):
            events = pd.DataFrame(json.loads(events))
        main_events = filter_main_events(events)
        return to_json(main_events)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data from StatsBomb API: {str(e)}")
    except Exception as e:
        raise Exception(f"An error occurred while processing the match events: {str(e)}")


def get_player_stats(match_id: int, player_name: str) -> str:
    """
    Returns the consolidated statistics of a specific player in a match.

    Parameters:
        match_id (int): ID of the match (provided by StatsBomb).
        player_name (str): Full name of the player.

    Returns:
        str: Consolidated statistics of the player in JSON format.
    """
    try:
        # Load match events
        events = sb.events(match_id=match_id)

        # Validate if events were loaded
        if events.empty:
            raise PlayerStatsError(f"No events found for the match with ID {match_id}.")

        # Filter events for the specific player
        player_events = events[events['player'] == player_name]

        # Check if the player is present in the events
        if player_events.empty:
            raise PlayerStatsError(f"No events found for player '{player_name}' in match {match_id}.")

        # Consolidate statistics
        profile = {
            "player_name": player_name,
            "passes": {
                "completed": int(player_events[(player_events['type'] == 'Pass') & player_events['pass_outcome'].isna()].shape[0]),
                "attempted": int(player_events[player_events['type'] == 'Pass'].shape[0])
            },
            "shots": {
                "total": int(player_events[player_events['type'] == 'Shot'].shape[0]),
                "on_target": int(player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'On Target')].shape[0])
            },
            "defensive": {
                "tackles": int(player_events[player_events['type'] == 'Tackle'].shape[0]),
                "interceptions": int(player_events[player_events['type'] == 'Interception'].shape[0])
            },
            "fouls": {
                "committed": int(player_events[player_events['type'] == 'Foul Committed'].shape[0]),
                "won": int(player_events[player_events['type'] == 'Foul Won'].shape[0])
            },
            "minutes_played": int(player_events['minute'].max())
        }
        return json.dumps(profile)

    except Exception as e:
        return json.dumps({"error": str(e)})


def get_player_profile(match_id: int, player_name: str) -> str:
    """
    Generate a detailed profile of a specific player in a match.

    Args:
        match_id (int): The ID of the match.
        player_name (str): The name of the player.

    Returns:
        str: A JSON string containing the player's profile with detailed statistics.
    """
    try:
        # Carregar os eventos da partida
        events = sb.events(match_id=match_id)

        # Filtrar eventos do jogador específico
        player_events = events[events['player'] == player_name]
        if player_events.empty:
            return json.dumps({"error": f"No events found for player: {player_name}"})

        # Consolidar estatísticas do jogador
        profile = {
            "player_name": player_name,
            "passes_completed": int(player_events[(player_events['type'] == 'Pass') & player_events['pass_outcome'].isna()].shape[0]),
            "passes_attempted": int(player_events[player_events['type'] == 'Pass'].shape[0]),
            "shots": int(player_events[player_events['type'] == 'Shot'].shape[0]),
            "shots_on_target": int(player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'On Target')].shape[0]),
            "tackles": int(player_events[player_events['type'] == 'Tackle'].shape[0]),
            "interceptions": int(player_events[player_events['type'] == 'Interception'].shape[0]),
            "fouls_committed": int(player_events[player_events['type'] == 'Foul Committed'].shape[0]),
            "minutes_played": int(player_events['minute'].max())
        }

        # Retornar o perfil em formato JSON
        return json.dumps(profile)

    except Exception as e:
        return json.dumps({"error": str(e)})
    
def get_lineups(match_id: int) -> str:
    """
    Fetch and process the lineups of a match.
    """
    data = sb.lineups(match_id=match_id)
    data_final = copy(data)
    list_fields = ['cards', 'positions']
    for field in list_fields:
        for key, df in data.items():
            df[field] = df[field].apply(lambda v: {field: v})
            data_final[key] = df.to_dict(orient='records')
    return json.dumps(data_final)

