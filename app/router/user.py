

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, joinedload, selectinload
from collections import OrderedDict
import uuid

from app.db.base import *
from app.core import schemas
from app.db.models import models
from app.core.auth import *
# from app.services.email import *
import logging

logging.basicConfig(level=logging.INFO)
router = APIRouter()

# Create a user
@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)):

     # Check if passwords match
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_phone = await get_user_by_phone(db, phone=user.phone)
    if db_user_by_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create the user and add it to the database
    created_user = await create_user_in_db(db=db, user=user)
    
     # Generate the verification link
    verification_link = f"http://localhost:8000/api/v1/user/verify/{created_user.verification_token}"

    print(created_user.verification_token)

     # Send the verification email
    # send_verification_email(created_user.email, verification_link)
    return created_user

@router.get("/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_async_db)):
    async with db as session:
        try:
            user = await get_verification_token(db=session, token=token)
            if not user:
                return {"message": "Invalid or expired verification link"}
                raise HTTPException(status_code=400, detail="Invalid or expired verification link")

            user.is_verified = True
            user.verification_token = None  # Clear the token after verification
            # Commit changes to the database
            await session.commit()

            # Refresh the user object to reflect changes made in the database
            await session.refresh(user)
            
            # Return the updated user
            return {"message": "Email verified successfully"}
        except Exception as e:
            logging.error(f"Error verifying email: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
# Read users with pagination
@router.get("/", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_db),current_user: schemas.User = Depends(get_current_active_user)):
    users = await get_users(db, skip=skip, limit=limit)
    return users

# Read a specific user by ID
@router.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    db_user = await get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Read the current logged-in user
@router.get("/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

# Update a user by ID
@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user_update: schemas.UserUpdate, db: AsyncSession = Depends(get_async_db)):
    async with db as session:
        db_user = await get_user(session, user_id=user_id)
        print("User ID:", id(db_user))  # Print the ID of db_user
        print("Session ID:", id(session))  # Print the ID of the session
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user_update.email and user_update.email != db_user.email:
            db_user.email = user_update.email
        
        # Update user's password if provided
        if user_update.password:
            # Securely hash the password before updating
            db_user.hashed_password = await get_password_hash(user_update.password)
        
        # Update user's active status
        db_user.is_active = user_update.is_active

       
        # Commit changes to the database
        await session.commit()

        # Refresh the user object to reflect changes made in the database
        await session.refresh(db_user)
        
        # Return the updated user
        return db_user

# Delete a user by ID
@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    async with db as session:
        db_user = await get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        await session.delete(db_user)
        await session.commit()
        return JSONResponse(content={"message": f"{db_user.email } has been deleted successfully"})

# User CRUD Operations
async def get_user(session: AsyncSession, user_id: int):
    # async with db as session:
    # async with session.begin():
    stmt = select(models.User).filter(models.User.id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    async with db as session:
        # async with session.begin():
        stmt = select(models.User).filter(models.User.email == email)
        result = await session.execute(stmt)
        return result.scalars().first()

async def get_user_by_phone(db: AsyncSession, phone: str):
    async with db as session:
        stmt = select(models.User).filter(models.User.phone == phone)
        result = await session.execute(stmt)
        return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10):
     async with db as session:
        # async with session.begin():
        stmt = select(models.User).offset(skip).limit(limit)
        result = await session.execute(stmt)
        users = result.unique().scalars().all()
        return users
     
async def get_verification_token(db: AsyncSession, token:str):
 
    stmt = select(models.User).filter(models.User.verification_token == token)
    result = await db.execute(stmt)
    user = result.scalars().first()
    return user


async def create_user_in_db(db: AsyncSession, user: schemas.UserCreate):
     async with db as session:   
        verification_token = str(uuid.uuid4())
        hashed_password = await get_password_hash(user.password)
        # Eagerly load the items along with the user
        created_user = db_user = models.User(
                                    first_name = user.first_name,
                                    surname = user.surname,
                                    email=user.email, 
                                    password=hashed_password, 
                                    phone = user.phone,
                                    is_verified = False, 
                                    verification_token = verification_token)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        stmt = select(models.User).filter(models.User.id == db_user.id)
        result = await session.execute(stmt)
        return result.scalars().first()
        
    
    
    
