from unittest.mock import patch, MagicMock, mock_open

from app.services.image_processor import ImageProcessor

class TestImageProcessor:
    """
    Tests for the ImageProcessor class.
    
    These tests verify that the image processor correctly handles uploaded images
    and image URLs.
    """
    
    def setup_method(self):
        """Set up the test environment."""
        # Create a mock file
        self.mock_file = MagicMock()
        self.mock_file.filename = "79d754a275386650e7e71d67f3cde5f2.png"
        self.mock_file.file.read.return_value = b"image_data"
        
        # Create a mock response for URL requests
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.iter_content.return_value = [b"image_data"]
    
    @patch('app.services.image_processor.os.makedirs')
    def test_init(self, mock_makedirs):
        """Test that the image processor is initialized correctly."""
        
        # Create an instance of the processor to trigger the initialization
        processor = ImageProcessor()
        
        # Check that the data directory was created
        mock_makedirs.assert_called_once()
    
    @patch('app.services.image_processor.os.makedirs')
    @patch('app.services.image_processor.uuid.uuid4')
    @patch('app.services.image_processor.open', new_callable=mock_open)
    @patch('app.services.image_processor.is_valid_image')
    @patch('app.services.image_processor.normalize_image')
    @patch('app.services.image_processor.get_image_info')
    def test_process_uploaded_image_success(self, mock_get_info, mock_normalize, mock_is_valid, mock_open, mock_uuid, mock_makedirs):
        """Test that the image processor correctly processes an uploaded image."""
        # Set up the mocks
        mock_uuid.return_value = "79d754a275386650e7e71d67f3cde5f2"
        mock_is_valid.return_value = True
        mock_normalize.return_value = True
        mock_get_info.return_value = {"width": 100, "height": 100}
        
        # Create the image processor
        processor = ImageProcessor()
        
        # Process an uploaded image
        image_path, success = processor.process_uploaded_image(self.mock_file)
        
        # Check that the image was processed correctly
        assert success is True
        assert "79d754a275386650e7e71d67f3cde5f2" in image_path
        mock_open.assert_called_once()
        mock_is_valid.assert_called_once()
        mock_normalize.assert_called_once()
    
    @patch('app.services.image_processor.os.makedirs')
    @patch('app.services.image_processor.uuid.uuid4')
    @patch('app.services.image_processor.open', new_callable=mock_open)
    @patch('app.services.image_processor.is_valid_image')
    @patch('app.services.image_processor.os.remove')
    def test_process_uploaded_image_invalid(self, mock_remove, mock_is_valid, mock_open, mock_uuid, mock_makedirs):
        """Test that the image processor correctly handles an invalid uploaded image."""
        # Set up the mocks
        mock_uuid.return_value = "79d754a275386650e7e71d67f3cde5f2"
        mock_is_valid.return_value = False
        
        # Create the image processor
        processor = ImageProcessor()
        
        # Process an invalid uploaded image
        image_path, success = processor.process_uploaded_image(self.mock_file)
        
        # Check that the image was processed correctly
        assert success is False
        assert image_path == ""
        mock_open.assert_called_once()
        mock_is_valid.assert_called_once()
        mock_remove.assert_called_once()
    
    @patch('app.services.image_processor.os.makedirs')
    @patch('app.services.image_processor.uuid.uuid4')
    @patch('app.services.image_processor.requests.get')
    @patch('app.services.image_processor.open', new_callable=mock_open)
    @patch('app.services.image_processor.is_valid_image')
    @patch('app.services.image_processor.normalize_image')
    @patch('app.services.image_processor.get_image_info')
    def test_process_image_url_success(self, mock_get_info, mock_normalize, mock_is_valid, mock_open, mock_get, mock_uuid, mock_makedirs):
        """Test that the image processor correctly processes an image URL."""
        # Set up the mocks
        mock_uuid.return_value = "79d754a275386650e7e71d67f3cde5f2"
        mock_get.return_value = self.mock_response
        mock_is_valid.return_value = True
        mock_normalize.return_value = True
        mock_get_info.return_value = {"width": 100, "height": 100}
        
        # Create the image processor
        processor = ImageProcessor()
        
        # Process an image URL
        image_path, success = processor.process_image_url("https://brandsafety-crawler.s3.amazonaws.com/screenshots/79d754a275386650e7e71d67f3cde5f2.png")
        
        # Check that the image was processed correctly
        assert success is True
        assert "79d754a275386650e7e71d67f3cde5f2" in image_path
        mock_get.assert_called_once()
        mock_open.assert_called_once()
        mock_is_valid.assert_called_once()
        mock_normalize.assert_called_once()
    
    @patch('app.services.image_processor.os.makedirs')
    @patch('app.services.image_processor.requests.get')
    def test_process_image_url_download_error(self, mock_get, mock_makedirs):
        """Test that the image processor correctly handles a download error."""
        # Set up the mocks
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Create the image processor
        processor = ImageProcessor()
        
        # Process an image URL with a download error
        image_path, success = processor.process_image_url("https://brandsafety-crawler.s3.amazonaws.com/screenshots/79d754a275386650e7e71d67f3cde5f2.png")
        
        # Check that the error was handled correctly
        assert success is False
        assert image_path == ""
        mock_get.assert_called_once()