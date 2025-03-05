from fastapi.testclient import TestClient
from unittest.mock import patch

from app.api.main import app

client = TestClient(app)

class TestEndpoints:
    """
    Tests for the API endpoints.
    
    These tests verify that the API endpoints correctly handle requests
    and return appropriate responses.
    """
    
    def setup_method(self):
        """Set up the test environment."""
        # Create a mock classification result
        self.mock_result = {
            "image_path": "79d754a275386650e7e71d67f3cde5f2.png",
            "adultContentRating": "high",
            "adultContentRating_confidence_score": "98%",
            "adultContentRating_explanation": "large number of adult content detected in the image.",
            "drugsContentRating": "medium",
            "drugsContentRating_confidence_score": "67%",
            "drugsContentRating_explanation": "moderate drugs content detected in the image.",
            "alcoholContentRating": "medium",
            "alcoholContentRating_confidence_score": "70%",
            "alcoholContentRating_explanation": "moderate alcohol content detected in the image.",
            "hateSpeechRating": "medium",
            "hateSpeechRating_confidence_score": "64%",
            "hateSpeechRating_explanation": "moderate hate speech detected in the image.",
            "armsAndAmmunitionRating": "low",
            "armsAndAmmunitionRating_confidence_score": "0%",
            "armsAndAmmunitionRating_explanation": "No arms or ammunition detected in the image.",
            "deathInjuryOrMilitaryConflictRating": "low",
            "deathInjuryOrMilitaryConflictRating_confidence_score": "0%",
            "deathInjuryOrMilitaryConflictRating_explanation": "No death, injury, or military conflict detected in the image.",
            "terrorismRating": "low",
            "terrorismRating_confidence_score": "0%",
            "terrorismRating_explanation": "No terrorism content detected in the image.",
            "obscenityAndProfanityRating": "low",
            "obscenityAndProfanityRating_confidence_score": "0%",
            "obscenityAndProfanityRating_explanation": "No obscenity or profanity detected in the image."
        }
    
    def test_health_check(self):
        """Test that the health check endpoint returns a 200 status code."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "status" in response.json()["data"]
        assert response.json()["data"]["status"] == "ok"
    
    @patch('app.api.endpoints.classification.classification_service')
    def test_classify_image_success(self, mock_service):
        """Test that the classify image endpoint correctly handles a successful request."""
        # Set up the mock
        mock_service.classify_uploaded_image.return_value = self.mock_result
        
        # Create a test file
        files = {"file": ("79d754a275386650e7e71d67f3cde5f2.png", b"image_data", "image/png")}
        
        # Make the request
        response = client.post("/api/v1/classify", files=files)
        
        # Check the response
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["data"]["adultContentRating"] == "high"
        assert response.json()["data"]["drugsContentRating"] == "medium"
    
    @patch('app.api.endpoints.classification.classification_service')
    def test_classify_image_error(self, mock_service):
        """Test that the classify image endpoint correctly handles an error."""
        # Set up the mock
        mock_service.classify_uploaded_image.return_value = {"error": "Test error"}
        
        # Create a test file
        files = {"file": ("79d754a275386650e7e71d67f3cde5f2.png", b"image_data", "image/png")}
        
        # Make the request
        response = client.post("/api/v1/classify", files=files)
        
        # Check the response
        assert response.status_code == 500
        assert response.json()["success"] is False
        assert response.json()["error"]["message"] == "Test error"
    
    @patch('app.api.endpoints.classification.classification_service')
    def test_classify_image_invalid_format(self, mock_service):
        """Test that the classify image endpoint correctly handles an invalid file format."""
        # Create a test file with an invalid format
        files = {"file": ("test_file.txt", b"text_data", "text/plain")}
        
        # Make the request
        response = client.post("/api/v1/classify", files=files)
        
        # Check the response
        assert response.status_code == 400
        assert response.json()["success"] is False
        assert "Unsupported file format" in response.json()["error"]["message"]
    
    @patch('app.api.endpoints.classification.classification_service')
    def test_classify_image_url_success(self, mock_service):
        """Test that the classify image URL endpoint correctly handles a successful request."""
        # Set up the mock
        mock_service.classify_image_url.return_value = self.mock_result
        
        # Make the request
        response = client.post(
            "/api/v1/classify-url",
            json={"url": "https://brandsafety-crawler.s3.amazonaws.com/screenshots/79d754a275386650e7e71d67f3cde5f2.png"}
        )
        
        # Check the response
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["data"]["adultContentRating"] == "high"
        assert response.json()["data"]["drugsContentRating"] == "medium"
    
    @patch('app.api.endpoints.classification.classification_service')
    def test_classify_image_url_error(self, mock_service):
        """Test that the classify image URL endpoint correctly handles an error."""
        # Set up the mock
        mock_service.classify_image_url.return_value = {"error": "Test error"}
        
        # Make the request
        response = client.post(
            "/api/v1/classify-url",
            json={"url": "https://brandsafety-crawler.s3.amazonaws.com/screenshots/79d754a275386650e7e71d67f3cde5f2.png"}
        )
        
        # Check the response
        assert response.status_code == 500
        assert response.json()["success"] is False
        assert response.json()["error"]["message"] == "Test error"
    
    def test_classify_image_url_invalid_url(self):
        """Test that the classify image URL endpoint correctly handles an invalid URL."""
        # Make the request with an invalid URL
        response = client.post(
            "/api/v1/classify-url",
            json={"url": "not_a_url"}
        )
        
        # Check the response
        assert response.status_code == 422  # Validation error