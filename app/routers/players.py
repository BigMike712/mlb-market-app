from fastapi import APIRouter
from fastapi import Query
from app.services.mlb_api import fetch_market_data, format_player_listings

router = APIRouter(prefix="/players", tags=["Players"])

# When someone sends a GET request to the route /players/, call the function below:
@router.get("/")
def list_players():
    return {"message": "This will list player data soon!"}

@router.get("/live-prices")
def get_live_prices(
    sort : str = Query(default = None), 
    min_ovr : int = Query(default = None),
    max_ovr : int = Query(default = None),
    limit : int = Query(default = None)
):
    raw_data = fetch_market_data()
    players = format_player_listings(raw_data)
    # Sort functionality
    if sort != None:
        players = sorted(players, key = lambda p : (p.get(sort) is None, p.get(sort)))       
    # Min overall filter
    if min_ovr != None:
        players = [p for p in players if (p["overall"] != None) & (p["overall"] >= min_ovr)]
    # Max overall filter
    if max_ovr != None:
        players = [p for p in players if (p["overall"] != None) & (p["overall"] <= max_ovr)]
    # Limit functionality
    if limit != None:
        players = players[:limit]
    return {"count" : len(players), "players" : players} 

@router.get("/search")
def search_player(name : str = Query()):
    raw_data = fetch_market_data(name = name)
    formatted_data = format_player_listings(raw_data)
    return{"count" : len(formatted_data), "results" : formatted_data}

