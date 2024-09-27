from fastapi import FastAPI, Depends, HTTPException, status, Query

from models import Stake
from schemas import AddNewStakeSchema, StakeSchema, UpdateStakeSchema
from db import engine, SessionLocal, Base
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    """ connection to sqlite database """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def index() -> dict[str, str]:
    """ temporary index page that is gonna get deleted """
    return {"message": "you are welcome"}


@app.post("/add_stake", status_code=status.HTTP_201_CREATED,
          responses={400: {"description": "Bad Request",
                           "content": {"application/json": {"example": {"detail": "ticker already exist"}}}}})
async def add_stake(request: AddNewStakeSchema, db: Session = Depends(get_db)) -> StakeSchema:
    """ used to add new stake to database """
    if db.query(Stake).filter(Stake.ticker == request.ticker).first():
        raise HTTPException(status_code=400, detail="ticker already exist")
    stake = Stake(company_name=request.company_name, ticker=request.ticker, current_price=request.current_price,
                  daily_change_percent=request.daily_change_percent, stock_turnover=request.stock_turnover)
    db.add(stake)
    db.commit()
    db.refresh(stake)
    return stake


@app.get("/get_stake/{stake_ticker}",
         responses={404: {"description": "not found",
                          "content": {"application/json": {"example": {"detail": "Item not found"}}}}})
async def add_stake(stake_ticker: str, db: Session = Depends(get_db)) -> StakeSchema:
    """ used to get all information about a stake form database """
    stake = db.query(Stake).filter(Stake.ticker == stake_ticker).first()
    if stake is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return stake


@app.put("/update_stake/{stake_id}",
         responses={
             200: {"description": "updated successfully"},
             404: {"description": "not found",
                   "content": {"application/json": {"example": {"detail": "Item not found"}}}}
         })
def update_stake(stake_id: int, stake_updates: UpdateStakeSchema, db: Session = Depends(get_db)) -> StakeSchema:
    """ used to update a stakes data """
    stake = db.query(Stake).filter(Stake.id == stake_id).first()
    if stake is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = stake_updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(stake, key, value)

    db.commit()
    db.refresh(stake)

    return stake


@app.delete("/delete_stake/{stake_ticker}",
            responses={
                200: {"description": "deleted successfully", "content": {
                    "application/json": {"example": {"message": "stake AbCd_company got deleted successfully."}}}},
                404: {"description": "not found",
                      "content": {"application/json": {"example": {"detail": "Item not found"}}}}
            }
            )
def delete_stake(stake_ticker: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """ used to delete a stake from database by its unique ticker """
    stake = db.query(Stake).filter(Stake.ticker == stake_ticker).first()
    if stake:
        db.delete(stake)
        db.commit()
        return {"message": f"stake {stake_ticker} got deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/stake_list/")
async def read_items(
        company_name: str = Query(None, description="Filter by company name"),
        ticker: str = Query(None, description="Filter by ticker"),
        current_price: str = Query(None, description="Filter by current price"),
        daily_change_percent: str = Query(None, description="Filter by daily change percent"),
        stock_turnover: str = Query(None, description="Filter by item stock turnover"),
        sort_by: str = Query("id", description="Sort by field (company_name, ticker, current_price, daily_change_percent, stock_turnover)"),
        db: Session = Depends(get_db)
) -> list[StakeSchema]:
    """ used to return list of all stakes with given order or params """
    query = db.query(Stake)
    query_params = {"company_name": company_name, "ticker": ticker, "current_price": current_price,
                    "daily_change_percent": daily_change_percent, "stock_turnover": stock_turnover}

    user_params = {k: v for k, v in query_params.items() if v is not None}
    if len(user_params) > 0:
        for param in user_params:
            query = query.filter(getattr(Stake, param) == user_params[param])

    if sort_by.startswith("-") and sort_by[1:] in query_params:
        query = query.order_by(getattr(Stake, sort_by).desc())
    elif sort_by in query_params:
        query = query.order_by(getattr(Stake, sort_by).asc())

    return query
