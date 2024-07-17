# app/api/v1/endpoints/ocr.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Form
from app.models.users import *
from app.crud.users import *
from app.crud.ocr import *
from app.crud.ocrtemplate import *
from app.models.ocrtemplate import *
from app.core.security import get_password_hash
from app.dependencies import get_current_user

from typing import List

import os


router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to a temporary location
        with open(f"/tmp/{file.filename}", "wb") as buffer:
            buffer.write(await file.read())
        
        # Perform OCR on the saved image
        formatted_output = await do_ocr_tesseract(f"/tmp/{file.filename}")
        
        # Return the formatted output
        return JSONResponse(content=formatted_output)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@router.post("/process")
async def upload_files(files: List[UploadFile] = File(...), template_name: str = Form(...), current_user: User = Depends(get_current_user)):
    results = []
    try:
        for file in files:
            filepath = f"/tmp/{file.filename}"
            # Save the uploaded file to a temporary location
            with open(filepath, "wb") as buffer:
                buffer.write(await file.read())
            
            # Perform OCR on the saved image
            formatted_output = await do_ocr_tesseract(filepath)

            # Parse the output
            parsed_data = await parse_ocr_output(formatted_output, template_name)

            save_data = await create_data_from_template(template_name, parsed_data, current_user['user_id'])

            results.append({"filename": file.filename, "output": formatted_output})

            os.remove(filepath)
        
        # Return the formatted output
        return JSONResponse(content=save_data.dict())

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
def format_string(input_string: str) -> str:
    # Split the string by colon
    parts = input_string.split(':')
    
    # Strip extra spaces from each part
    formatted_parts = [part.strip() for part in parts]
    
    # Join the parts with a single colon
    formatted_string = ':'.join(formatted_parts)
    
    return formatted_string
   
async def parse_ocr_output(raw_output: str, template_name: str) -> Dict[str, str]:

    if raw_output is None:
        return {"error": "No output to parse"}
    if template_name is None:
        return {"error": "No template provided"}
    
    template = await get_template_by_name(template_name)

    lines = raw_output.splitlines()
    #  # Decode escape sequences in the string
    # decoded_output = raw_output.encode().decode('unicode_escape')
    # print(f"Decoded output: {repr(decoded_output)}")

    # lines = decoded_output.splitlines()  # This will handle \n, \r\n, and \r correctly
    # print(f"Lines: {lines}")

    parsed_data = {}
    for line in lines:
        line = format_string(line)
        print(f"Processing line: {line}")
        for field_name, field_value in template.fields.items():
            if line.startswith(field_value + ":"):
                parsed_data[field_value] = line.split(':', 1)[1].strip()
    return parsed_data