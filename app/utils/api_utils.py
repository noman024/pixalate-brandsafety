from typing import Dict, Any

from fastapi import HTTPException
from loguru import logger

def format_error_response(error_message: str, status_code: int = 500) -> Dict[str, Any]:
    """
    Format an error response.
    
    This function creates a standardized error response format for API endpoints.
    
    Args:
        error_message: Error message
        status_code: HTTP status code
        
    Returns:
        Formatted error response
    """
    return {
        "success": False,
        "error": {
            "message": error_message,
            "code": status_code
        }
    }

def format_success_response(data: Any) -> Dict[str, Any]:
    """
    Format a success response.
    
    This function creates a standardized success response format for API endpoints.
    
    Args:
        data: Response data
        
    Returns:
        Formatted success response
    """
    return {
        "success": True,
        "data": data
    }

def handle_api_error(error: Exception, default_message: str = "An unexpected error occurred") -> HTTPException:
    """
    Handle API errors.
    
    This function logs the error and creates an HTTPException with an appropriate
    error message and status code.
    
    Args:
        error: Exception that occurred
        default_message: Default error message
        
    Returns:
        HTTPException to be raised
    """
    # Log the error
    logger.error(f"API Error: {str(error)}")
    
    # Determine the error message and status code
    if hasattr(error, "detail"):
        error_message = error.detail
    else:
        error_message = str(error) or default_message
    
    # Determine the status code
    if hasattr(error, "status_code"):
        status_code = error.status_code
    else:
        status_code = 500
    
    # Create and return the HTTPException
    return HTTPException(
        status_code=status_code,
        detail=format_error_response(error_message, status_code)
    )

def validate_image_format(content_type: str) -> bool:
    """
    Validate the image format based on content type.
    
    This function checks if the content type is a supported image format.
    
    Args:
        content_type: Content type of the uploaded file
        
    Returns:
        True if the format is supported, False otherwise
    """
    supported_formats = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp"
    ]
    
    return content_type in supported_formats