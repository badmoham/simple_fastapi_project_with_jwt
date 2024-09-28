from fastapi import FastAPI

from db import engine, Base
from routers import stocks, users


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(stocks.router)
app.include_router(users.router)
