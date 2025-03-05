from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseModel(ABC):
    """
    Base class for all vision models.
    
    This abstract class defines the interface that all vision models must implement.
    It provides methods for classifying images from both file paths and URLs.
    """
    
    @abstractmethod
    def classify_image(self, image_path: str) -> Dict[str, Any]:
        """
        Classify an image into brand safety categories.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with classification results for all brand safety categories
        """
        pass
    
    @abstractmethod
    def classify_image_url(self, image_url: str) -> Dict[str, Any]:
        """
        Classify an image from a URL into brand safety categories.
        
        Args:
            image_url: URL of the image
            
        Returns:
            Dictionary with classification results for all brand safety categories
        """
        pass