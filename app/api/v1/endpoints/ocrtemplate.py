from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.ocrtemplate import OCRTemplate
from app.models.users import User
from app.crud.ocrtemplate import *
from app.dependencies import get_current_user  # Assume this dependency retrieves the current user # Assume you have a database dependency

router = APIRouter()

# In-memory storage for simplicity; replace with your database logic
templates = {}

@router.post("/", response_model=OCRTemplate)
async def create_OCR_template(template: OCRTemplate, current_user: User = Depends(get_current_user)):
    
    template = await create_template(template, current_user['user_id'])
    return template

@router.get("/", response_model=List[Union[OCRTemplateInDB, dict]])
async def get_OCR_templates_for_user(template_name:Optional[bool] = False, current_user: User = Depends(get_current_user)):
    
    templates = await get_all_templates_by_user_id(current_user['user_id'], template_name)
    return templates

@router.get("/{template_name}", response_model=OCRTemplate)
async def get_template(template_name: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    template = await get_template_by_name_and_user(template_name, user_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates", response_model=OCRTemplate)
async def update_template_endpoint(template: OCRTemplate, user: str = Depends(get_current_user)):
    print("Updating template:", template)
    print("User ID:", user['user_id'])
    updated_template = await update_template(template.template_name, template, user['user_id'])
    if not updated_template:
        raise HTTPException(status_code=404, detail="Template not found or could not be updated")
    return updated_template

@router.delete("/{template_name}")
async def delete_template_endpoint(template_name: str, current_user: str = Depends(get_current_user)):
    user_id = current_user['user_id']
    
    deleted_template = await delete_template(template_name, user_id)
    if not deleted_template:
        raise HTTPException(status_code=404, detail="Template not found or could not be deleted")
    return {"detail": f"{template_name } templatedeleted"}
