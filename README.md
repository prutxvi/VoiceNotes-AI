# VoiceNotes AI

Transform your voice into smart study notes instantly! A lightweight Streamlit app that records audio lectures, transcribes them with Groq's Whisper AI, and generates structured study materials using Llama 3.3.

## ✨ Features

- **🎙️ Live Audio Recording** — Built-in mic recorder for seamless audio capture
- **🔊 Fast Transcription** — Groq Whisper-large-v3 for accurate, lightning-fast audio-to-text conversion
- **📝 Smart Summaries** — AI-powered 3-sentence summaries of your lectures
- **🔑 Key Concepts** — Automatically extracts 5 important bullet points
- **🃏 Flashcards** — Generates 5 interactive study flashcards (question ↔ answer pairs)
- **📊 JSON Output** — Structured data for easy integration with other tools
- **⚡ Real-time UI** — Tabbed interface with summary, flashcards, and transcript views
- **🔐 Secure** — API key stored locally in `.env`, never exposed

## Quick Overview

- **App entry:** `app.py`
- **Tech Stack:** Streamlit (UI), Groq API (Whisper + Llama 3.3), Python 3.10+
- **Use case:** Students, researchers, professionals who want instant study notes from lectures

## Prerequisites

- Python 3.10 or higher
- A Groq API key (free tier available at [console.groq.com](https://console.groq.com))
- ~500MB free disk space for dependencies

## Installation & Setup

### 1. Clone the Repository
```powershell
git clone https://github.com/prutxvi/VoiceNotes-AI.git
cd "VoiceNotes-AI"
```

### 2. Create Virtual Environment (Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file (or copy from `.env.example`):
```text
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key: https://console.groq.com/keys

## 🚀 Running the App

```powershell
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Quick Steps in the App
1. Click **"⏺️ Start Recording"** to begin recording
2. Click **"⏹️ Stop Recording"** when done
3. Click **"⚡ Transcribe & Generate"** to process
4. Review your **Summary**, **Flashcards**, and **Transcript** in the tabs

## Project Structure

```
VoiceNotes-AI/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variable template
├── LICENSE                  # MIT License
├── README.md               # This file
├── CONTRIBUTING.md         # Contribution guidelines
├── CODE_OF_CONDUCT.md      # Code of conduct
├── .gitignore              # Git ignore rules
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
└── tests/
    └── test_app_file.py    # Basic smoke tests
```

## 📋 Requirements

All dependencies are in `requirements.txt`:

- **streamlit** — Web UI framework
- **groq** — API client for Groq (Whisper + Llama)
- **python-dotenv** — Environment variable management
- **streamlit-mic-recorder** — Audio input widget
- **pytest** — Testing framework

## 🔧 Configuration

### API Keys & Secrets

**Never commit `.env` files!** The `.gitignore` already excludes them.

- Get a free Groq API key: https://console.groq.com/keys
- Store in `.env` — it's automatically loaded by the app

### Models Used

- **Whisper Large V3** — Fast, accurate transcription
- **Llama 3.3 70B Versatile** — Study note generation & flashcards

## 📝 Usage Examples

### Example 1: Lecture Recording
Record a 5-minute lecture on photosynthesis → Get:
- 3-sentence summary
- 5 key concepts
- 5 flashcards for review

### Example 2: Interview Notes
Record a 10-minute interview → Organize into:
- Summary of main topics
- Bullet points for reference
- Question-answer pairs for later

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick steps:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m "feat: add new feature"`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Groq API](https://groq.com/) (Whisper + Llama)
- Community contributions welcome!

## 📞 Support & Feedback

Found a bug? Have a feature request? Open an [issue](https://github.com/prutxvi/VoiceNotes-AI/issues).

---

**Happy note-taking! 🎓**
