import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import json

# 1. Setup & Config
load_dotenv()
st.set_page_config(page_title="VoiceNotes AI", page_icon="🎙️", layout="wide")

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ Groq API Key missing! Check your .env file.")
    st.stop()

client = Groq(api_key=api_key)

# 2. Helper Functions
def transcribe_audio(audio_bytes):
    """Sends audio to Groq's Whisper for fast transcription."""
    try:
        # Groq requires a filename with extension
        transcription = client.audio.transcriptions.create(
            file=("recording.wav", audio_bytes), 
            model="whisper-large-v3", # Active model
            response_format="json",
            language="en"
        )
        return transcription.text
    except Exception as e:
        st.error(f"Transcription Error: {str(e)}")
        return None

def generate_study_material(text):
    """Sends transcript to Llama 3 for processing into JSON."""
    system_prompt = """
    You are an expert study assistant. Analyze the transcript and output a valid JSON object with:
    1. "summary": A concise 3-sentence summary.
    2. "key_points": A list of 5 key bullet points.
    3. "flashcards": A list of 5 objects, each with "front" (question) and "back" (answer).
    Do not add any markdown formatting like ```json. Just return the raw JSON.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # --- ROBUST EXTRACTION & CLEANING ---
        first_choice = completion.choices[0]
        
        # 1. Unwrap List (if applicable)
        if isinstance(first_choice, list):
            first_choice = first_choice[0]
            
        # 2. Extract Content (Object vs Dict)
        if hasattr(first_choice, 'message'):
            content = first_choice.message.content
        elif isinstance(first_choice, dict):
            content = first_choice['message']['content']
        else:
            content = str(first_choice)
            
        # 3. Clean Markdown Wrappers (The Critical Fix)
        # Llama sometimes adds `````` despite instructions. We strip it.
        content = content.replace("``````", "").strip()

        return json.loads(content)
        
    except Exception as e:
        st.error(f"Llama Error: {str(e)}")
        print(f"DEBUG INFO: {completion.choices}") # Debug log
        return None

# 3. The UI Layout
st.title("🎙️ VoiceNotes AI")
st.markdown("Record your lecture. Get **Instant Study Notes**.")

# Session State for storing data between reruns
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "study_data" not in st.session_state:
    st.session_state.study_data = None

# Input Section
col1, col2 = st.columns([1, 2]) # ✅ Fixed: Correct list syntax

with col1:
    st.subheader("1. Record Audio")
    # The Recorder Widget
    audio = mic_recorder(
        start_prompt="⏺️ Start Recording",
        stop_prompt="⏹️ Stop Recording",
        key='recorder',
        format="wav" # Important for Groq
    )
    
    if audio:
        st.audio(audio['bytes'])
        if st.button("⚡ Transcribe & Generate"):
            with st.spinner("🎧 Transcribing..."):
                text = transcribe_audio(audio['bytes'])
                st.session_state.transcript = text
                
            if text:
                with st.spinner("🧠 Generating Notes..."):
                    data = generate_study_material(text)
                    st.session_state.study_data = data
                    
                if st.session_state.study_data:
                    st.success("Done! Check the tabs on the right 👉")

# Output Section
if st.session_state.study_data:
    data = st.session_state.study_data
    
    with col2:
        st.subheader("2. Your Study Material")
        
        tab1, tab2, tab3 = st.tabs(["📝 Smart Notes", "🃏 Flashcards", "📜 Full Transcript"])
        
        with tab1:
            st.info(f"**Summary:** {data.get('summary', 'No summary available')}")
            st.markdown("### 🔑 Key Concepts")
            for point in data.get('key_points', []):
                st.markdown(f"- {point}")
                
        with tab2:
            st.markdown("### Flashcards")
            cards = data.get('flashcards', [])
            cols = st.columns(2)
            for i, card in enumerate(cards):
                with cols[i % 2]:
                    with st.expander(f"❓ {card['front']}"):
                        st.write(f"**💡 {card['back']}**")
                        
        with tab3:
            st.text_area("Raw Transcript", st.session_state.transcript, height=300)
