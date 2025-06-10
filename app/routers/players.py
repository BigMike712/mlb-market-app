from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from app.services.mlb_api import fetch_market_data, format_player_listings
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/players", tags=["Players"])

print("players.py loaded")

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

@router.get("/search", response_class=HTMLResponse)
def search_player(name : str , request: Request):
    if not name:
        return templates.TemplateResponse("search_results.html", {
        "request": request,
        "players": []
        })
    
    raw_data = fetch_market_data(name = name)
    formatted_data = format_player_listings(raw_data)

    return templates.TemplateResponse("search_results.html", {
        "request": request,
        "players": formatted_data
    })

