from typing import Annotated
from datetime import timedelta

from fastapi import Depends, HTTPException, status , APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from schemas.users import Token, User
from token_utils import authenticate_user, create_access_token, get_current_active_user

from secrets import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2y$10$VGvTHX9Scr2rt6v3yzRQh.6LCmseyvRCM/QkECz0MPOuwyz3itfCe",  # password: 123456
        "disabled": False,
    }
}


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
