"""
Utility functions for card detection and processing.
"""
from PIL import Image
from io import BytesIO
import base64
import cv2
import streamlit as st
import requests
from inference_sdk import InferenceHTTPClient
from src import config


@st.cache_resource
def get_client():
    """Get cached Roboflow inference client."""
    try:
        api_key = st.secrets["ROBOFLOW_API_KEY"]
    except KeyError:
        st.error("""
        ⚠️ **API Key Missing!**
        
        Please add your Roboflow API key to Streamlit Cloud secrets:
        
        1. Go to your app dashboard on Streamlit Cloud
        2. Click **Settings** (⚙️ icon)
        3. Go to **Secrets** tab
        4. Add the following:
        
        ```toml
        ROBOFLOW_API_KEY = "your-api-key-here"
        ```
        
        5. Click **Save** and the app will redeploy
        """)
        st.stop()
    
    return InferenceHTTPClient(
        api_url=config.API_URL,
        api_key=api_key
    )


def detect_cards(image, client):
    """
    Detect playing cards in an image using Roboflow API.
    
    Args:
        image: PIL Image object
        client: InferenceHTTPClient instance
        
    Returns:
        dict: API response with predictions
    """
    try:
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save image to bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=95)
        img_bytes = img_byte_arr.getvalue()
        
        # Get API key from secrets
        api_key = st.secrets["ROBOFLOW_API_KEY"]
        
        # Parse model_id (format: "workspace/project/version")
        # MODEL_ID is "playing-cards-ow27d/4"
        # Roboflow format: workspace/project/version
        model_parts = config.MODEL_ID.split('/')
        if len(model_parts) == 2:
            # Split workspace/project from version
            workspace_project = model_parts[0]  # "playing-cards-ow27d"
            version = model_parts[1]  # "4"
        else:
            # Fallback if format is different
            workspace_project = config.MODEL_ID
            version = "1"
        
        # Roboflow serverless inference endpoint format
        # Try different endpoint formats
        # Format 1: https://serverless.roboflow.com/{workspace}/{project}/{version}
        # Format 2: https://serverless.roboflow.com/infer/{model_id}
        # Let's try the model_id format first as it's more standard
        url = f"{config.API_URL}/infer/{config.MODEL_ID}"
        
        files = {
            'file': ('image.jpg', img_bytes, 'image/jpeg')
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        params = {
            'api_key': api_key
        }
        
        response = requests.post(url, files=files, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Debug: Log the response structure (only in development)
        # st.write("API Response:", result)  # Uncomment for debugging
        
        # Ensure result has predictions key
        if 'predictions' not in result:
            # Roboflow might return data in different format
            if 'results' in result:
                result['predictions'] = result['results']
            elif isinstance(result, list):
                result = {'predictions': result}
            elif 'detections' in result:
                result['predictions'] = result['detections']
        
        return result
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error detecting cards (HTTP): {str(e)}")
        # Try SDK method as fallback
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            result = client.infer(image, model_id=config.MODEL_ID)
            return result
        except Exception as e2:
            st.error(f"SDK fallback also failed: {str(e2)}")
            return {'predictions': []}
    except Exception as e:
        st.error(f"Error detecting cards: {str(e)}")
        return {'predictions': []}


def get_full_card_name(card_name):
    """
    Convert card code (e.g., 'AH') to full name (e.g., '♥️ Ace of Hearts').
    
    Args:
        card_name: Card code string (e.g., 'AH', 'KS', '10D')
        
    Returns:
        str: Full card name with emoji
    """
    if len(card_name) >= 2:
        suit_char = card_name[-1].upper()
        rank_part = card_name[:-1]
        if suit_char in config.SUITS and rank_part in config.RANKS:
            suit_name, emoji = config.SUITS[suit_char]
            return f"{emoji} {config.RANKS[rank_part]} of {suit_name}"
    return f"🃏 {card_name}"


def filter_duplicates(predictions):
    """
    Filter duplicate card detections based on confidence and spatial proximity.
    
    Args:
        predictions: List of prediction dictionaries from API
        
    Returns:
        list: Filtered predictions without duplicates
    """
    if not predictions:
        return []
    
    # Filter by confidence threshold
    predictions = [p for p in predictions if p['confidence'] >= config.CONFIDENCE_THRESHOLD]

    # Group by class, but keep spatially distinct cards
    result = []
    for pred in sorted(predictions, key=lambda x: x['confidence'], reverse=True):
        # Check if this is a duplicate of an already added card (same class, close position)
        is_duplicate = False
        for existing in result:
            if existing['class'] == pred['class']:
                # Calculate distance between centers
                dist = ((pred['x'] - existing['x'])**2 + (pred['y'] - existing['y'])**2)**0.5
                # If centers are within threshold pixels, consider it the same physical card
                if dist < config.DUPLICATE_DISTANCE_THRESHOLD:
                    is_duplicate = True
                    break
        if not is_duplicate:
            result.append(pred)
    return result


def draw_boxes_cv(frame, predictions):
    """
    Draw bounding boxes and labels on frame for detected cards.
    
    Args:
        frame: OpenCV frame (numpy array)
        predictions: List of prediction dictionaries
        
    Returns:
        numpy array: Frame with drawn bounding boxes and labels
    """
    for pred in predictions:
        x, y = int(pred['x']), int(pred['y'])
        w, h = int(pred['width']), int(pred['height'])
        left, top = x - w // 2, y - h // 2
        right, bottom = x + w // 2, y + h // 2

        color = (0, 255, 0)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 3)

        card_name = pred['class']
        if len(card_name) >= 2 and card_name[-1] in config.SUITS:
            rank_name = config.RANKS.get(card_name[:-1], card_name[:-1])
            full_name = f"{rank_name} of {config.SUITS[card_name[-1]][0]}"
        else:
            full_name = card_name

        label = f"{full_name} ({pred['confidence']:.0%})"
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

