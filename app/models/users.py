# app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta, datetime

class User(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserInDB(User):
    is_validated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[str] = None
