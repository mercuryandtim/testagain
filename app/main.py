from fastapi import FastAPI, Depends, HTTPException, status, File,  UploadFile, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
from typing import Annotated
# from transparent_background import Remover
import uvicorn,os

from datetime import timedelta
from dotenv import load_dotenv
from app.db.base import *
from app.core.auth import *
from app.router.user import *

# Load environment variables from .env file
load_dotenv()


# Read environment variables
host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", 7860))
print(host,port)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix='/api/v1/user', tags=["User"])

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


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")