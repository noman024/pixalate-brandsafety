import json
import csv
import requests
import streamlit as st
from PIL import Image
import io
import os
import sys
from io import StringIO
from loguru import logger

# Add the project root to the Python path to make app imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from app
from app.core.logging import setup_logging

# Set up logging using the centralized logging configuration
setup_logging()

# Set page config
st.set_page_config(
    page_title="Brand Safety Analysis",
    page_icon="🛡️",
    layout="wide",
)

# API endpoints
API_URL = "http://localhost:8000/api/v1"

def main():
    """
    Main function for the Streamlit UI.
    
    This function sets up the Streamlit UI with tabs for image upload and URL input,
    and displays the classification results.
    """
    # Title and description
    st.title("Brand Safety Analysis System")
    st.markdown(
        """
        This system analyzes images for brand safety concerns based on IAB and GARM frameworks.
        Upload an image or provide an image URL to get started.
        """
    )
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["Upload Image", "Image URL"])
    
    # Tab 1: Upload Image
    with tab1:
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
        
        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Classify the image when the button is clicked
            if st.button("Analyze Image", key="analyze_upload"):
                with st.spinner("Analyzing image..."):
                    try:
                        # Prepare the file for upload
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
                        
                        # Call the API
                        response = requests.post(f"{API_URL}/classify", files=files)
                        
                        # Display the results
                        if response.status_code == 200:
                            display_results(response.json(), uploaded_file.name)
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # Tab 2: Image URL
    with tab2:
        image_url = st.text_input("Enter Image URL")
        
        if image_url:
            try:
                # Display the image from URL
                response = requests.get(image_url)
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption="Image from URL", use_column_width=True)
                
                # Extract filename from URL
                url_filename = os.path.basename(image_url)
                
                # Classify the image when the button is clicked
                if st.button("Analyze Image", key="analyze_url"):
                    with st.spinner("Analyzing image..."):
                        try:
                            # Call the API
                            response = requests.post(
                                f"{API_URL}/classify-url",
                                json={"url": image_url}
                            )
                            
                            # Display the results
                            if response.status_code == 200:
                                display_results(response.json(), url_filename)
                            else:
                                st.error(f"Error: {response.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")

def display_results(response, filename):
    """
    Display the classification results.
    
    This function displays the classification results in a user-friendly format,
    with color-coded ratings and expandable explanations.
    
    Args:
        response: API response containing classification results
        filename: Original filename of the image
    """
    # Check if the response is successful
    if not response.get("success", False):
        st.error(f"Error: {response.get('error', {}).get('message', 'Unknown error')}")
        return
    
    # Get the results
    results = response.get("data", {})
    
    st.subheader("Brand Safety Analysis Results")
    
    # Create columns for categories
    col1, col2 = st.columns(2)
    
    # Display results in a structured format
    categories = [
        ("Adult Content", "adultContentRating"),
        ("Drugs Content", "drugsContentRating"),
        ("Alcohol Content", "alcoholContentRating"),
        ("Hate Speech", "hateSpeechRating"),
        ("Arms and Ammunition", "armsAndAmmunitionRating"),
        ("Death, Injury, or Military Conflict", "deathInjuryOrMilitaryConflictRating"),
        ("Terrorism", "terrorismRating"),
        ("Obscenity and Profanity", "obscenityAndProfanityRating"),
    ]
    
    # Display categories in two columns
    for i, (display_name, key) in enumerate(categories):
        col = col1 if i < 4 else col2
        
        with col:
            st.markdown(f"### {display_name}")
            
            # Get values with fallbacks
            rating = results.get(f"{key}", "N/A")
            confidence = results.get(f"{key}_confidence_score", "N/A")
            explanation = results.get(f"{key}_explanation", "No explanation provided")
            
            # Display rating with color
            if rating == "low":
                st.success(f"Rating: {rating.upper()}")
            elif rating == "medium":
                st.warning(f"Rating: {rating.upper()}")
            elif rating == "high":
                st.error(f"Rating: {rating.upper()}")
            else:
                st.info(f"Rating: {rating}")
            
            st.markdown(f"**Confidence:** {confidence}")
            
            # Create expandable section for explanation
            with st.expander("Explanation"):
                st.markdown(explanation)
            
            st.markdown("---")
    
    # Generate dynamic filename based on the input image
    base_filename = os.path.splitext(filename)[0]
    json_filename = f"{base_filename}_results.json"
    csv_filename = f"{base_filename}_results.csv"
    
    # Create download buttons container
    download_col1, download_col2 = st.columns(2)
    
    # Add download button for JSON results
    with download_col1:
        st.download_button(
            label="Download Results (JSON)",
            data=json.dumps(results, indent=2),
            file_name=json_filename,
            mime="application/json",
        )
    
    # Convert results to CSV format
    csv_data = convert_to_csv(results)
    
    # Add download button for CSV results
    with download_col2:
        st.download_button(
            label="Download Results (CSV)",
            data=csv_data,
            file_name=csv_filename,
            mime="text/csv",
        )

def convert_to_csv(results):
    """
    Convert results to CSV format.
    
    Args:
        results: Classification results
        
    Returns:
        CSV data as string
    """
    # Create a list to hold the rows
    rows = []
    
    # Add header row
    rows.append(["Category", "Rating", "Confidence Score", "Explanation"])
    
    # Map of key prefixes to display names
    category_map = {
        "adultContent": "Adult Content",
        "drugsContent": "Drugs Content",
        "alcoholContent": "Alcohol Content",
        "hateSpeech": "Hate Speech",
        "armsAndAmmunition": "Arms and Ammunition",
        "deathInjuryOrMilitaryConflict": "Death, Injury, or Military Conflict",
        "terrorism": "Terrorism",
        "obscenityAndProfanity": "Obscenity and Profanity"
    }
    
    # Add data rows
    for key_prefix, display_name in category_map.items():
        rating_key = f"{key_prefix}Rating"
        confidence_key = f"{rating_key}_confidence_score"
        explanation_key = f"{rating_key}_explanation"
        
        if rating_key in results:
            rows.append([
                display_name,
                results.get(rating_key, "N/A"),
                results.get(confidence_key, "N/A"),
                results.get(explanation_key, "No explanation provided")
            ])
    
    # Convert to CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    
    return output.getvalue()

if __name__ == "__main__":
    logger.info("[STREAMLIT] Starting Brand Safety Analysis Streamlit UI")
    main()