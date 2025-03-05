import os
import uuid
import time
from typing import Tuple

import requests
from loguru import logger

from app.core.config import settings
from app.utils.image_utils import is_valid_image, normalize_image, get_image_info

class ImageProcessor:
    """
    Service for processing images.
    
    This class provides methods for processing uploaded images and images from URLs.
    It handles validation, normalization, and storage of images.
    """
    
    def __init__(self):
        """Initialize the image processor and create the data directory if needed."""
        # Create data directory if it doesn't exist
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        logger.info(f"Initialized ImageProcessor with data directory: {settings.DATA_DIR}")
    
    def _process_image(self, image_path: str, source_identifier: str, source_type: str) -> Tuple[bool, str]:
        """
        Process an image file after it has been saved to disk.
        
        This is a helper method that handles the common image processing steps:
        validation, normalization, and logging.
        
        Args:
            image_path: Path to the saved image file
            source_identifier: Identifier for the image source (filename or URL)
            source_type: Type of source ('uploaded' or 'url')
            
        Returns:
            Tuple of (success flag, error message)
        """
        try:
            # Validate the image
            if not is_valid_image(image_path):
                error_msg = f"Invalid image format from {source_type}: {source_identifier}"
                logger.error(error_msg)
                return False, error_msg
            
            # Get image info before normalization
            before_info = get_image_info(image_path)
            logger.debug(f"Image info before normalization: {before_info}")
            
            # Normalize the image
            if not normalize_image(image_path):
                error_msg = f"Failed to normalize image from {source_type}: {source_identifier}"
                logger.error(error_msg)
                return False, error_msg
            
            # Get image info after normalization
            after_info = get_image_info(image_path)
            logger.debug(f"Image info after normalization: {after_info}")
            
            return True, ""
            
        except Exception as e:
            error_msg = f"Error processing image from {source_type}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_uploaded_image(self, file) -> Tuple[str, bool]:
        """
        Process an uploaded image file.
        
        This method saves the uploaded file, validates it, and normalizes it.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (image path, success flag)
        """
        start_time = time.time()
        try:
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(settings.DATA_DIR, filename)
            
            # Save the uploaded file
            with open(image_path, "wb") as buffer:
                buffer.write(file.file.read())
            
            # Log with clear mapping between original filename and UUID filename
            logger.info(f"Saved uploaded image '{file.filename}' to: {image_path} (UUID-generated filename)")
            
            # Process the image
            success, error_msg = self._process_image(image_path, file.filename, 'uploaded')
            if not success:
                os.remove(image_path)
                return "", False
            
            process_time = time.time() - start_time
            logger.info(f"[IMAGE_PROCESSOR] Successfully processed uploaded image '{file.filename}' (saved as {os.path.basename(image_path)}) in {process_time:.2f} seconds")
            return image_path, True
            
        except Exception as e:
            logger.error(f"Error processing uploaded image: {str(e)}")
            return "", False
    
    def process_image_url(self, url: str) -> Tuple[str, bool]:
        """
        Process an image from a URL.
        
        This method downloads the image from the URL, validates it, and normalizes it.
        
        Args:
            url: URL of the image
            
        Returns:
            Tuple of (image path, success flag)
        """
        start_time = time.time()
        try:
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(settings.DATA_DIR, filename)
            
            logger.info(f"Downloading image from URL: {url}")
            
            # Download the image
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code != 200:
                error_msg = f"Failed to download image from URL: {url}, status code: {response.status_code}"
                logger.error(error_msg)
                return "", False
            
            # Save the downloaded image
            with open(image_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            # Log with clear mapping between URL and UUID filename
            logger.info(f"Saved image from URL '{url}' to: {image_path} (UUID-generated filename)")
            
            # Process the image
            success, error_msg = self._process_image(image_path, url, 'url')
            if not success:
                os.remove(image_path)
                return "", False
            
            process_time = time.time() - start_time
            logger.info(f"[IMAGE_PROCESSOR] Successfully processed image from URL '{url}' (saved as {os.path.basename(image_path)}) in {process_time:.2f} seconds")
            return image_path, True
            
        except Exception as e:
            logger.error(f"Error processing image URL: {str(e)}")
            return "", False