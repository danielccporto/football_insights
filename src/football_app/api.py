from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.football_app.football_stats.matches import get_main_events, get_player_profile
import json 


# Cria a instância do FastAPI
app = FastAPI(title="Football Insights API")

# Modelos Pydantic para entrada e saída
class MatchSummaryRequest(BaseModel):
    match_id: int

class MatchSummaryResponse(BaseModel):
    goals: list
    assists: list
    cards: list

class PlayerProfileRequest(BaseModel):
    match_id: int
    player_name: str

class PlayerProfileResponse(BaseModel):
    player_name: str
    passes_completed: int
    passes_attempted: int   
    shots: int
    shots_on_target: int
    tackles: int
    interceptions: int
    fouls_committed: int
    minutes_played: int

# Endpoint: /match_summary
@app.post("/match_summary", response_model=MatchSummaryResponse)
def match_summary(request: MatchSummaryRequest):
    try:
        events_json = get_main_events(request.match_id)
        events_dict = json.loads(events_json)        
        return events_dict
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint: /player_profile
@app.post("/player_profile", response_model=PlayerProfileResponse)
def player_profile(request: PlayerProfileRequest):
    try:
        # Chama a função para o perfil do jogador
        profile_json = get_player_profile(request.match_id, request.player_name)
        
        # Transforma a string JSON em um dicionário Python
        profile_dict = json.loads(profile_json)
        
        return profile_dict
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
