import base64
import json
import time
from typing import Dict, Any

from openai import OpenAI
from loguru import logger

from app.core.config import settings
from app.models.base import BaseModel
from app.prompts.openai_prompts import get_classification_prompt

class OpenAIModel(BaseModel):
    """
    OpenAI Vision model for image classification.
    
    This class implements the BaseModel interface using OpenAI's Vision model
    to classify images into brand safety categories.
    """
    
    def __init__(self):
        """Initialize the OpenAI client with API key from settings."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        logger.info(f"Initialized OpenAI model: {self.model}")
    
    def _encode_image(self, image_path: str) -> str:
        """
        Encode an image as base64.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def classify_image(self, image_path: str) -> Dict[str, Any]:
        """
        Classify an image into brand safety categories.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with classification results
        """
        try:
            start_time = time.time()
            logger.info(f"Classifying image: {image_path}")
            
            # Encode the image
            encode_start = time.time()
            base64_image = self._encode_image(image_path)
            encode_time = time.time() - encode_start
            logger.debug(f"Image encoding took {encode_time:.2f} seconds")
            
            # Get the prompt
            system_prompt = get_classification_prompt()
            
            # Call the OpenAI API
            api_start = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please classify this image for brand safety:"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            api_time = time.time() - api_start
            logger.info(f"OpenAI API request took {api_time:.2f} seconds")
            
            # Process the response
            process_start = time.time()
            result = self._process_response(response, image_path)
            process_time = time.time() - process_start
            logger.debug(f"Response processing took {process_time:.2f} seconds")
            
            # Calculate total time
            total_time = time.time() - start_time
            logger.info(f"Successfully classified image: {image_path} in {total_time:.2f} seconds")
            
            # Add timing information to result
            result["processing_time"] = {
                "total_seconds": round(total_time, 2),
                "api_seconds": round(api_time, 2),
                "encode_seconds": round(encode_time, 2),
                "process_seconds": round(process_time, 2)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying image: {str(e)}")
            raise
    
    def classify_image_url(self, image_url: str) -> Dict[str, Any]:
        """
        Classify an image from a URL into brand safety categories.
        
        Args:
            image_url: URL of the image
            
        Returns:
            Dictionary with classification results
        """
        try:
            start_time = time.time()
            logger.info(f"Classifying image URL: {image_url}")
            
            # Get the prompt
            system_prompt = get_classification_prompt()
            
            # Call the OpenAI API
            api_start = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please classify this image for brand safety:"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            api_time = time.time() - api_start
            logger.info(f"OpenAI API request took {api_time:.2f} seconds")
            
            # Process the response
            process_start = time.time()
            result = self._process_response(response, image_url)
            process_time = time.time() - process_start
            logger.debug(f"Response processing took {process_time:.2f} seconds")
            
            # Calculate total time
            total_time = time.time() - start_time
            logger.info(f"Successfully classified image URL: {image_url} in {total_time:.2f} seconds")
            
            # Add timing information to result
            result["processing_time"] = {
                "total_seconds": round(total_time, 2),
                "api_seconds": round(api_time, 2),
                "process_seconds": round(process_time, 2)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying image URL: {str(e)}")
            raise
    
    def _process_response(self, response, image_path: str) -> Dict[str, Any]:
        """
        Process the OpenAI API response.
        
        Args:
            response: OpenAI API response
            image_path: Path to the image file or URL
            
        Returns:
            Processed classification results
        """
        try:
            # Extract the content from the response
            content = response.choices[0].message.content
            
            # Try to parse the JSON response
            try:
                # Extract JSON from the response (it might be wrapped in markdown code blocks)
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].strip()
                else:
                    json_str = content.strip()
                
                # Parse the JSON
                result = json.loads(json_str)
                
                # Add the image path to the result
                result["image_path"] = image_path
                
                return result
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {content}")
                
                # If JSON parsing fails, create a basic response
                return {
                    "image_path": image_path,
                    "error": "Failed to parse model response",
                    "raw_response": content
                }
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise