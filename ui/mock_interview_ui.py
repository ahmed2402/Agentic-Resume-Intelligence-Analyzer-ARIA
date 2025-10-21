"""
Mock Interview Analyzer UI
Provides interface for recording and analyzing mock interviews
"""

import streamlit as st
import os
import sys
import tempfile
from datetime import datetime
import json

# Add the mock_interview module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mock_interview'))

from mock_interview.core.audio_processor import AudioProcessor
from mock_interview.core.interview_analyzer import InterviewAnalyzer

# Optional browser recorder component
try:
    from st_audiorec import st_audiorec  # returns WAV bytes
except Exception:
    st_audiorec = None

def show_mock_interview_ui():
    """Main UI for Mock Interview Analyzer"""
    st.header("🎤 Mock Interview Analyzer")
    st.write("Practice your interview skills with AI-powered analysis of your responses.")
    
    # Initialize session state
    if 'interview_session' not in st.session_state:
        st.session_state.interview_session = {
            'questions': [],
            'responses': [],
            'analyses': []
        }
    
    # Sidebar for configuration
    with st.sidebar:
        st.subheader("🎯 Interview Settings")
        
        # Job information
        job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
        job_description = st.text_area("Job Description", height=100, 
                                    placeholder="Paste job description for better analysis")
        
        # Interview type
        interview_type = st.selectbox(
            "Interview Type",
            ["Technical", "Behavioral", "General", "Custom"]
        )
        
        # Recording settings
        st.subheader("🎙️ Recording Settings")
        recording_duration = st.slider("Max Recording Duration (seconds)", 30, 300, 120)
        
        # Analysis settings
        st.subheader("📊 Analysis Settings")
        include_audio_analysis = st.checkbox("Include Audio Analysis", value=True)
        include_sentiment_analysis = st.checkbox("Include Sentiment Analysis", value=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Interview Questions")
        
        # Question selection
        if interview_type == "Technical":
            questions = [
                "Tell me about a challenging technical problem you solved.",
                "How do you approach debugging complex issues?",
                "Describe your experience with version control systems.",
                "What programming languages are you most comfortable with?",
                "How do you ensure code quality in your projects?"
            ]
        elif interview_type == "Behavioral":
            questions = [
                "Tell me about a time you had to work with a difficult team member.",
                "Describe a situation where you had to learn something new quickly.",
                "Give me an example of a time you failed and what you learned.",
                "Tell me about a time you had to meet a tight deadline.",
                "Describe a situation where you had to persuade someone to see your point of view."
            ]
        elif interview_type == "General":
            questions = [
                "Tell me about yourself.",
                "Why are you interested in this position?",
                "What are your greatest strengths?",
                "What are your areas for improvement?",
                "Where do you see yourself in 5 years?"
            ]
        else:
            questions = ["Enter your custom question below"]
        
        # Display current question
        if st.session_state.interview_session['questions']:
            current_question = st.session_state.interview_session['questions'][-1]
        else:
            current_question = st.selectbox("Select a question to practice:", questions)
        
        # Custom question input
        if interview_type == "Custom":
            current_question = st.text_input("Enter your custom question:", value=current_question)
        
        # Display current question
        if current_question:
            st.info(f"**Current Question:** {current_question}")
            
            # Ideal answer input (optional)
            ideal_answer = st.text_area(
                "Ideal Answer (Optional)", 
                height=100,
                placeholder="Enter what a good answer should include for keyword matching..."
            )
    
    with col2:
        st.subheader("🎙️ Capture Audio")
        st.session_state.audio_processor = AudioProcessor()
        audio_bytes = None
        
        if st_audiorec is not None:
            st.caption("Use your browser to record. Click to start/stop.")
            audio_bytes = st_audiorec()
        
        st.caption("Or upload a recorded response (WAV recommended).")
        uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "ogg", "webm", "m4a"], accept_multiple_files=False)
        if uploaded is not None:
            audio_bytes = uploaded.read()
        
        # Optional manual transcript input
        manual_transcript = st.text_area("Or paste your transcript (optional)", height=120)
    
    # Analysis section
    if st.session_state.interview_session['responses']:
        st.subheader("📊 Interview Analysis")
        
        # Display all responses and analyses
        for i, (question, response, analysis) in enumerate(zip(
            st.session_state.interview_session['questions'],
            st.session_state.interview_session['responses'],
            st.session_state.interview_session['analyses']
        )):
            with st.expander(f"Question {i+1}: {question[:50]}..."):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("**Your Response:**")
                    st.write(response)
                
                with col2:
                    st.write("**Analysis:**")
                    
                    # Overall score
                    overall = analysis.get('overall_score', {})
                    score = overall.get('score', 0)
                    grade = overall.get('grade', 'N/A')
                    
                    st.metric("Overall Score", f"{score:.1%}", f"Grade: {grade}")
                    
                    # Individual metrics
                    metrics = ['clarity', 'confidence', 'sentiment', 'keyword_match', 'fluency']
                    for metric in metrics:
                        if metric in analysis:
                            metric_score = analysis[metric].get('score', 0)
                            st.metric(metric.title(), f"{metric_score:.1%}")
                
                # Detailed feedback
                st.write("**Feedback:**")
                analyzer = InterviewAnalyzer()
                feedback = analyzer.generate_feedback(analysis)
                st.write(feedback)
    
    # Add new question button
    if st.button("➕ Add New Question"):
        if current_question and current_question not in st.session_state.interview_session['questions']:
            st.session_state.interview_session['questions'].append(current_question)
            st.session_state.interview_session['responses'].append("")
            st.session_state.interview_session['analyses'].append({})
            st.rerun()
    
    # Process audio if available
    if 'audio_processor' in st.session_state and (audio_bytes or manual_transcript):
        try:
            transcript = manual_transcript.strip() if manual_transcript else ""
            if not transcript and audio_bytes:
                transcript = st.session_state.audio_processor.speech_to_text(audio_bytes)
            
            if transcript and transcript != "Could not understand audio":
                st.success(f"Transcript: {transcript}")
                
                # Analyze audio features
                audio_features = None
                if audio_bytes and include_audio_analysis:
                    audio_features = st.session_state.audio_processor.analyze_audio_features(audio_bytes)
                
                # Perform analysis
                analyzer = InterviewAnalyzer()
                analysis = analyzer.analyze_response(
                    transcript=transcript,
                    ideal_answer=ideal_answer if ideal_answer else "",
                    audio_features=audio_features
                )
                
                # Store results
                if st.session_state.interview_session['questions']:
                    st.session_state.interview_session['responses'][-1] = transcript
                    st.session_state.interview_session['analyses'][-1] = analysis
                else:
                    st.session_state.interview_session['questions'].append(current_question)
                    st.session_state.interview_session['responses'].append(transcript)
                    st.session_state.interview_session['analyses'].append(analysis)
                
                st.rerun()
            else:
                st.error("Could not transcribe audio. Please try speaking more clearly or paste a transcript.")
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
    
    # Export results
    if st.session_state.interview_session['responses']:
        st.subheader("📤 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Generate Report"):
                # Generate detailed report
                report = generate_interview_report(st.session_state.interview_session)
                st.download_button(
                    label="Download Interview Report",
                    data=report,
                    file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("🗑️ Clear Session"):
                st.session_state.interview_session = {
                    'questions': [],
                    'responses': [],
                    'analyses': []
                }
                st.rerun()

def generate_interview_report(session_data):
    """Generate a detailed interview report"""
    report = []
    report.append("MOCK INTERVIEW ANALYSIS REPORT")
    report.append("=" * 50)
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    for i, (question, response, analysis) in enumerate(zip(
        session_data['questions'],
        session_data['responses'],
        session_data['analyses']
    )):
        report.append(f"QUESTION {i+1}:")
        report.append(f"Q: {question}")
        report.append(f"A: {response}")
        report.append("")
        
        # Analysis results
        report.append("ANALYSIS:")
        overall = analysis.get('overall_score', {})
        report.append(f"Overall Score: {overall.get('score', 0):.1%} (Grade: {overall.get('grade', 'N/A')})")
        
        metrics = ['clarity', 'confidence', 'sentiment', 'keyword_match', 'fluency']
        for metric in metrics:
            if metric in analysis:
                score = analysis[metric].get('score', 0)
                details = analysis[metric].get('details', '')
                report.append(f"{metric.title()}: {score:.1%} - {details}")
        
        report.append("")
        report.append("-" * 30)
        report.append("")
    
    return "\n".join(report)
