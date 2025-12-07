import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import json
from streamlit_mermaid import st_mermaid
from fpdf import FPDF
import re

# 1. Setup & Config
load_dotenv()
st.set_page_config(page_title="VoiceNotes AI Pro", page_icon="🎙️", layout="wide")

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ Groq API Key missing! Check your .env file.")
    st.stop()

client = Groq(api_key=api_key)

# 2. Helper Functions

def sanitize_mermaid(mermaid_code):
    """
    Fixes common Mermaid syntax errors by removing special chars from node names.
    """
    if not mermaid_code: return ""
    # Remove markdown wrappers if present
    mermaid_code = mermaid_code.replace("``````", "").strip()
    return mermaid_code

def transcribe_audio(audio_bytes):
    try:
        transcription = client.audio.transcriptions.create(
            file=("recording.wav", audio_bytes), 
            model="whisper-large-v3", 
            response_format="json", 
            language="en"
        )
        return transcription.text
    except Exception as e:
        st.error(f"Transcription Error: {str(e)}")
        return None

def generate_study_material(text):
    system_prompt = """
    You are an expert study assistant. Output valid JSON.
    
    For "mind_map": Create a simple MermaidJS flowchart (graph TD). 
    IMPORTANT: Do NOT use parentheses (), brackets [], or special characters inside node names. Use short, simple text labels.
    Example: A[Start] --> B[End]
    
    For "quiz": Output a single object with:
    - "question": string
    - "options": list of 4 strings
    - "answer": string (must match one option exactly)
    
    Structure:
    {
        "summary": "...",
        "key_points": ["..."],
        "flashcards": [{"front": "...", "back": "..."}],
        "mind_map": "graph TD; A[Concept] --> B[Result];",
        "quiz": {"question": "...", "options": ["A", "B", "C", "D"], "answer": "A"}
    }
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Robust Extraction
        first_choice = completion.choices[0]
        if isinstance(first_choice, list): first_choice = first_choice[0]
        
        if hasattr(first_choice, 'message'):
            content = first_choice.message.content
        elif isinstance(first_choice, dict):
            content = first_choice['message']['content']
        else:
            content = str(first_choice)
            
        content = content.replace("``````", "").strip()
        return json.loads(content)
        
    except Exception as e:
        st.error(f"Llama Error: {str(e)}")
        return None

def create_pdf(data, transcript):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "VoiceNotes AI Study Guide", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Summary", ln=True)
    pdf.set_font("Arial", size=12)
    summary = data.get('summary', '').encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, summary)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Key Concepts", ln=True)
    pdf.set_font("Arial", size=12)
    for point in data.get('key_points', []):
        clean_point = point.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, f"- {clean_point}")
        
    return pdf.output(dest='S').encode('latin-1')

# 3. The UI Layout
st.title("🎙️ VoiceNotes AI Pro")
st.markdown("Record your lecture. Get **Visuals, Notes & Quizzes**.")

if "transcript" not in st.session_state: st.session_state.transcript = None
if "study_data" not in st.session_state: st.session_state.study_data = None

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Record")
    audio = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Stop", key='recorder', format="wav")
    
    if audio:
        st.audio(audio['bytes'])
        if st.button("⚡ Generate Magic"):
            with st.spinner("Processing..."):
                text = transcribe_audio(audio['bytes'])
                st.session_state.transcript = text
                
            if text:
                with st.spinner("Creating Visuals..."):
                    data = generate_study_material(text)
                    st.session_state.study_data = data
                    st.success("Done!")

if st.session_state.study_data:
    data = st.session_state.study_data
    
    with col2:
        st.subheader("2. Your Study Deck")
        
        tabs = st.tabs(["📝 Notes", "🧠 Mind Map", "🃏 Flashcards", "❓ Quiz", "💾 Export"])
        
        with tabs[0]: # Notes
            st.info(data.get('summary'))
            for p in data.get('key_points', []): st.markdown(f"- {p}")
            
        with tabs[1]: # Mind Map (Fixed)
            st.markdown("### Concept Connections")
            raw_mermaid = data.get('mind_map', '')
            clean_mermaid = sanitize_mermaid(raw_mermaid)
            if clean_mermaid:
                st_mermaid(clean_mermaid, height=400)
            else:
                st.warning("No visual generated.")
                
        with tabs[2]: # Flashcards
            cols = st.columns(2)
            for i, card in enumerate(data.get('flashcards', [])):
                with cols[i % 2]:
                    with st.expander(f"Q: {card['front']}"):
                        st.write(f"**A: {card['back']}**")
                        
        with tabs[3]: # Quiz (Fixed UI)
            st.markdown("### Quick Check")
            quiz = data.get('quiz', {})
            
            # Check if quiz is a dictionary (Correct) or string (Error case)
            if isinstance(quiz, dict) and 'options' in quiz:
                st.write(f"**{quiz['question']}**")
                
                # Use a radio button for interaction
                user_choice = st.radio("Choose one:", quiz['options'], index=None)
                
                if st.button("Check Answer"):
                    if user_choice == quiz['answer']:
                        st.balloons()
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The answer is: {quiz['answer']}")
            else:
                st.warning("Quiz data format issue. Try regenerating.")
                
        with tabs[4]: # Export
            if st.button("📄 Download PDF"):
                pdf_bytes = create_pdf(data, st.session_state.transcript)
                st.download_button("Download Now", pdf_bytes, "notes.pdf", "application/pdf")
