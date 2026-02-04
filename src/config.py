"""
Configuration settings for CardScan application.
"""

# API Configuration
MODEL_ID = "playing-cards-ow27d/4"
CONFIDENCE_THRESHOLD = 0.5
API_URL = "https://serverless.roboflow.com"

# Card Data
RANKS = {
    'A': 'Ace', '2': '2', '3': '3', '4': '4', '5': '5', 
    '6': '6', '7': '7', '8': '8', '9': '9', '10': '10', 
    'J': 'Jack', 'Q': 'Queen', 'K': 'King'
}

SUITS = {
    'H': ('Hearts', '♥️'), 
    'D': ('Diamonds', '♦️'), 
    'S': ('Spades', '♠️'), 
    'C': ('Clubs', '♣️')
}

# Detection Settings
DUPLICATE_DISTANCE_THRESHOLD = 250  # pixels
DETECTION_UPDATE_INTERVAL = 0.5  # seconds

# Page Configuration
PAGE_TITLE = "CardScan"
PAGE_ICON = "♠️"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "collapsed"

