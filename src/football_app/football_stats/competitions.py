from statsbombpy import sb

import json

def get_competitions() -> str:
    return json.dumps(
        sb.competitions().to_dict(orient='records')
    )

def get_matches(competition_id: int, season_id: int) -> str:
    return json.dumps(
        sb.matches(competition_id=competition_id, season_id=season_id).to_dict(orient='records')
    )