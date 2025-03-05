from unittest.mock import patch, MagicMock

from app.models.openai_model import OpenAIModel

class TestOpenAIModel:
    """
    Tests for the OpenAIModel class.
    
    These tests verify that the OpenAI model correctly classifies images
    and handles errors appropriately.
    """
    
    def setup_method(self):
        """Set up the test environment."""
        # Create a mock OpenAI client
        self.mock_client = MagicMock()
        
        # Create a mock response
        self.mock_response = MagicMock()
        self.mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""
                    ```json
                    {
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
                    ```
                    """
                )
            )
        ]
        
        # Set up the mock client to return the mock response
        self.mock_client.chat.completions.create.return_value = self.mock_response
    
    @patch('app.models.openai_model.OpenAI')
    def test_init(self, mock_openai):
        """Test that the model is initialized correctly."""
        # Set up the mock
        mock_openai.return_value = self.mock_client
        
        # Create an instance of the model to trigger the initialization
        model = OpenAIModel()
        
        # Check that the client was created with the correct API key
        mock_openai.assert_called_once()
    
    @patch('app.models.openai_model.OpenAI')
    @patch('app.models.openai_model.base64.b64encode')
    @patch('builtins.open', new_callable=MagicMock)
    def test_classify_image(self, mock_open, mock_b64encode, mock_openai):
        """Test that the model correctly classifies an image."""
        # Set up the mocks
        mock_openai.return_value = self.mock_client
        mock_b64encode.return_value = b'encoded_image'
        mock_open.return_value.__enter__.return_value.read.return_value = b'image_data'
        
        # Create the model
        model = OpenAIModel()
        
        # Classify an image
        result = model.classify_image('79d754a275386650e7e71d67f3cde5f2.png')
        
        # Check that the client was called with the correct parameters
        self.mock_client.chat.completions.create.assert_called_once()
        
        # Check that the result contains the expected keys
        assert 'adultContentRating' in result
        assert 'adultContentRating_confidence_score' in result
        assert 'adultContentRating_explanation' in result
        assert 'image_path' in result
        assert result['image_path'] == '79d754a275386650e7e71d67f3cde5f2.png'
    
    @patch('app.models.openai_model.OpenAI')
    def test_classify_image_url(self, mock_openai):
        """Test that the model correctly classifies an image URL."""
        # Set up the mock
        mock_openai.return_value = self.mock_client
        
        # Create the model
        model = OpenAIModel()
        
        # Classify an image URL
        result = model.classify_image_url('https://brandsafety-crawler.s3.amazonaws.com/screenshots/79d754a275386650e7e71d67f3cde5f2.png')
        
        # Check that the client was called with the correct parameters
        self.mock_client.chat.completions.create.assert_called_once()
        
        # Check that the result contains the expected keys
        assert 'adultContentRating' in result
        assert 'adultContentRating_confidence_score' in result
        assert 'adultContentRating_explanation' in result
        assert 'image_path' in result
        assert result['image_path'] == 'https://brandsafety-crawler.s3.amazonaws.com/screenshots/79d754a275386650e7e71d67f3cde5f2.png'
    
    @patch('app.models.openai_model.OpenAI')
    def test_process_response_json_error(self, mock_openai):
        """Test that the model handles JSON parsing errors correctly."""
        # Set up the mock
        mock_openai.return_value = self.mock_client
        
        # Create a mock response with invalid JSON
        invalid_response = MagicMock()
        invalid_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="This is not valid JSON"
                )
            )
        ]
        
        # Create the model
        model = OpenAIModel()
        
        # Process the invalid response
        result = model._process_response(invalid_response, '79d754a275386650e7e71d67f3cde5f2.png')
        
        # Check that the result contains an error
        assert 'error' in result
        assert result['error'] == 'Failed to parse model response'
        assert 'raw_response' in result
        assert result['raw_response'] == 'This is not valid JSON'