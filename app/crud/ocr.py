import asyncio
from PIL import Image
import pytesseract
import re, cv2
import imutils
from concurrent.futures import ThreadPoolExecutor
from app.models.ocrtemplate import *
from app.core.database import get_database
from app.core.config import settings
from typing import Any
from fastapi import HTTPException
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def identify_structure(line):
    line = line.strip()
    
    if line.count(':') > 1:
        return 'mixed-column'
    
    if ':' in line or re.search(r'^[A-Za-z]+\s+[A-Za-z0-9]+', line):
        return 'key-value'
    
    uppercase_words = re.findall(r'\b[A-Z]+\b', line)
    numbers = re.findall(r'\b\d+\b', line)
    
    if len(uppercase_words) > 1:
        return 'table-header'
    
    if len(numbers) > 1 and len(uppercase_words) <= 1:
        return 'table-row'
    
    return 'text'

def format_extracted_text(text):
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    formatted_text = []
    in_table = False
    
    for line in lines:
        structure = identify_structure(line)
        
        if structure == 'mixed-column':
            parts = line.split(':')
            formatted_parts = [f"{parts[i].strip()}: {parts[i+1].strip()}" for i in range(0, len(parts)-1, 2)]
            formatted_text.extend(formatted_parts)
            in_table = False
        elif structure == 'key-value':
            formatted_text.append(line)
            in_table = False
        elif structure == 'table-header':
            formatted_text.append(line)
            in_table = True
        elif structure == 'table-row' and in_table:
            formatted_text.append(line)
        else:
            if in_table:
                in_table = False
                formatted_text.append("\n")
            formatted_text.append(line)
    
    return "\n".join(formatted_text)

def refine_text_formatting(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\s', '.\n', text)
    text = re.sub(r'\s*:\s*', ': ', text)
    return text

def do_ocr(image_path):
    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image)
    formatted_text = format_extracted_text(extracted_text)
    return formatted_text

async def do_ocr_tesseract(image_path):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        formatted_text = await loop.run_in_executor(pool, do_ocr, image_path)
    return formatted_text


async def create_data_from_template(template_name:str, fields:Dict[str, str], user_id:str) -> OCRTemplateInDB:
    template = OCRTemplateInDB(template_name=template_name, fields=fields, user_id=user_id)
    db = get_database(settings.MongoDB_NAME)
    result = await db["extracted data"].insert_one(template.dict())
    if template:
        return template
    return None


def preprocess_image(image: Any) -> Any:
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Apply Otsu's thresholding
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise and invert image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    invert = 255 - opening
    
    return invert

async def detect_rotation(image_path: str) -> Any:
    # Load the input image
    image = cv2.imread(image_path)
    if image is None:
        raise HTTPException(status_code=400, detail="Image not found or unable to read")

    # Convert from BGR to RGB channel ordering
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Use Tesseract to determine the text orientation
    results = pytesseract.image_to_osd(rgb, output_type=Output.DICT)
    
    # Display the orientation information
    print("[INFO] detected orientation: {}".format(results["orientation"]))
    print("[INFO] rotate by {} degrees to correct".format(results["rotate"]))
    print("[INFO] detected script: {}".format(results["script"]))
    
    # Rotate the image to correct the orientation
    rotated = imutils.rotate_bound(image, angle=results["rotate"])
    
    return rotated

async def tesseract_ocr(image_path: str) -> str:
    # Detect rotation and get the image
    image = await detect_rotation(image_path)
    
    # Preprocess the image
    preprocessed_image = preprocess_image(image)

    # Perform OCR using Tesseract
    result = pytesseract.image_to_string(preprocessed_image, config='--psm 6')

    formatted_text = format_extracted_text(result)
    return formatted_text
# Example usage
async def main():
    image_path = 'KTP.jpg'
    formatted_text = await do_ocr_tesseract(image_path)
    formatted_text_pre = await tesseract_ocr(image_path)
    print(formatted_text)
    print(formatted_text_pre)

# asyncio.run(main())


