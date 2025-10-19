# main.py
import streamlit as st
from ui.resume_match_ui import show_resume_match_ui
from ui.ats_checker_ui import show_ats_checker_ui
from ui.interview_prep_ui import show_interview_prep_ui

st.set_page_config(page_title="ARIA – Agentic Resume Intelligence Analyzer", layout="wide")

st.title("🤖 ARIA – Agentic Resume Intelligence Analyzer")

# Create tabs for each module
tabs = st.tabs(["📄 Resume Matcher", "📊 ATS Checker", "💬 Interview Prep Chatbot"])

with tabs[0]:
    show_resume_match_ui()

with tabs[1]:
    show_ats_checker_ui()

with tabs[2]:
    show_interview_prep_ui()
