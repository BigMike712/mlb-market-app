from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Investment(BaseModel):
    name: str
    overall: int
    buy_price: int
    quantity: int
    total_invested: int
    qsv: int
    risk: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class InvestmentIn(BaseModel):
    uuid: str
    buy_price: int = Field(..., gt=0, description="Price per card in stubs (must be > 0)")
    quantity: int = Field(..., gt=0, description="Number of cards purchased (must be > 0)")

class InvestmentUpdate(BaseModel):
    buy_price: Optional[int] = None
    quantity: Optional[int] = None
    qsv: Optional[int] = None