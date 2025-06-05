from fastapi import APIRouter
from fastapi import Query
from fastapi import Body
from pydantic import BaseModel, Field
from dataclasses import dataclass
from dataclasses import asdict
from typing import Optional

@dataclass
class Investment:
    name: str
    overall: int
    buy_price: int
    quantity: int
    total_invested: int
    qsv: int
    risk: int

class InvestmentIn(BaseModel):
    uuid: str
    buy_price: int = Field(..., gt=0, description="Price per card in stubs (must be > 0)")
    quantity: int = Field(..., gt=0, description="Number of cards purchased (must be > 0)")

class InvestmentUpdate(BaseModel):
    buy_price: Optional[int] = None
    quantity: Optional[int] = None
    qsv: Optional[int] = None

investments = []

# -------- Helper Function --------
def format_investment(investment):
    flag = ""
    if investment.risk > 0.5 * investment.buy_price:
        flag = "⚠️ HIGH RISK"
    return{
        f"Name: {investment.name} | "
        f"OVR: {investment.overall} | "
        f"Buy Price: {investment.buy_price} | "
        f"QSV: {investment.qsv} | "
        f"Quantity: {investment.quantity} | "
        f"Total Invested: {investment.total_invested} | "
        f"Risk: {investment.risk} {flag}"
    }


router = APIRouter(prefix="/investments", tags=["Investments"])

# Pretty printout of investments
@router.get("/pretty")
def print_pretty_all():
    return{"investments" : [format_investment(i) for i in investments]}

# Add a single investment
@router.post("/add")
def add_investment(investment: InvestmentIn):
    investments.append(investment)
    return {"message": "Investment added", "investment": investment.dict()}

# Return all investments
@router.get("/")
def get_all_investments():
    result = [asdict(i) for i in investments]
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
    return {"message": "Investment for Shohei Ohtani deleted"}


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

    return {
        "message": f"Investment for {investment.name} updated",
        "updated_investment": asdict(investment)
    }

# Summary of all investments
@router.get("/summary")
def get_summary():
    total_quantity = 0
    for i in investments:
        total_quantity += i.quantity
    total_stubs_invested = 0
    for i in investments:
        total_stubs_invested += (i.buy_price * i.quantity)
    total_qsv = 0
    for i in investments:
        total_qsv += (i.qsv * i.quantity)
    total_risk = 0
    for i in investments:
        total_risk += i.risk
    return {"total_quantity" : total_quantity, 
            "total_stubs_invested" : total_stubs_invested, 
            "total_qsv" : total_qsv, 
            "total_risk" : total_risk}



