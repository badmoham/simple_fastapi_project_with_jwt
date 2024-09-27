from typing import Optional

from pydantic import BaseModel


class AddNewStakeSchema(BaseModel):
    company_name: str
    ticker: str
    current_price: int
    daily_change_percent: float
    stock_turnover: int


class UpdateStakeSchema(BaseModel):
    company_name: Optional[str] = None
    ticker: Optional[str] = None
    current_price: Optional[int] = None
    daily_change_percent: Optional[float] = None
    stock_turnover: Optional[int] = None


class StakeSchema(BaseModel):
    id: int
    company_name: str
    ticker: str
    current_price: int
    daily_change_percent: float
    stock_turnover: int
