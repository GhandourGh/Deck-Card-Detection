import streamlit as st
from PIL import Image
import av
import threading
import time
from pathlib import Path
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from src import config
from src import utils

# Load CSS from external file
def load_css():
    """Load CSS styles from external file."""
    css_path = Path(__file__).parent / 'src' / 'static' / 'styles.css'
    with open(css_path, 'r') as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.INITIAL_SIDEBAR_STATE
)

# Load CSS
load_css()

# Initialize client
CLIENT = utils.get_client()

class CardDetector(VideoProcessorBase):
    def __init__(self):
        self.last_predictions = []
        self.lock = threading.Lock()
        self.detection_running = False

    def get_predictions(self):
        with self.lock:
            return self.last_predictions.copy()

    def _run_detection(self, img):
        try:
            # Convert BGR (OpenCV) to RGB (PIL) by reversing color channels
            pil_image = Image.fromarray(img[:, :, ::-1])
            result = utils.detect_cards(pil_image, CLIENT)
            if 'predictions' in result:
                with self.lock:
                    self.last_predictions = utils.filter_duplicates(result['predictions'])
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            # Log specific errors for debugging
            pass
        except Exception as e:
            # Catch any other unexpected errors
            pass
        finally:
            self.detection_running = False

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        if not self.detection_running:
            self.detection_running = True
            threading.Thread(target=self._run_detection, args=(img.copy(),), daemon=True).start()

        with self.lock:
            predictions = self.last_predictions.copy()

        if predictions:
            img = utils.draw_boxes_cv(img, predictions)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Initialize session state
if 'card_history' not in st.session_state:
    st.session_state.card_history = {}  # {card_name: {"count": int, "confidence": float}}

# Navbar
st.markdown("""
<div class="navbar">
    <div>
        <span class="navbar-brand">♠️ CardScan</span>
        <span class="navbar-subtitle">Real-time playing card detection</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([2, 1], gap="small")

with col1:
    ctx = webrtc_streamer(
        key="card-detection",
        video_processor_factory=CardDetector,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

with col2:
    total_cards = sum(data["count"] for data in st.session_state.card_history.values()) if st.session_state.card_history else 0
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Cards Detected</div>
        <div class="stat-value">{total_cards}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Reset Session", use_container_width=True):
        st.session_state.card_history = {}
        st.rerun()
    st.markdown('<div class="section-title">Detected Cards</div>', unsafe_allow_html=True)

    if st.session_state.card_history:
        for card_name, data in sorted(st.session_state.card_history.items()):
            suit_char = card_name[-1].upper() if len(card_name) >= 2 else ''
            suit_map = {'H': 'hearts', 'D': 'diamonds', 'S': 'spades', 'C': 'clubs'}
            suit_class = suit_map.get(suit_char, 'clubs')
            count_display = f" x{data['count']}" if data['count'] > 1 else ""
            st.markdown(f"""
            <div class="card-item {suit_class}">
                <span class="card-name">{utils.get_full_card_name(card_name)}{count_display}</span>
                <span class="card-confidence">{data['confidence']:.0%}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">♠️</div>
            <div>No cards detected yet</div>
        </div>
        """, unsafe_allow_html=True)

# Update loop - continuously check for new card detections
if ctx.state.playing and ctx.video_processor:
    while ctx.state.playing and ctx.video_processor:
        try:
            predictions = ctx.video_processor.get_predictions()
        except AttributeError:
            break

        changed = False
        # Count how many of each card type are in current frame
        current_counts = {}
        for pred in predictions:
            card_name = pred['class']
            confidence = pred['confidence']
            if card_name not in current_counts:
                current_counts[card_name] = {"count": 0, "confidence": confidence}
            current_counts[card_name]["count"] += 1
            current_counts[card_name]["confidence"] = max(current_counts[card_name]["confidence"], confidence)

        # Update history if we see more cards of a type than before
        for card_name, data in current_counts.items():
            if card_name not in st.session_state.card_history:
                st.session_state.card_history[card_name] = data
                changed = True
            else:
                # Update count if we see more cards
                if data["count"] > st.session_state.card_history[card_name]["count"]:
                    st.session_state.card_history[card_name]["count"] = data["count"]
                    changed = True
            

        if changed:
            st.rerun()
        time.sleep(config.DETECTION_UPDATE_INTERVAL)

# Footer
st.markdown('<div class="footer">Built by <a href="https://github.com/GhandourGh">GhandourGh</a></div>', unsafe_allow_html=True)
