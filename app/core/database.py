# app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_DETAILS)

def get_database(db_name:str):
    return client[db_name]

async def create_collection(db_name:str, collection_name:str):
    database = get_database(db_name)
    existing_collections = await database.list_collection_names()
    if collection_name not in existing_collections:
        await database.create_collection(collection_name)
    else:
        print(f"Collection '{collection_name}' already exists in database '{db_name}'")


async def list_collection_names(db_name: str):
    database = get_database(db_name)
    collection_names = await database.list_collection_names()
    return collection_names

async def init_db():
    print(settings.MongoDB_NAME)
    for collection_name in settings.COLLECTION_NAMES:
        await create_collection(settings.MongoDB_NAME, collection_name)
    
    collections = await list_collection_names(settings.MongoDB_NAME)
    print(f"Collections in '{settings.MongoDB_NAME}': {collections}")
 