# app/crud/user.py
from app.core.database import get_database
from app.models.users import UserInDB, User
from app.core.security import get_password_hash, verify_password
from bson import ObjectId
from app.core.config import settings
import uuid


async def create_user(user: UserInDB):
    user_dict = user.dict()
    user_dict["user_id"] = str(uuid.uuid4())
    print("user_id:", user_dict["user_id"])
    user_dict["password"] = get_password_hash(user.password)
    db = get_database(settings.MongoDB_NAME)
    result = await db["users"].insert_one(user_dict)
    
    
    return User(**user_dict)

async def get_user_by_username(username: str):
    db = get_database(settings.MongoDB_NAME)
    user = await db["users"].find_one({"username": username})
    return user

async def get_user_by_email(email: str):
    db = get_database(settings.MongoDB_NAME)
    user = await db["users"].find_one({"email": email})
    return user

async def authenticate_user(username: str, password: str):
    user = await get_user_by_email(username)
    print("User:", user)
    if user and verify_password(password, user["password"]):
        return user
    return False