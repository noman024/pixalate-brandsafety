from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from loguru import logger
import time

from app.services.classification import ClassificationService
from app.utils.api_utils import format_success_response, format_error_response, validate_image_format, handle_api_error

router = APIRouter()

# Create a global instance of the classification service
classification_service = ClassificationService()

class ImageUrlRequest(BaseModel):
    """
    Request model for image URL classification.
    
    This model defines the structure of the request body for the image URL classification endpoint.
    """
    url: HttpUrl

@router.post("/classify")
async def classify_image(file: UploadFile = File(...)):
    """
    Classify an uploaded image into brand safety categories.
    
    This endpoint accepts an uploaded image file and classifies it into various
    brand safety categories using the OpenAI Vision model.
    
    Args:
        file: Uploaded image file
        
    Returns:
        Classification results
    """
    start_time = time.time()
    try:
        logger.info(f"Received image classification request: {file.filename}")
        
        # Check if the file is an image
        if not validate_image_format(file.content_type):
            error_message = f"Unsupported file format: {file.content_type}"
            logger.error(error_message)
            return JSONResponse(
                status_code=400,
                content=format_error_response(error_message, 400)
            )
        
        # Classify the image
        result = classification_service.classify_uploaded_image(file)
        
        # Check for errors
        if "error" in result:
            error_message = result["error"]
            logger.error(error_message)
            return JSONResponse(
                status_code=500,
                content=format_error_response(error_message, 500)
            )
        
        # Calculate total endpoint processing time
        total_time = time.time() - start_time
        # Include the original filename and note that it was processed with a UUID filename
        logger.info(f"[API] Successfully classified image '{file.filename}' (Total endpoint time: {total_time:.2f}s)")
        
        return format_success_response(result)
        
    except Exception as e:
        # Handle unexpected errors
        raise handle_api_error(e, f"Failed to classify image: {str(e)}")

@router.post("/classify-url")
async def classify_image_url(request: ImageUrlRequest):
    """
    Classify an image from a URL into brand safety categories.
    
    This endpoint accepts an image URL and classifies it into various
    brand safety categories using the OpenAI Vision model.
    
    Args:
        request: Request containing the image URL
        
    Returns:
        Classification results
    """
    start_time = time.time()
    try:
        url = str(request.url)
        logger.info(f"Received image URL classification request: {url}")
        
        # Classify the image URL
        result = classification_service.classify_image_url(url)
        
        # Check for errors
        if "error" in result:
            error_message = result["error"]
            logger.error(error_message)
            return JSONResponse(
                status_code=500,
                content=format_error_response(error_message, 500)
            )
        
        # Calculate total endpoint processing time
        total_time = time.time() - start_time
        logger.info(f"[API] Successfully classified image URL: {url} (Total endpoint time: {total_time:.2f}s)")
        
        return format_success_response(result)
        
    except Exception as e:
        # Handle unexpected errors
        raise handle_api_error(e, f"Failed to classify image URL: {str(e)}")