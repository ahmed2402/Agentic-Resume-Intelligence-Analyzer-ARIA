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
from mock_interview.core.question_generator import QuestionGenerator
from mock_interview.core.report_generator import InterviewReportGenerator

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
            'job_description': '',
            'questions': [],
            'responses': [],
            'analyses': [],
            'current_question_index': 0,
            'session_started': False
        }
    
    # Step 1: Job Description Input
    if not st.session_state.interview_session['session_started']:
        show_job_description_input()
    else:
        # Step 2: Interview Session
        show_interview_session()

def show_job_description_input():
    """Display job description input and question generation"""
    st.subheader("📝 Step 1: Job Description")
    st.write("Please provide the job description to generate relevant interview questions.")
    
    # Job description input
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the complete job description here...",
        value=st.session_state.interview_session.get('job_description', '')
    )
    
    # Interview settings
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.slider("Number of Questions", 3, 10, 5)
        question_types = st.multiselect(
            "Question Types",
            ["technical", "behavioral", "general", "situational"],
            default=["technical", "behavioral", "general"]
        )
    
    with col2:
        st.subheader("🎙️ Recording Settings")
        recording_duration = st.slider("Max Recording Duration (seconds)", 30, 300, 120)
        include_audio_analysis = st.checkbox("Include Audio Analysis", value=True)
        include_sentiment_analysis = st.checkbox("Include Sentiment Analysis", value=True)
    
    # Generate questions button
    if st.button("🎯 Generate Interview Questions", type="primary"):
        if job_description.strip():
            with st.spinner("Generating personalized interview questions..."):
                try:
                    question_generator = QuestionGenerator()
                    questions = question_generator.generate_questions(
                        job_description=job_description,
                        num_questions=num_questions,
                        question_types=question_types
                    )
                    
                    if questions:
                        # Update session state
                        st.session_state.interview_session.update({
                            'job_description': job_description,
                            'questions': questions,
                            'session_started': True,
                            'recording_duration': recording_duration,
                            'include_audio_analysis': include_audio_analysis,
                            'include_sentiment_analysis': include_sentiment_analysis
                        })
                        
                        st.success(f"Generated {len(questions)} personalized interview questions!")
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. Please try again.")
        
                except Exception as e:
                    st.error(f"Error generating questions: {str(e)}")
        else:
            st.warning("Please enter a job description first.")

def show_interview_session():
    """Display the interview session interface"""
    session = st.session_state.interview_session
    questions = session['questions']
    current_index = session.get('current_question_index', 0)
    
    # Progress indicator
    progress = (current_index + 1) / len(questions) if questions else 0
    st.progress(progress, text=f"Question {current_index + 1} of {len(questions)}")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=current_index == 0):
            st.session_state.interview_session['current_question_index'] = max(0, current_index - 1)
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Session"):
            st.session_state.interview_session = {
                'job_description': '',
                'questions': [],
                'responses': [],
                'analyses': [],
                'current_question_index': 0,
                'session_started': False
            }
            st.rerun()
    
    with col3:
        if st.button("➡️ Next", disabled=current_index >= len(questions) - 1):
            st.session_state.interview_session['current_question_index'] = min(len(questions) - 1, current_index + 1)
            st.rerun()
    
    # Current question display
    if current_index < len(questions):
        current_question = questions[current_index]
        
        st.subheader(f"Question {current_index + 1}: {current_question.get('type', 'general').title()}")
        st.info(f"**{current_question['question']}**")
        
        # Question details
        with st.expander("Question Details"):
            st.write(f"**Type:** {current_question.get('type', 'N/A')}")
            st.write(f"**Difficulty:** {current_question.get('difficulty', 'N/A')}")
            st.write(f"**Focus Area:** {current_question.get('focus_area', 'N/A')}")
            if current_question.get('ideal_answer_keywords'):
                st.write(f"**Key Points to Cover:** {', '.join(current_question['ideal_answer_keywords'])}")
        
        # Response capture
        show_response_capture(current_question, current_index)
        
        # Show previous responses if any
        if session['responses'] and any(session['responses']):
            show_previous_responses()
    
    # Final report
    if current_index >= len(questions) - 1 and session['responses'] and any(session['responses']):
        show_final_report()

