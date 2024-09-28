from typing import Annotated

from fastapi import Depends, HTTPException, status, Query, APIRouter
from sqlalchemy.orm import Session

from schemas.stocks import AddNewStockSchema, StockSchema, UpdateStockSchema
from models.stocks import Stock
from dependencies import get_db
from schemas.users import User
from token_utils import get_current_active_user

router = APIRouter()


@router.post("/add_stock", status_code=status.HTTP_201_CREATED,
             responses={
                 401: {"description": "unauthorized",
                       "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
                 400: {"description": "Bad Request",
                       "content": {"application/json": {"example": {"detail": "ticker already exist"}}}}})
async def add_stock(current_user: Annotated[User, Depends(get_current_active_user)],
                    request: AddNewStockSchema, db: Session = Depends(get_db)) -> StockSchema:
    """ used to add new stock to database """
    if db.query(Stock).filter(Stock.ticker == request.ticker).first():
        raise HTTPException(status_code=400, detail="ticker already exist")
    stock = Stock(company_name=request.company_name, ticker=request.ticker, current_price=request.current_price,
                  daily_change_percent=request.daily_change_percent, stock_turnover=request.stock_turnover)
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


@router.get("/get_stock/{stock_ticker}",
            responses={
                401: {"description": "unauthorized",
                      "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
                404: {"description": "not found",
                      "content": {"application/json": {"example": {"detail": "Item not found"}}}}})
async def get_stock(current_user: Annotated[User, Depends(get_current_active_user)],
                    stock_ticker: str, db: Session = Depends(get_db)) -> StockSchema:
    """ used to get all information about a stock form database """
    stock = db.query(Stock).filter(Stock.ticker == stock_ticker).first()
    if stock is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return stock


@router.put("/update_stock/{stock_id}",
            responses={
                200: {"description": "updated successfully"},
                401: {"description": "unauthorized",
                      "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
                404: {"description": "not found",
                      "content": {"application/json": {"example": {"detail": "Item not found"}}}}
            })
async def update_stock(current_user: Annotated[User, Depends(get_current_active_user)],
                       stock_id: int, stock_updates: UpdateStockSchema, db: Session = Depends(get_db)) -> StockSchema:
    """ used to update a stocks data """
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if stock is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = stock_updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(stock, key, value)

    db.commit()
    db.refresh(stock)

    return stock


@router.delete("/delete_stock/{stock_ticker}",
               responses={
                   200: {"description": "deleted successfully", "content": {
                       "application/json": {"example": {"message": "stock AbCd_company got deleted successfully."}}}},
                   401: {"description": "unauthorized",
                         "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
                   404: {"description": "not found",
                         "content": {"application/json": {"example": {"detail": "Item not found"}}}}
               }
               )
async def delete_stock(current_user: Annotated[User, Depends(get_current_active_user)],
                       stock_ticker: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """ used to delete a stock from database by its unique ticker """
    stock = db.query(Stock).filter(Stock.ticker == stock_ticker).first()
    if stock:
        db.delete(stock)
        db.commit()
        return {"message": f"stock {stock_ticker} got deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/stock_list/",
            responses={401: {"description": "unauthorized",
                             "content": {"application/json": {"example": {"detail": "Not authenticated"}}}}})
async def get_stock_list(
        current_user: Annotated[User, Depends(get_current_active_user)],
        company_name: str = Query(None, description="Filter by company name"),
        ticker: str = Query(None, description="Filter by ticker"),
        current_price: str = Query(None, description="Filter by current price"),
        daily_change_percent: str = Query(None, description="Filter by daily change percent"),
        stock_turnover: str = Query(None, description="Filter by item stock turnover"),
        sort_by: str = Query("id",
                             description="Sort by field (company_name, ticker, current_price, daily_change_percent, stock_turnover)"),
        db: Session = Depends(get_db)
) -> list[StockSchema]:
    """ used to return list of all stocks with given order or params """
    query = db.query(Stock)
    query_params = {"company_name": company_name, "ticker": ticker, "current_price": current_price,
                    "daily_change_percent": daily_change_percent, "stock_turnover": stock_turnover}

    user_params = {k: v for k, v in query_params.items() if v is not None}
    if len(user_params) > 0:
        for param in user_params:
            query = query.filter(getattr(Stock, param) == user_params[param])

    if sort_by.startswith("-") and sort_by[1:] in query_params:
        query = query.order_by(getattr(Stock, sort_by).desc())
    elif sort_by in query_params:
        query = query.order_by(getattr(Stock, sort_by).asc())

    return query
