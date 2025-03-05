import os

from PIL import Image
from loguru import logger

from app.core.config import settings

def is_valid_image(image_path: str) -> bool:
    """
    Check if an image is valid.
    
    This function validates an image file by checking its format and size.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if the image is valid, False otherwise
    """
    try:
        # Try to open the image
        with Image.open(image_path) as img:
            # Check if the format is supported
            if img.format and img.format.lower() not in settings.SUPPORTED_FORMATS:
                logger.warning(f"Unsupported image format: {img.format}")
                return False
            
            # Check if the image is too large
            if os.path.getsize(image_path) > settings.MAX_IMAGE_SIZE:
                logger.warning(f"Image too large: {os.path.getsize(image_path)} bytes")
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"Error validating image: {str(e)}")
        return False

def normalize_image(image_path: str) -> bool:
    """
    Normalize an image (resize, convert to RGB, etc.).
    
    This function normalizes an image by converting it to RGB format if needed
    and resizing it if it's too large, while preserving the aspect ratio.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize if too large (preserving aspect ratio)
            max_size = 1024
            if img.width > max_size or img.height > max_size:
                # Calculate new dimensions
                if img.width > img.height:
                    new_width = max_size
                    new_height = int(img.height * (max_size / img.width))
                else:
                    new_height = max_size
                    new_width = int(img.width * (max_size / img.height))
                
                # Resize the image
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Save the normalized image
            img.save(image_path, "JPEG", quality=85)
            
            return True
            
    except Exception as e:
        logger.error(f"Error normalizing image: {str(e)}")
        return False

def get_image_info(image_path: str) -> dict:
    """
    Get information about an image.
    
    This function extracts information about an image, such as its dimensions,
    format, and mode.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image information
    """
    try:
        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": os.path.getsize(image_path)
            }
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return {}