def show_response_capture(question, question_index):
    """Display response capture interface"""
    st.subheader("🎙️ Your Response")
    
    # Initialize audio_bytes and manual_transcript
    audio_bytes = None
    manual_transcript = ""
    # Initialize audio processor
    if 'audio_processor' not in st.session_state:
        st.session_state.audio_processor = AudioProcessor()
    
    # Audio recording options
    tab1, tab2, tab3 = st.tabs(["🎤 Record Audio", "📁 Upload Audio", "✍️ Type Response"])
        
    with tab1:
        if st_audiorec is not None:
            st.caption("Click to start/stop recording. Speak clearly into your microphone.")
            audio_bytes = st_audiorec()
        else:
            st.warning("Audio recording not available. Please use the upload or type options.")
    
    with tab2:
        st.caption("Upload a recorded audio file (WAV, MP3, OGG, WEBM, M4A)")
        uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "ogg", "webm", "m4a"], 
                                   accept_multiple_files=False, key=f"upload_{question_index}")
        if uploaded is not None:
            audio_bytes = uploaded.read()
        
    with tab3:
        st.caption("Type your response directly")
        manual_transcript = st.text_area("Your Response", height=150, 
                                       placeholder="Type your answer here...",
                                       key=f"manual_{question_index}")
    
    # Process response button
    if st.button("📊 Analyze Response", type="primary"):
        if audio_bytes or manual_transcript.strip():
            process_response(question, question_index, audio_bytes, manual_transcript)
        else:
            st.warning("Please provide a response (record, upload, or type) before analysis.")

def process_response(question, question_index, audio_bytes, manual_transcript):
    """Process and analyze the response"""
    with st.spinner("Analyzing your response..."):
        try:
            # Get transcript
            transcript = manual_transcript.strip() if manual_transcript else ""
            if not transcript and audio_bytes:
                transcript = st.session_state.audio_processor.speech_to_text(audio_bytes)
            
            if not transcript or transcript == "Could not understand audio":
                st.error("Could not process your response. Please try speaking more clearly or typing your answer.")
                return
            
            st.success(f"✅ Response captured: {transcript[:100]}...")
            
            # Analyze audio features
            audio_features = None
            if audio_bytes and st.session_state.interview_session.get('include_audio_analysis', True):
                audio_features = st.session_state.audio_processor.analyze_audio_features(audio_bytes)
            
            # Perform analysis
            analyzer = InterviewAnalyzer()
            analysis = analyzer.analyze_response(
                transcript=transcript,
                question=question['question'],
                ideal_answer="",  # Could be enhanced with ideal answer generation
                audio_features=audio_features,
                job_description=st.session_state.interview_session.get('job_description', '')
            )
            
            # Store results
            session = st.session_state.interview_session
            while len(session['responses']) <= question_index:
                session['responses'].append("")
                session['analyses'].append({})
            
            session['responses'][question_index] = transcript
            session['analyses'][question_index] = analysis
            
            # Show immediate feedback
            # Determine if answer was audio or text
            is_audio = audio_bytes is not None
            show_immediate_feedback(analysis, is_audio)
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing response: {str(e)}")

