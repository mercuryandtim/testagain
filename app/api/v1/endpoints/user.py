# app/api/v1/endpoints/user.py
from fastapi import APIRouter, Depends, HTTPException
from app.models import users
from app.crud.users import *
from app.core.security import get_password_hash
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/")
async def register_user(user: users.User):

    db_user = await get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = await get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_in_db = UserInDB(**user.dict(), hashed_password=get_password_hash(user.password))

    user = await create_user(user_in_db)

    return user

@router.get("/me/", response_model=users.User)
async def read_users_me(current_user: users.User = Depends(get_current_user)):
    print("Current user:", current_user)

    
    return current_user
