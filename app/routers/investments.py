from fastapi import APIRouter
from fastapi import Query
from pydantic import BaseModel
from dataclasses import dataclass

class Investment:
    name: str
    overall: int
    buy_price: int
    qsv: int
    risk: int

class InvestmentIn(BaseModel):
    name: str
    overall: int
    buy_price: int
    qsv: int
    risk: int

investments = []

router = APIRouter(prefix="/investments", tags=["Investments"])

@router.post("/add")
def add_investment(investment: InvestmentIn):
    new_investment = Investment(**investment.dict())
    investments.append(new_investment)
    return {"message": "Investment added", "investment": investment}

