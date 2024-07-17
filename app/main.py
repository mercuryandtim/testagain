from fastapi import FastAPI, Depends, HTTPException, status, File,  UploadFile, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
from typing import Annotated
# from transparent_background import Remover
import uvicorn,os

from pymongo import MongoClient, GEOSPHERE
from bson import ObjectId
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from datetime import timedelta, datetime
from dotenv import dotenv_values
from app.api.v1.endpoints import user, auth, ocr, ocrtemplate, config
from app.db.base import *
from app.core.auth import *
# from app.router.user import *
from app.core.database import *


# Load environment variables from .env file
dotenv_values(".env")


# Read environment variables
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", 8080)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app.mongodb_client = MongoClient(mongodb_uri)
    # app.database = app.mongodb_client[db_name]
   
    logger.info("Connected to the MongoDB database!")
    
    try:
        await init_db()
        # collections = app.database.list_collection_names()
        # print(f"Collections in {db_name}: {collections}")
        yield
    except Exception as e:
        logger.error(e)
        
app = FastAPI(lifespan=lifespan)
# Allow CORS for specific origin with credentials
origins = [
    os.getenv("client")
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix='/api/v1/user', tags=["User"])
app.include_router(ocrtemplate.router, prefix='/api/v1/ocrtemplate', tags=["OCR Template"])
app.include_router(ocr.router, prefix='/api/v1/ocr', tags=["OCR"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(config.router, prefix='/api/v1/config', tags=["Config"])


class Destination(BaseModel):
    name: str
    description: str
    location: Dict[str, Any]
    accommodations: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "This is a service to extract the first frame of a video!"}

@app.post("/login")
async def login_for_access_token(response: Response, db: AsyncSession = Depends(get_async_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    print("Access token:", access_token)
    # response.set_cookie("access_token", access_token, httponly=True)
    # return "Login Successful"
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/destinations", response_model=List[Destination])
async def get_destinations():
    db = app.database['destinations']
    destinations = list(db.find())
    return destinations

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")