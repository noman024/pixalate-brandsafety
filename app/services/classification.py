import os
import json
import time
from typing import Dict, Any, Tuple

from loguru import logger

from app.models.openai_model import OpenAIModel
from app.services.image_processor import ImageProcessor
from app.core.config import settings

class ClassificationService:
    """
    Service for classifying images.
    
    This class provides methods for classifying uploaded images and images from URLs
    using the OpenAI Vision model.
    """
    
    def __init__(self):
        """Initialize the classification service with the OpenAI model and image processor."""
        self.model = OpenAIModel()
        self.image_processor = ImageProcessor()
        logger.info("Initialized ClassificationService")
    
    def classify_uploaded_image(self, file) -> Dict[str, Any]:
        """
        Classify an uploaded image.
        
        This method processes the uploaded image and classifies it using the OpenAI model.
        The results are also saved to a JSON file in the data directory.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Classification results
        """
        start_time = time.time()
        try:
            logger.info(f"Classifying uploaded image: {file.filename}")
            
            # Process the uploaded image
            process_start = time.time()
            image_path, success = self.image_processor.process_uploaded_image(file)
            process_time = time.time() - process_start
            logger.debug(f"Image processing took {process_time:.2f} seconds")
            
            if not success:
                error_message = f"Failed to process the uploaded image: {file.filename}"
                logger.error(error_message)
                return {"error": error_message}
            
            # Classify the image
            classify_start = time.time()
            result = self.model.classify_image(image_path)
            classify_time = time.time() - classify_start
            logger.debug(f"Image classification took {classify_time:.2f} seconds")
            
            # Save the results to a JSON file
            save_start = time.time()
            self._save_results_to_file(result, image_path)
            save_time = time.time() - save_start
            logger.debug(f"Saving results took {save_time:.2f} seconds")
            
            # Calculate total service time
            total_time = time.time() - start_time
            # Include both original filename and UUID filename in the log
            logger.info(f"[SERVICE] Successfully classified uploaded image '{file.filename}' (saved as {os.path.basename(image_path)}) in {total_time:.2f} seconds")
            
            # Add service timing information to result
            if "processing_time" not in result:
                result["processing_time"] = {}
            
            result["processing_time"].update({
                "service_total_seconds": round(total_time, 2),
                "image_processing_seconds": round(process_time, 2),
                "save_results_seconds": round(save_time, 2)
            })
            
            return result
            
        except Exception as e:
            error_message = f"Error classifying uploaded image: {str(e)}"
            logger.error(error_message)
            return {"error": error_message}
    
    def classify_image_url(self, url: str) -> Dict[str, Any]:
        """
        Classify an image from a URL.
        
        This method processes the image from the URL and classifies it using the OpenAI model.
        The results are also saved to a JSON file in the data directory.
        
        Args:
            url: URL of the image
            
        Returns:
            Classification results
        """
        start_time = time.time()
        try:
            logger.info(f"Classifying image URL: {url}")
            
            # Process the image URL
            process_start = time.time()
            image_path, success = self.image_processor.process_image_url(url)
            process_time = time.time() - process_start
            logger.debug(f"Image URL processing took {process_time:.2f} seconds")
            
            if not success:
                error_message = f"Failed to process the image URL: {url}"
                logger.error(error_message)
                return {"error": error_message}
            
            # Classify the image
            classify_start = time.time()
            result = self.model.classify_image(image_path)
            classify_time = time.time() - classify_start
            logger.debug(f"Image classification took {classify_time:.2f} seconds")
            
            # Save the results to a JSON file
            save_start = time.time()
            self._save_results_to_file(result, image_path)
            save_time = time.time() - save_start
            logger.debug(f"Saving results took {save_time:.2f} seconds")
            
            # Calculate total service time
            total_time = time.time() - start_time
            # Include both URL and UUID filename in the log
            logger.info(f"[SERVICE] Successfully classified image URL '{url}' (saved as {os.path.basename(image_path)}) in {total_time:.2f} seconds")
            
            # Add service timing information to result
            if "processing_time" not in result:
                result["processing_time"] = {}
            
            result["processing_time"].update({
                "service_total_seconds": round(total_time, 2),
                "image_processing_seconds": round(process_time, 2),
                "save_results_seconds": round(save_time, 2)
            })
            
            return result
            
        except Exception as e:
            error_message = f"Error classifying image URL: {str(e)}"
            logger.error(error_message)
            return {"error": error_message}
    
    def _save_results_to_file(self, result: Dict[str, Any], image_path: str) -> Tuple[str, bool]:
        """
        Save classification results to a JSON file.
        
        Args:
            result: Classification results
            image_path: Path to the image file
            
        Returns:
            Tuple of (results file path, success flag)
        """
        try:
            # Get the image filename without extension
            image_filename = os.path.basename(image_path)
            image_name = os.path.splitext(image_filename)[0]
            
            # Create the results filename
            results_filename = f"{image_name}_results.json"
            results_path = os.path.join(settings.DATA_DIR, results_filename)
            
            # Get the size of the result data
            result_size = len(json.dumps(result))
            
            # Save the results to a JSON file
            with open(results_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Saved classification results to: {results_path} (size: {result_size} bytes)")
            return results_path, True
            
        except Exception as e:
            logger.error(f"Error saving classification results: {str(e)}")
            return "", False
    
    def get_results_filename(self, image_path: str) -> str:
        """
        Get the results filename for an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Results filename
        """
        # Get the image filename without extension
        image_filename = os.path.basename(image_path)
        image_name = os.path.splitext(image_filename)[0]
        
        # Create the results filename
        return f"{image_name}_results"