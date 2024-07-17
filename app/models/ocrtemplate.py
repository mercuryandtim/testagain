from pydantic import BaseModel, Field
from typing import Dict, Optional

class OCRTemplate(BaseModel):
    template_name: str
    fields: Dict[str, str]
    user_id: Optional[str] = Field(None, description="ID of the user who owns the template. None for common templates.")

class OCRTemplateInDB(BaseModel):
    template_name: str
    fields: Dict[str, str]
    user_id: str