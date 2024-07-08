from fastapi import Depends
from sqlalchemy import Column, DateTime, Integer, String, Boolean, select
from app.db.base import Base
import datetime
from sqlalchemy.orm import declarative_base


# Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    country = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    verification_token = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    password = Column(String(255), nullable=False)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)

   
