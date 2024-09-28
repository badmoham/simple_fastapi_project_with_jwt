from typing import Annotated

from fastapi import Depends, HTTPException, status, Query, APIRouter
from sqlalchemy.orm import Session

from schemas.stakes import AddNewStakeSchema, StakeSchema, UpdateStakeSchema
from models.stakes import Stake
from dependencies import get_db
from schemas.users import User
from token_utils import get_current_active_user

router = APIRouter()


@router.post("/add_stake", status_code=status.HTTP_201_CREATED,
             responses={
                 401: {"description": "unauthorized",
                       "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
                 400: {"description": "Bad Request",
                       "content": {"application/json": {"example": {"detail": "ticker already exist"}}}}})
async def add_stake(current_user: Annotated[User, Depends(get_current_active_user)],
                    request: AddNewStakeSchema, db: Session = Depends(get_db)) -> StakeSchema:
    """ used to add new stake to database """
    if db.query(Stake).filter(Stake.ticker == request.ticker).first():
        raise HTTPException(status_code=400, detail="ticker already exist")
    stake = Stake(company_name=request.company_name, ticker=request.ticker, current_price=request.current_price,
                  daily_change_percent=request.daily_change_percent, stock_turnover=request.stock_turnover)
    db.add(stake)
    db.commit()
    db.refresh(stake)
    return stake


@router.get("/get_stake/{stake_ticker}",
            responses={
                401: {"description": "unauthorized",
                      "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
                404: {"description": "not found",
                      "content": {"application/json": {"example": {"detail": "Item not found"}}}}})
async def get_stake(current_user: Annotated[User, Depends(get_current_active_user)],
                    stake_ticker: str, db: Session = Depends(get_db)) -> StakeSchema:
    """ used to get all information about a stake form database """
    stake = db.query(Stake).filter(Stake.ticker == stake_ticker).first()
    if stake is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return stake


@router.put("/update_stake/{stake_id}",
            responses={
                200: {"description": "updated successfully"},
                401: {"description": "unauthorized",
                      "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
                404: {"description": "not found",
                      "content": {"application/json": {"example": {"detail": "Item not found"}}}}
            })
async def update_stake(current_user: Annotated[User, Depends(get_current_active_user)],
                       stake_id: int, stake_updates: UpdateStakeSchema, db: Session = Depends(get_db)) -> StakeSchema:
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


@router.delete("/delete_stake/{stake_ticker}",
               responses={
                   200: {"description": "deleted successfully", "content": {
                       "application/json": {"example": {"message": "stake AbCd_company got deleted successfully."}}}},
                   401: {"description": "unauthorized",
                         "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
                   404: {"description": "not found",
                         "content": {"application/json": {"example": {"detail": "Item not found"}}}}
               }
               )
async def delete_stake(current_user: Annotated[User, Depends(get_current_active_user)],
                       stake_ticker: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """ used to delete a stake from database by its unique ticker """
    stake = db.query(Stake).filter(Stake.ticker == stake_ticker).first()
    if stake:
        db.delete(stake)
        db.commit()
        return {"message": f"stake {stake_ticker} got deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/stake_list/",
            responses={401: {"description": "unauthorized",
                             "content": {"application/json": {"example": {"detail": "Not authenticated"}}}}})
async def get_stake_list(
        current_user: Annotated[User, Depends(get_current_active_user)],
        company_name: str = Query(None, description="Filter by company name"),
        ticker: str = Query(None, description="Filter by ticker"),
        current_price: str = Query(None, description="Filter by current price"),
        daily_change_percent: str = Query(None, description="Filter by daily change percent"),
        stock_turnover: str = Query(None, description="Filter by item stock turnover"),
        sort_by: str = Query("id",
                             description="Sort by field (company_name, ticker, current_price, daily_change_percent, stock_turnover)"),
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
