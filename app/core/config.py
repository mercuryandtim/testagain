
# app/core/config.py
import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    MONGO_DETAILS: str = os.getenv("mongodb_uri")
    MongoDB_NAME: str = "OCRwebapp"
    COLLECTION_NAMES: list = ["users", "files", "templates", "extracted data", "external credentials"]
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

print(f"SECRET_KEY: {settings.SECRET_KEY}")  # Add this line to verify the SECRET_KEY