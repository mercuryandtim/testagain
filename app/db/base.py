import asyncio, contextlib, logging, os, sys, time
from dotenv import load_dotenv
from typing import AsyncIterator, Any, Dict, List, Optional, Tuple, Type, Union
# from app.db.models.models import Base

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)


load_dotenv()

from sqlalchemy import text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# # Define the MySQL connection details
username = os.getenv("usernameDb")
password = os.getenv("password")
host = os.getenv("host")  # e.g., 'localhost' or '127.0.0.1'
# port = os.getenv("port")  # Default MySQL port
database_name = os.getenv("database_name")


# username = 'hidh4125_admin'
# password = 'Alberto471'
# host = 'hidigi.asia'  # e.g., 'localhost' or '127.0.0.1'
port = '3306'  # Default MySQL port
# database_name = 'hidh4125_speechRecognition'

print(username,password,host,port,database_name)

# Create an engine to connect to the MySQL server
engine = create_async_engine(f'mysql+aiomysql://{username}:{password}@{host}:{port}/{database_name}', echo=True, future=True)


async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def create_async_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class DatabaseSessionManager:
    def __init__(self, sessionmaker, engine):
        self.sessionmaker = sessionmaker
        self.engine = engine

    async def close(self):
        if(self.engine):
            await self.engine.dispose()
            
    @contextlib.asynccontextmanager
    async def create_session(self) ->AsyncIterator[AsyncSession]:
        session = self.sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

session_manager = DatabaseSessionManager(async_session, engine)

async def get_async_db():
    async with session_manager.create_session() as session:
        try:
            yield session
        finally:
            await session.close()