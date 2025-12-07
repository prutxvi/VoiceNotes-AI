# VoiceNotes AI

Lightweight Streamlit app to record audio and produce study materials (summary, key points, flashcards) using Groq's Whisper and Llama models.

**Quick overview**
- **App entry:** `app.py`
- **Purpose:** Record audio, transcribe with Groq Whisper, then generate structured study notes with Llama.

**Prerequisites**
- Python 3.10+ recommended
- A Groq API key (set in `.env` as `GROQ_API_KEY`)

**Setup (PowerShell)**
```powershell
python -m venv .venv
; .\.venv\Scripts\Activate.ps1
; python -m pip install --upgrade pip
; pip install -r requirements.txt
```

Create a `.env` file (or copy `.env.example`) and set your Groq API key:
```text
GROQ_API_KEY=your_api_key_here
```

**Run**
```powershell
streamlit run app.py
```

**Files added to help GitHub**
- `.gitignore` — ignore envs, caches, and sensitive files
- `requirements.txt` — Python dependencies
- `.env.example` — example environment variables
- `LICENSE` — MIT license (update author name)
- `tests/` — a tiny smoke test to validate repository
- `.github/workflows/ci.yml` — CI to run tests on push/PR

Notes
- Before pushing, review `requirements.txt` and pin versions if you need reproducible builds.
- Update `LICENSE` with your name and the year if needed.
