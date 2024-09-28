from typing import Optional

from pydantic import BaseModel


class AddNewStockSchema(BaseModel):
    company_name: str
    ticker: str
    current_price: int
    daily_change_percent: float
    stock_turnover: int


class UpdateStockSchema(BaseModel):
    company_name: Optional[str] = None
    ticker: Optional[str] = None
    current_price: Optional[int] = None
    daily_change_percent: Optional[float] = None
    stock_turnover: Optional[int] = None


class StockSchema(BaseModel):
    id: int
    company_name: str
    ticker: str
    current_price: int
    daily_change_percent: float
    stock_turnover: int
