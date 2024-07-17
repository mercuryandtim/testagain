from fastapi import FastAPI, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
import os

class ConfigUpdateRequest(BaseModel):
    MONGO_DETAILS: Optional[str] = None
    MongoDB_NAME: Optional[str] = None
    COLLECTION_NAMES: Optional[List[str]] = None
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None