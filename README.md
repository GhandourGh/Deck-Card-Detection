# Deck-Card-Detection 🃏

An AI-powered real-time playing card detection application built with Streamlit. This application uses computer vision to identify and track playing cards from live camera feed or images.

## ✨ Features

- **Real-time Detection**: Live card detection using webcam feed
- **52 Card Support**: Detects all standard playing cards (Ace through King, all suits)
- **Confidence Scores**: Shows detection confidence for each card
- **Visual Feedback**: Bounding boxes and labels on detected cards
- **Card History**: Tracks all detected cards with counts and confidence levels
- **Modern UI**: Beautiful gradient-based interface with smooth animations
- **Duplicate Filtering**: Smart filtering to avoid counting the same card multiple times

## 🚀 Live Demo

[Deploy on Streamlit Cloud](https://share.streamlit.io/) - Coming soon!

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: Roboflow Inference API
- **Computer Vision**: OpenCV, PIL
- **Real-time Processing**: WebRTC, AV
- **Language**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- Roboflow API key ([Get one here](https://roboflow.com/))
- Webcam (for real-time detection)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/GhandourGh/Deck-Card-Detection.git
   cd Deck-Card-Detection
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key**
   - Create `.streamlit/secrets.toml` file
   - Add your Roboflow API key:
   ```toml
   ROBOFLOW_API_KEY = "your-api-key-here"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
Deck-Card-Detection/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore            # Git ignore rules
└── src/                  # Source code
    ├── __init__.py
    ├── config.py         # Configuration settings
    ├── utils.py          # Utility functions
    └── static/
        └── styles.css    # CSS styles
```

## 🎮 How to Use

1. **Start the application**: Run `streamlit run app.py`
2. **Allow camera access**: Grant permission when prompted
3. **Point camera at cards**: Position playing cards in view
4. **View results**: Detected cards appear in the sidebar with confidence scores
5. **Reset session**: Click "Reset Session" to clear detection history

## ⚙️ Configuration

Edit `src/config.py` to customize:
- Confidence threshold (default: 0.5)
- Detection update interval
- Duplicate distance threshold
- Model settings

## 🔒 Security

- API keys are stored in `.streamlit/secrets.toml` (not committed to git)
- All sensitive data is excluded via `.gitignore`
- No hardcoded credentials in source code

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

**GhandourGh**
- GitHub: [@GhandourGh](https://github.com/GhandourGh)

## 🙏 Acknowledgments

- [Roboflow](https://roboflow.com/) for the card detection model
- [Streamlit](https://streamlit.io/) for the amazing framework
- [Streamlit WebRTC](https://github.com/whitphx/streamlit-webrtc) for real-time video processing

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ♠️ by GhandourGh
