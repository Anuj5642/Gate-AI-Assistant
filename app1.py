import streamlit as st
import google.generativeai as genai
import os
import requests
import base64
import docx
import PyPDF2
from fpdf import FPDF

# --- API Key Setup ---
GOOGLE_API_KEY = "AIzaSyB-s8_7wiDdMDWcHxTqUctuVEYA49eIY5I"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Page Setup ---
st.set_page_config(page_title="GATE AI Assistant", page_icon="📘", layout="centered")

# --- Styling ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f4f8;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #0072C6;
        color: white;
        font-size: 16px;
        border-radius: 8px;
        padding: 8px 24px;
    }
    .stTextInput>div>input, .stTextArea textarea {
        font-size: 16px;
        padding: 0.75em;
        border-radius: 8px;
        border: 1px solid #ccc;
    }
    .response-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        color: #000;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load Lottie Animation ---
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

try:
    from streamlit_lottie import st_lottie
    lottie_url = "https://assets10.lottiefiles.com/packages/lf20_tno6cg2w.json"
    animation = load_lottie_url(lottie_url)
    if animation:
        st_lottie(animation, height=250, key="ai")
except ImportError:
    st.warning("Install streamlit-lottie for animations: pip install streamlit-lottie")

# --- Title & Instructions ---
st.markdown("<h1 style='text-align: center; color: #336699;'>🎓 GATE AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("#### 🔍 Ask your GATE question below or upload a file:")

# --- File Upload Section ---
uploaded_file = st.file_uploader("📂 Upload your question file (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])
file_question = ""

def extract_text_from_file(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
    return ""

if uploaded_file:
    try:
        file_question = extract_text_from_file(uploaded_file)
        if file_question:
            st.success("✅ File uploaded and question extracted.")
            st.text_area("📘 Extracted Question:", value=file_question, height=150)
        else:
            st.warning("⚠️ Could not extract any content.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

# --- Manual Input ---
manual_question = st.text_input("✍️ Or type your question here:")
question = file_question if file_question else manual_question

# --- Generate PDF ---
def create_pdf(text, filename="GATE_Answer.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    with open(filename, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    return f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="{filename}">📥 Download answer as PDF</a>'

# --- Get Answer Button ---
if st.button("Get Answer"):
    if question.strip() == "":
        st.warning("🚨 Please enter or upload a question.")
    else:
        with st.spinner("🤖 Thinking..."):
            try:
                response = model.generate_content(question)
                answer = response.text
                st.markdown(f"<div class='response-box'>{answer}</div>", unsafe_allow_html=True)
                st.markdown("---")
                st.markdown(create_pdf(answer), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")
