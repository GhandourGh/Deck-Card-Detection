# Deployment Guide for Streamlit Cloud

## 🚀 Deploying to Streamlit Community Cloud

### Step 1: Push to GitHub
Your code is already set up and ready to push:
```bash
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in the details:
   - **Repository**: `GhandourGh/Deck-Card-Detection`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Deploy"**

### Step 3: Add Your API Key (IMPORTANT!)

1. In your app dashboard, click on **"Settings"** (⚙️ icon)
2. Go to **"Secrets"** tab
3. Add your Roboflow API key:
   ```toml
   ROBOFLOW_API_KEY = "your-api-key-here"
   ```
4. Click **"Save"**
5. Your app will automatically redeploy

### Step 4: Access Your App

Your app will be live at:
```
https://YOUR-APP-NAME.streamlit.app
```

## 🔒 Security Checklist

✅ **Secrets are properly ignored** - `.streamlit/secrets.toml` is in `.gitignore`
✅ **No hardcoded API keys** - All keys use `st.secrets`
✅ **Proper file structure** - All source code organized in `src/` folder

## 📝 Notes

- The app requires camera access for real-time detection
- Make sure your Roboflow API key has sufficient credits
- The app will automatically install dependencies from `requirements.txt`

## 🐛 Troubleshooting

**Issue**: App fails to start
- Check that all dependencies in `requirements.txt` are correct
- Verify your API key is correctly set in Streamlit Cloud secrets

**Issue**: Camera not working
- Ensure HTTPS is enabled (Streamlit Cloud does this automatically)
- Check browser permissions for camera access

**Issue**: No cards detected
- Verify your Roboflow API key is valid
- Check the model ID in `src/config.py` matches your Roboflow model

