from fastapi import FastAPI, HTTPException, Depends
from app.core.database import get_database
from app.models.ocrtemplate import OCRTemplate, OCRTemplateInDB
from app.core.security import get_password_hash, verify_password
from bson import ObjectId
from app.core.config import settings
from typing import List, Optional, Union
from pymongo import ReturnDocument



async def create_template(template: OCRTemplate, user_id: str, templateForAll: Optional[bool] = False):
    existing_template = await get_template_by_name_and_user(template.template_name, user_id)
    if existing_template:
        raise HTTPException(status_code=401, detail="Template already exists")

    template_dict = template.dict()
    if templateForAll:
        template_dict["user_id"] = "all"
    else:
        template_dict["user_id"] = user_id
    db = get_database(settings.MongoDB_NAME)
    template = await db["templates"].insert_one(template_dict)
    if template:
        return OCRTemplate(**template_dict)
    return None

async def get_all_templates():
    db = get_database(settings.MongoDB_NAME)
    templates = await db["templates"].find().to_list(1000)
    return [OCRTemplateInDB(**template) for template in templates]

async def get_all_templates_by_user_id(user_id: str, template_name: Optional[bool] = False)->  Union[List[OCRTemplateInDB], List[dict]]:
    db = get_database(settings.MongoDB_NAME)

    # Query to find templates with user_id equal to the given user_id or "all"
    templates = await db["templates"].find({
        "$or": [
            {"user_id": user_id},
            {"user_id": "all"}
        ]
    }).to_list(1000)
    # templates = await db["templates"].find({"user_id": user_id}).to_list(1000)

    if template_name:
        # Return only the template_name field
        return [{"template_name": template["template_name"]} for template in templates]

    return [OCRTemplateInDB(**template) for template in templates]
   
async def get_template_by_name(template_name: str) -> OCRTemplate:
    db = get_database(settings.MongoDB_NAME)
    template = await db["templates"].find_one({"template_name": template_name})
    if template:
        return OCRTemplate(**template)
    return None

async def get_template_by_name_and_user(template_name: str, user_id: Optional[str]) -> OCRTemplate:
    query = {"template_name": template_name, "user_id": user_id}
    print("Query:", query)
    db = get_database(settings.MongoDB_NAME)
    template = await db["templates"].find_one(query)
    print(template)
    if template:
        return OCRTemplate(**template)
    return None

async def update_template(template_name: str, template: OCRTemplate, user_id: str):
    query = {"template_name": template_name, "user_id": user_id}
    print("Query:", query)
    db = get_database(settings.MongoDB_NAME)
    updated_template = await db["templates"].find_one_and_update(
        query, 
        {"$set": template.dict()},
        return_document=ReturnDocument.AFTER
    )
    if updated_template:
        return OCRTemplate(**updated_template)
    return None

async def delete_template(template_name: str, user_id: str):
    query = {"template_name": template_name, "user_id": user_id}
    print("Query:", query)
    db = get_database(settings.MongoDB_NAME)
    deleted_template = await db["templates"].find_one_and_delete(query)
    if deleted_template:
        return OCRTemplate(**deleted_template)
    return None
