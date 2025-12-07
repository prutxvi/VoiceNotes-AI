import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
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
    # Try to get from streamlit secrets (for deployment)
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        st.error("❌ Groq API Key missing!")
        st.stop()

client = Groq(api_key=api_key)

# 2. Helper Functions
def sanitize_mermaid(mermaid_code):
    if not mermaid_code: return ""
    mermaid_code = mermaid_code.replace("``````", "").strip()
    return mermaid_code

def transcribe_audio(audio_file):
    try:
        transcription = client.audio.transcriptions.create(
            file=("recording.wav", audio_file), 
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
    # ✅ NEW NATIVE AUDIO INPUT
    audio_file = st.audio_input("Record your voice")
    
    if audio_file is not None:
        if st.button("⚡ Generate Magic"):
            with st.spinner("Processing..."):
                text = transcribe_audio(audio_file)
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
            
        with tabs[1]: # Mind Map
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
                        
        with tabs[3]: # Quiz
            st.markdown("### Quick Check")
            quiz = data.get('quiz', {})
            if isinstance(quiz, dict) and 'options' in quiz:
                st.write(f"**{quiz['question']}**")
                user_choice = st.radio("Choose one:", quiz['options'], index=None)
                if st.button("Check Answer"):
                    if user_choice == quiz['answer']:
                        st.balloons()
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The answer is: {quiz['answer']}")
            else:
                st.warning("Quiz data format issue.")
                
        with tabs[4]: # Export
            if st.button("📄 Download PDF"):
                pdf_bytes = create_pdf(data, st.session_state.transcript)
                st.download_button("Download Now", pdf_bytes, "notes.pdf", "application/pdf")
