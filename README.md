# Brand Safety Analysis System

A system for classifying images into brand safety categories based on IAB and GARM frameworks using OpenAI's Vision model.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Technical Approaches](#technical-approaches)
- [Logging](#logging)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)

## Overview

The Brand Safety Analysis System is designed to help digital advertisers ensure their ads don't appear alongside inappropriate content. The system analyzes images for brand safety concerns, providing classifications across multiple categories:

- Adult Content
- Arms and Ammunition
- Death, Injury, or Military Conflict
- Hate Speech
- Obscenity and Profanity
- Drugs Content
- Alcohol Content
- Terrorism

For each category, the system provides:
- A rating (low/medium/high)
- A confidence score (0%-99%)
- An explanation for the classification

## Features

- Image classification into brand safety categories
- Confidence scores for classifications
- Explanations for classifications
- Support for both uploaded images and image URLs
- Streamlit UI for easy interaction
- FastAPI endpoints for programmatic access
- Comprehensive logging system
- Robust error handling

## Technical Architecture

The system follows a layered architecture:

```
┌─────────────┐
│    UI Layer │ Streamlit Interface
└──────┬──────┘
       │
┌──────▼──────┐
│   API Layer │ FastAPI Endpoints
└──────┬──────┘
       │
┌──────▼──────┐
│Service Layer│ Image Processing & Classification
└──────┬──────┘
       │
┌──────▼──────┐
│ Model Layer │ OpenAI Vision Model
└─────────────┘
```

## Project Structure

```
pixalate-brandsafety/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── setup_env.sh
├── data/                        # Directory for storing uploaded images
├── logs/                        # Directory for log files
│   ├── app.log                  # Centralized log file
│   └── error.log                # Error log file
├── app/
│   ├── main.py                  # Main Streamlit application
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   ├── endpoints/
│   │   │   ├── classification.py # Classification endpoints
│   │   │   └── health.py        # Health check endpoints
│   ├── core/
│   │   ├── config.py            # Configuration settings
│   │   └── logging.py           # Logging configuration
│   ├── models/
│   │   ├── base.py              # Base model interface
│   │   └── openai_model.py      # OpenAI model implementation
│   ├── services/
│   │   ├── image_processor.py   # Image preprocessing
│   │   └── classification.py    # Classification logic
│   └── utils/
│       ├── image_utils.py       # Image utility functions
│       └── api_utils.py         # API utility functions
└── tests/
    ├── test_models/
    │   └── test_openai_model.py
    ├── test_services/
    │   └── test_image_processor.py
    └── test_api/
        └── test_endpoints.py
```

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pixalate-brandsafety
   ```

2. Set up the virtual environment and install dependencies:
   ```bash
   # Run the setup script
   bash setup_env.sh
   
   # Activate the virtual environment
   source venv/bin/activate
   ```

3. Create a `.env` file based on `.env.example` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Running the Application

#### Option 1: Using the run.sh script (Recommended)

The project includes a run.sh script that starts both the FastAPI server and Streamlit UI in a split terminal view using tmux:

```bash
# Make the script executable (if not already)
chmod +x run.sh

# Run both the API and UI with a single command
./run.sh
```

This script:
- Checks for and kills any existing processes using ports 8000 and 8501
- Checks for and handles existing tmux sessions with the same name
- Uses tmux to create a split terminal view
- Runs the FastAPI server in the left pane
- Runs the Streamlit UI in the right pane in headless mode (no automatic browser opening)
- Uses environment variables to prevent automatic reloading
- Properly handles shutdown of both services when the tmux session is closed

Prerequisites:
- tmux must be installed (`sudo apt-get install tmux`)

#### Option 2: Starting services separately

1. Start the FastAPI server:
   ```bash
   # Activate the virtual environment if not already activated
   source venv/bin/activate
   
   # Run the FastAPI server
   uvicorn app.api.main:app --reload
   ```

2. Start the Streamlit UI (in a separate terminal):
   ```bash
   # Activate the virtual environment
   source venv/bin/activate
   
   # Run the Streamlit UI
   streamlit run app/main.py
   ```

3. Access the applications:
   - Streamlit UI: http://localhost:8501
   - FastAPI documentation: http://localhost:8000/docs

### Using the Streamlit UI

1. Open http://localhost:8501 in your browser
2. Choose between uploading an image or providing an image URL
3. Click "Analyze Image" to see the brand safety classification results
4. View the results with color-coded ratings and detailed explanations
5. Download the results as JSON if needed

### Using the API

#### Classify an Uploaded Image

```bash
curl -X POST "http://localhost:8000/api/v1/classify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

#### Classify an Image URL

```bash
curl -X POST "http://localhost:8000/api/v1/classify-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}'
```

### Testing with Postman

1. **Setup Postman**:
   - Download and install [Postman](https://www.postman.com/downloads/)
   - Create a new collection for Brand Safety Analysis

2. **Testing Image Upload Endpoint**:
   - Create a new POST request to `http://localhost:8000/api/v1/classify`
   - Go to the "Body" tab
   - Select "form-data"
   - Add a key named "file" and change the type to "File"
   - Click "Select Files" and choose an image to upload
   - Click "Send" to make the request

3. **Testing Image URL Endpoint**:
   - Create a new POST request to `http://localhost:8000/api/v1/classify-url`
   - Go to the "Body" tab
   - Select "raw" and choose "JSON" from the dropdown
   - Enter the following JSON:
     ```json
     {
       "url": "https://example.com/path/to/image.jpg"
     }
     ```
   - Click "Send" to make the request

4. **Viewing Results**:
   - The response will be displayed in the "Response" section
   - You can save the response or export it for further analysis

## API Documentation

### Endpoints

#### Health Check

- **URL**: `/api/v1/health`
- **Method**: GET
- **Description**: Check the health status of the API
- **Response**: Status information including system metrics

#### Classify Image

- **URL**: `/api/v1/classify`
- **Method**: POST
- **Description**: Classify an uploaded image
- **Request Body**: Multipart form with a file field
- **Response**: Classification results for all brand safety categories

#### Classify Image URL

- **URL**: `/api/v1/classify-url`
- **Method**: POST
- **Description**: Classify an image from a URL
- **Request Body**: JSON with a url field
- **Response**: Classification results for all brand safety categories

### Response Format

```json
{
    "success": true,
    "data": {
        "image_path": "<uploaded_image_path_saved_in_local/image_url>",
        "adultContentRating": "<low/medium/high>",
        "adultContentRating_confidence_score": "<0%-99%>",
        "adultContentRating_explanation": "<explanation>",
        "drugsContentRating": "<low/medium/high>",
        "drugsContentRating_confidence_score": "<0%-99%>",
        "drugsContentRating_explanation": "<explanation>",
        "alcoholContentRating": "<low/medium/high>",
        "alcoholContentRating_confidence_score": "<0%-99%>",
        "alcoholContentRating_explanation": "<explanation>",
        "hateSpeechRating": "<low/medium/high>",
        "hateSpeechRating_confidence_score": "<0%-99%>",
        "hateSpeechRating_explanation": "<explanation>",
        "armsAndAmmunitionRating": "<low/medium/high>",
        "armsAndAmmunitionRating_confidence_score": "<0%-99%>",
        "armsAndAmmunitionRating_explanation": "<explanation>",
        "deathInjuryOrMilitaryConflictRating": "<low/medium/high>",
        "deathInjuryOrMilitaryConflictRating_confidence_score": "<0%-99%>",
        "deathInjuryOrMilitaryConflictRating_explanation": "<explanation>",
        "terrorismRating": "<low/medium/high>",
        "terrorismRating_confidence_score": "<0%-99%>",
        "terrorismRating_explanation": "<explanation>",
        "obscenityAndProfanityRating": "<low/medium/high>",
        "obscenityAndProfanityRating_confidence_score": "<0%-99%>",
        "obscenityAndProfanityRating_explanation": "<explanation>"
    }
}
```

## Technical Approaches

The project implements the Single Model Approach (Approach 1) as described in the project brief:

### Single Model Approach

- Uses a single vision model (OpenAI's GPT-4o) for all image classifications
- Simple implementation with consistent results
- Lower development complexity
- No fallback mechanism (single point of failure)

The implementation includes:

1. **Prompt Engineering**: Carefully crafted prompts for the OpenAI model to ensure accurate and structured responses
2. **Image Processing**: Validation, normalization, and optimization of images before classification
3. **Structured Response Parsing**: Extraction and formatting of classification results from the model's response
4. **Error Handling**: Robust error handling throughout the application
5. **Logging**: Comprehensive logging system for monitoring and debugging

## Logging

The system uses a centralized logging approach:

- **Console Logs**: Real-time logs with color-coding for different log levels
- **App Log**: Centralized log file (`logs/app.log`) containing all log entries
- **Error Log**: Separate log file (`logs/error.log`) for error messages only

Log features:
- Rotation when files reach 10 MB
- Compression as zip files
- 30-day retention policy
- Consistent formatting with timestamps, log levels, and messages
- Layer-specific prefixes for clear source identification:
  - `[API]`: Logs from the API layer
  - `[SERVICE]`: Logs from the service layer
  - `[IMAGE_PROCESSOR]`: Logs from the image processor
  - `[STREAMLIT]`: Logs from the Streamlit UI
  - `[LOGGING]`: Logs from the logging system itself

The logging system is designed to prevent duplicate log entries and ensure proper log propagation across different components of the application.

## Testing

The project includes comprehensive tests for all components:

- **Model Tests**: Tests for the OpenAI model integration
- **Service Tests**: Tests for image processing and classification services
- **API Tests**: Tests for the FastAPI endpoints

To run the tests:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run specific test files
pytest tests/test_models/test_openai_model.py
pytest tests/test_services/test_image_processor.py
pytest tests/test_api/test_endpoints.py
```

## Future Enhancements

Potential future enhancements include:

1. **Sequential Multi-Model Approach (Approach 2)**:
   - Implement fallback mechanisms with multiple vision models
   - Start with OpenAI and fall back to alternatives if needed
   - Improve reliability and robustness

2. **Performance Optimizations**:
   - Implement caching for frequently classified images
   - Add batch processing capabilities
   - Optimize image preprocessing

3. **Additional Features**:
   - User authentication and authorization
   - Result history and analytics
   - Custom classification thresholds
   - Batch upload and processing