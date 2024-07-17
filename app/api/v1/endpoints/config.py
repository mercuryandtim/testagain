from fastapi import APIRouter, Depends, HTTPException
from app.db.models.config import *
from app.core.config import settings


router = APIRouter()

@router.get("/", response_model=ConfigUpdateRequest)
async def get_config():
    return settings

@router.put("/", response_model=ConfigUpdateRequest)
async def update_config(config: ConfigUpdateRequest):
    if config.MONGO_DETAILS is not None and config.MONGO_DETAILS != "string":
        settings.MONGO_DETAILS = config.MONGO_DETAILS
    if config.MongoDB_NAME is not None and config.MongoDB_NAME != "string":
        settings.MongoDB_NAME = config.MongoDB_NAME
    if config.COLLECTION_NAMES is not None and config.COLLECTION_NAMES != "string":
        settings.COLLECTION_NAMES = config.COLLECTION_NAMES
    if config.SECRET_KEY is not None and config.SECRET_KEY != "string":
        settings.SECRET_KEY = config.SECRET_KEY
    if config.ALGORITHM is not None and config.ALGORITHM != "string":   
        settings.ALGORITHM = config.ALGORITHM
    if config.ACCESS_TOKEN_EXPIRE_MINUTES is not None and config.ACCESS_TOKEN_EXPIRE_MINUTES != 0:
        settings.ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

    # return {
    #     "MONGO_DETAILS": settings.MONGO_DETAILS,
    #     "MongoDB_NAME": settings.MongoDB_NAME,
    #     "COLLECTION_NAMES": settings.COLLECTION_NAMES,
    #     "SECRET_KEY": settings.SECRET_KEY,
    #     "ALGORITHM": settings.ALGORITHM,
    #     "ACCESS_TOKEN_EXPIRE_MINUTES": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    # }
    return settings


