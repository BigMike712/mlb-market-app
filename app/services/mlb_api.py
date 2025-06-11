import requests

def fetch_market_data(name=None):
    url = "https://mlb25.theshow.com/apis/listings.json"
    params = {
        "type" : "mlb_card"
    }
    if name:
        params["name"] = name
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception("Failed to fetch data from MLB The Show API")
    
    return response.json()

def format_player_listings(raw_data):
    players = []

    for listing in raw_data.get("listings", []):
        item = listing.get("item", [])
        players.append({
            "name" : item.get("name"),
            "overall" : item.get("ovr"),
            "buy_price" : listing.get("best_buy_price"),
            "sell_price" : listing.get("best_sell_price"),
            "uuid" : item.get("uuid"),
            "img" : item.get("img")
        })

    return players

def get_listing(uuid):
    url = "https://mlb25.theshow.com/apis/listing.json"
    params = {
        "type" : "mlb_card",
        "uuid" : uuid
    }
    response = requests.get(url, params)
    return response.json()