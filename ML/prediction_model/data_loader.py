import os
import json
import time
import requests
import pandas as pd

# -----------------------------
# Load roster update metadata
# -----------------------------
def get_update_data(id:int):
    url = "https://mlb25.theshow.com/apis/roster_update.json"
    params = {"id" : id}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    data = response.json()
    return data

# -----------------------------
# Caching logic for player data
# -----------------------------
def get_cached_player_data(uuid: str, cache_dir="cache-5-23") -> dict:
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"player_{uuid}.json")

    # Return from cache if exists
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)

    # Otherwise, fetch from API
    data = get_player_data(uuid)
    if data:
        with open(cache_path, "w") as f:
            json.dump(data, f)
    return data

def get_player_data(uuid: str) -> dict:
    url = "https://mlb25.theshow.com/apis/item.json"
    params = {"id": uuid}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch player {uuid}: {response.status_code}")
    return response.json()

# -----------------------------
# Build roster update dataset
# -----------------------------
def load_roster_update_data(id: int) -> pd.DataFrame:
    update_data = get_update_data(id)
    players = []
    for player in update_data.get("attribute_changes", []):
        name = player.get("name")
        old_overall = player.get("old_rank")
        new_overall = player.get("current_rank")
        # Extract players UUID
        item = player.get("item", {})
        uuid = item.get("uuid") if item else None
        # Add label if upgraded or not
        label = 1 if new_overall > old_overall else 0
        # Append to our running list of players
        players.append({
            "player_name": name,
            "player_id": uuid,
            "old_overall": old_overall,
            "new_overall": new_overall,
            "upgrade_label": label
    })
    return pd.DataFrame(players)


# -----------------------------
# Build attribute dataset
# -----------------------------
def load_player_attributes(uuids: list[str], sleep_time=0.25) -> pd.DataFrame:
    players_attributes = []
    