def show_immediate_feedback(analysis, is_audio):
    """Show immediate feedback for the response"""
    st.subheader("📊 Immediate Analysis")
    
    # Overall score
    overall = analysis.get('overall_score', {})
    score = overall.get('score', 0)
    grade = overall.get('grade', 'N/A')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{score:.1%}", f"Grade: {grade}")
    with col2:
        st.metric("Clarity", f"{analysis.get('clarity', {}).get('score', 0):.1%}")
    with col3:
        if is_audio:
            st.metric("Confidence", f"{analysis.get('confidence', {}).get('score', 0):.1%}")
        else:
            st.metric("Confidence", "N/A")
    
    # Detailed metrics
    st.subheader("Detailed Metrics")
    
    metrics_col1, metrics_col2 = st.columns(2)
    with metrics_col1:
        st.metric("Sentiment", f"{analysis.get('sentiment', {}).get('score', 0):.1%}")
        if is_audio:
            st.metric("Fluency", f"{analysis.get('fluency', {}).get('score', 0):.1%}")
        else:
            st.metric("Fluency", "N/A")
    with metrics_col2:
        st.metric("Relevance", f"{analysis.get('relevance', {}).get('score', 0):.1%}")
        st.metric("Keyword Match", f"{analysis.get('keyword_match', {}).get('score', 0):.1%}")
    
    # Feedback
    st.subheader("💡 Feedback")
    analyzer = InterviewAnalyzer()
    feedback = analyzer.generate_feedback(analysis)
    st.write(feedback)

def show_previous_responses():
    """Show previous responses and analyses"""
    session = st.session_state.interview_session
    questions = session['questions']
    responses = session['responses']
    analyses = session['analyses']
    
    st.subheader("📋 Previous Responses")
    
    for i, (question, response, analysis) in enumerate(zip(questions, responses, analyses)):
        if response.strip():
            with st.expander(f"Question {i+1}: {question['question'][:50]}...", expanded=False):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("**Your Response:**")
                    st.write(response)
                
                with col2:
                    st.write("**Analysis:**")
                    if analysis:
                        overall = analysis.get('overall_score', {})
                        score = overall.get('score', 0)
                        grade = overall.get('grade', 'N/A')
                        st.metric("Score", f"{score:.1%}", f"Grade: {grade}")
                        
                        # Individual metrics
                        metrics = ['clarity', 'confidence', 'sentiment', 'relevance', 'fluency']
                        for metric in metrics:
                            if metric in analysis:
                                metric_score = analysis[metric].get('score', 0)
                                if isinstance(metric_score, (int, float)):
                                    st.metric(metric.title(), f"{metric_score:.1%}")
                                else:
                                    st.metric(metric.title(), str(metric_score))
                
def show_final_report():
    """Show comprehensive final report"""
    st.subheader("📊 Final Interview Report")
    
    if st.button("📄 Generate Comprehensive Report", type="primary"):
        with st.spinner("Generating comprehensive report..."):
            try:
                # Generate comprehensive report
                report_generator = InterviewReportGenerator()
                report_data = report_generator.generate_comprehensive_report(
                    st.session_state.interview_session,
                    st.session_state.interview_session.get('job_description', '')
                )
                
                # Display report sections
                show_report_sections(report_data)
                
                # Download option
                text_report = report_generator.generate_text_report(report_data)
                st.download_button(
                    label="📥 Download Full Report",
                    data=text_report,
                    file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")

def show_report_sections(report_data):
    """Display report sections"""
    # Overall Performance
    st.subheader("🎯 Overall Performance")
    overall = report_data['overall_performance']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{overall['overall_score']:.1%}")
    with col2:
        st.metric("Grade", overall['grade'])
    with col3:
        st.metric("Questions Answered", report_data['session_info']['completed_responses'])
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Strengths")
        for strength in report_data['strengths_weaknesses']['strengths']:
            st.success(f"• {strength}")
    
    with col2:
        st.subheader("⚠️ Areas for Improvement")
        for weakness in report_data['strengths_weaknesses']['weaknesses']:
            st.warning(f"• {weakness}")
    
    # AI Insights
    st.subheader("🤖 AI-Powered Insights")
    st.write(report_data['ai_insights'])
    
    # Recommendations
    st.subheader("💡 Recommendations")
    for i, rec in enumerate(report_data['recommendations'], 1):
        st.write(f"{i}. {rec}")
    
    # Improvement Plan
    st.subheader("📈 Improvement Plan")
    plan = report_data['improvement_plan']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Immediate Actions:**")
        for action in plan['immediate_actions']:
            st.write(f"• {action}")
    
    with col2:
        st.write("**Practice Schedule:**")
        for period, activity in plan['practice_schedule'].items():
            st.write(f"• {period.title()}: {activity}")