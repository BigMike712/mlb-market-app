from fastapi import APIRouter
from fastapi import Query
from fastapi import Body
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.investment_helpers import create_investment_from_input
from app.models.investment_models import InvestmentIn, Investment, InvestmentUpdate


# In-memory list of investments --> needs to be swapped to storing it into a DB at some point
investments = []

router = APIRouter(prefix="/investments", tags=["Investments"])


# Add a single investment
@router.post("/add")
def add_investment(investment: InvestmentIn):
    new_investment = create_investment_from_input(investment)
    investments.append(new_investment)
    return {"message": "Investment added", "investment": new_investment.dict()}

# Return all investments
@router.get("/")
def get_all_investments():
    result = [dict(i) for i in investments]
    return {"investments" : result}

# Calculate profit of existing investment
@router.get("/profit")
def calculate_profit(
    name : str = Query(),
    sell_price : int = Query()
):
    investment = None
    for i in investments:
        if i.name == name:
            investment = i
            break
    if investment == None:
        return {"error" : "No investment with that name found"}
    profit_per_card = investment.buy_price - (sell_price * 0.9)
    total_profit = profit_per_card * investment.quantity
    roi = (profit_per_card/investment.buy_price) * 100
    return {
        "name" : investment.name,
        "buy_price" : investment.buy_price,
        "sell_price" : sell_price,
        "quantity" : investment.quantity,
        "profit_per_card" : profit_per_card,
        "total_profit" : total_profit,
        "ROI%" : str(roi) + "%"
    }

# Delete existing investment
@router.delete("/delete")
def delete_investment(name : str = Query()):
    investment = None
    for i in investments:
        if i.name == name:
            investment = i
            break
    if investment == None:
        return {"error" : "No investment with that name found"}
    investments.remove(investment)
    return {"message": f"Investment for {investment.name} deleted"}


# Update existing invesment
@router.patch("/update")
def update_investment(
    name : str = Query(),
    update : InvestmentUpdate = Body()
):
    investment = None
    for i in investments:
        if i.name == name:
            investment = i
            break
    if investment == None:
        return {"error" : "No investment with that name found"}
    if update.buy_price is not None:
        investment.buy_price = update.buy_price
    if update.quantity is not None:
        investment.quantity = update.quantity
    if update.qsv is not None:
        investment.qsv = update.qsv

    investment.total_invested = investment.buy_price * investment.quantity
    investment.risk = investment.total_invested - (investment.qsv * investment.quantity)
    investment.updated_at = datetime.utcnow()

    return {
        "message": f"Investment for {investment.name} updated",
        "updated_investment": dict(investment)
    }

# Summary of all investments
@router.get("/summary")
def get_summary():
    total_quantity = 0
    total_stubs_invested = 0
    total_qsv = 0
    total_risk = 0
    for i in investments:
        total_quantity += i.quantity
        total_stubs_invested += (i.buy_price * i.quantity)
        total_qsv += (i.qsv * i.quantity)
        total_risk += i.risk
    return {"total_quantity" : total_quantity, 
            "total_stubs_invested" : total_stubs_invested, 
            "total_qsv" : total_qsv, 
            "total_risk" : total_risk}



