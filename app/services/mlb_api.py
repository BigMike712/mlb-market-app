import requests

def fetch_market_data():
    url = "https://mlb25.theshow.com/apis/listings.json"
    response = requests.get(url)

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
            "sell_price" : listing.get("best_sell_price")
        })

    return players