import requests
from app.models.investment_models import InvestmentIn, Investment
from datetime import datetime

def create_investment_from_input(investment_in: InvestmentIn) -> Investment: 
    # Extract player data using MLBTS API
    url = "https://mlb25.theshow.com/apis/listing.json"
    response = requests.get(url, params={"uuid":investment_in.uuid})
    data = response.json()
    item = data["item"]

    # Assign variables to then create Investment instance
    name = item["name"]
    ovr = item["ovr"]
    buy_price = investment_in.buy_price
    quantity = investment_in.quantity
    total_invested = buy_price*quantity
    
    # Check if card is Live Series or not:
    series = item.get("series", "")
    is_live = series.lower() == "live"
    qsv = get_qsv_from_overall(ovr, is_live)

    risk = total_invested - (qsv*quantity)
    created_at = datetime.utcnow()
    return Investment(
        name = name,
        overall = ovr,
        buy_price = buy_price,
        quantity = quantity,
        total_invested = total_invested,
        qsv = qsv,
        risk = risk,
        created_at = created_at,
        updated_at = None
    )

def get_qsv_from_overall(ovr: int, is_live: bool) -> int:
    if is_live:
        if ovr < 65: return 5
        elif ovr >= 65 and ovr <= 74: return 25
        elif ovr == 75: return 50
        elif ovr == 76: return 75
        elif ovr == 77: return 100
        elif ovr == 78: return 125
        elif ovr == 79: return 150
        elif ovr == 80: return 400
        elif ovr == 81: return 600
        elif ovr == 82: return 900
        elif ovr == 83: return 1200
        elif ovr == 84: return 1500
        elif ovr == 85: return 3000
        elif ovr == 86: return 3750
        elif ovr == 87: return 4500
        elif ovr == 88: return 5500
        elif ovr == 89: return 7000
        elif ovr == 90: return 8000
        elif ovr == 91: return 9000
        elif ovr >= 92: return 10000
    else:
        if ovr < 65: return 2
        elif ovr >= 65 and ovr <= 74: return 12
        elif ovr == 75: return 25
        elif ovr == 76: return 37
        elif ovr == 77: return 50
        elif ovr == 78: return 62
        elif ovr == 79: return 75
        elif ovr == 80: return 200
        elif ovr == 81: return 300
        elif ovr == 82: return 450
        elif ovr == 83: return 600
        elif ovr == 84: return 750
        elif ovr == 85: return 1500
        elif ovr == 86: return 1875
        elif ovr == 87: return 2250
        elif ovr == 88: return 2750
        elif ovr == 89: return 3500
        elif ovr == 90: return 4000
        elif ovr == 91: return 4500
        elif ovr >= 92: return 5000

