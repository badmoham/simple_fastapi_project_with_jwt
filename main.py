from fastapi import FastAPI

from db import engine, Base
from routers import stakes, users


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(stakes.router)
app.include_router(users.router)
