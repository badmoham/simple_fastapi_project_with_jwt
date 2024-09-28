from sqlalchemy import Column, Integer, String, Float
from db import Base


class Stock(Base):
    """ models holding stock related information """
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    ticker = Column(String, unique=True)
    current_price = Column(Integer)
    daily_change_percent = Column(Float)
    stock_turnover = Column(Integer)

