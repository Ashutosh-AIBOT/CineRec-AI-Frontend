# 🎬 CineRec AI: Premium Movie Companion

CineRec is a state-of-the-art movie discovery application that combines a **premium dark-cinema UI** with powerful **Groq-powered AI interaction**. It offers a personalized experience through mood tracking, AI chatbots ("Buddy"), and advanced recommendation algorithms.

## ✨ Features
- **Buddy AI Agent**: Your persistent movie companion that helps you find films by vibe.
- **Mood-Based Exploration**: Navigate movies through emotional states (Action, Romantic, Horror, etc.).
- **Interactive "Small Buddy"**: A contextual mini-sidebar that appears during movie details to give you instant "Vibe Checks".
- **Glassmorphic Design**: A modern, high-contrast Dark Mode interface inspired by professional cinematography tools.
- **Real-time Chat**: Powered by Groq Llama 3.1 for lightning-fast, free AI responses.

## 🛠️ Tech Stack
- **UI Framework**: Streamlit
- **AI Gateway**: Groq API
- **Networking**: Requests
- **Design**: Vanilla CSS & HTML5

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CineRec-AI-Frontend.git
   cd CineRec-AI-Frontend
   ```

2. **Setup virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add API Keys**:
   Create a `.streamlit/secrets.toml` file:
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   API_BASE = "https://your-backend-url.render.com"
   ```

5. **Run Locally**:
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment

### Streamlit Community Cloud (Recommended)
1. Push this folder to GitHub.
2. Connect your repo to [Streamlit Cloud](https://streamlit.io/cloud).
3. Add your `GROQ_API_KEY` and `API_BASE` in the **Advanced Settings > Secrets** section.

### Render / Docker
1. The repository includes a `Dockerfile` pre-configured for deployment as a Web Service on Render.
2. Expose port `8501`.

---
*Powered by CineRec AI Engine & Groq*
