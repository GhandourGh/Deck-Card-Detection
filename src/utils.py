"""
Utility functions for card detection and processing.
"""
from PIL import Image
from io import BytesIO
import base64
import cv2
import streamlit as st
from inference_sdk import InferenceHTTPClient
from src import config


@st.cache_resource
def get_client():
    """Get cached Roboflow inference client."""
    return InferenceHTTPClient(
        api_url=config.API_URL,
        api_key=st.secrets["ROBOFLOW_API_KEY"]
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
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        return client.infer(img_base64, model_id=config.MODEL_ID)
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

