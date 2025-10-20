import streamlit as st
import tempfile
import os
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from io import BytesIO
import base64

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.ats import ATSAnalyzer, create_ats_score_circle
from core.utils import load_resume

def show_ats_checker_ui():
    st.header("📊 ATS Checker Module")
    st.write("Analyze your resume for Applicant Tracking System (ATS) compatibility and get detailed insights to improve your chances of passing automated screening.")
    
    # Initialize session state for analysis results
    if "ats_analysis_results" not in st.session_state:
        st.session_state.ats_analysis_results = None
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Choose a PDF or DOCX file", 
            type=["pdf", "docx"],
            help="Upload your resume in PDF or DOCX format for ATS analysis"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Display file info
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.caption(f"File size: {file_size:.1f} KB")
    
    with col2:
        st.subheader("📋 Job Description (Optional)")
        job_description = st.text_area(
            "Paste the job description here", 
            height=200,
            help="Provide the job description for keyword matching and targeted analysis"
        )
        
        # Job description tips
        with st.expander("💡 Job Description Tips"):
            st.write("""
            - Copy the complete job posting text
            - Include requirements, responsibilities, and qualifications
            - The more detailed the description, the better the keyword analysis
            - This helps identify missing keywords in your resume
            """)
    
    # Analysis section
    if uploaded_file is not None:
        st.divider()
        
        # Analysis button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Analyze ATS Compatibility", type="primary", use_container_width=True):
                with st.spinner("Analyzing your resume for ATS compatibility..."):
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Initialize ATS analyzer
                        ats_analyzer = ATSAnalyzer()
                        
                        # Perform analysis
                        results = ats_analyzer.calculate_ats_score(tmp_file_path, job_description)
                        
                        # Store results in session state
                        st.session_state.ats_analysis_results = results
                        
                        # Clean up temporary file
                        os.unlink(tmp_file_path)
                        
                        st.success("✅ Analysis completed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        st.session_state.ats_analysis_results = None
    
    # Display results if analysis is complete
    if st.session_state.ats_analysis_results:
        results = st.session_state.ats_analysis_results
        
        if 'error' in results:
            st.error(f"❌ Analysis Error: {results['error']}")
        else:
            display_ats_results(results)
    
    # ATS Tips section
    with st.expander("📚 ATS Optimization Tips"):
        st.markdown("""
        ### 🎯 Key ATS Optimization Strategies:
        
        **Format Compatibility:**
        - Use standard fonts (Arial, Times New Roman, Calibri)
        - Avoid tables, graphics, and complex formatting
        - Use standard section headings (Experience, Education, Skills)
        - Save as PDF for best compatibility
        
        **Keyword Optimization:**
        - Include industry-specific keywords from job descriptions
        - Use action verbs (developed, implemented, managed, led)
        - Match terminology used in the job posting
        - Include technical skills and certifications
        
        **Structure Quality:**
        - Clear contact information at the top
        - Professional summary or objective
        - Chronological work experience
        - Education section with relevant details
        - Skills section with specific technologies
        
        **Content Quality:**
        - Quantify achievements with numbers and percentages
        - Use consistent formatting throughout
        - Keep length appropriate (1-2 pages)
        - Maintain professional tone
        - Include relevant keywords naturally
        """)

def display_ats_results(results):
    """Display comprehensive ATS analysis results"""
    
    # Overall Score Section
    st.divider()
    st.subheader("🎯 Overall ATS Score")
    
    overall_score = results['overall_score']
    
    # Create score visualization
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create circular progress chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = overall_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "ATS Compatibility Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "white"},
                'steps': [
                    {'range': [0, 50], 'color': "gray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300, font={'color': "white", 'family': "Roboto"})
        st.plotly_chart(fig, use_container_width=True)
    
    # Score interpretation
    if overall_score >= 80:
        st.success(f"🎉 **Excellent!** Your resume has great ATS compatibility ({overall_score}%)")
    elif overall_score >= 60:
        st.warning(f"⚠️ **Good** ATS compatibility ({overall_score}%), but there's room for improvement")
    else:
        st.error(f"❌ **Needs Improvement** - Your resume scored {overall_score}% and requires significant optimization")
    
    # Category Breakdown
    st.divider()
    st.subheader("📊 Category Breakdown")
    
    category_scores = results['category_scores']
    
    # Create category comparison chart
    categories = []
    scores = []
    weights = []
    
    for category, data in category_scores.items():
        category_name = category.replace('_', ' ').title()
        categories.append(category_name)
        scores.append(data['score'] * 100)
        weights.append(data['weight'] * 100)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=categories,
        x=scores,
        orientation='h',
        marker=dict(
            color=scores,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Score (%)")
        ),
        text=[f"{score:.1f}%" for score in scores],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Category Scores",
        xaxis_title="Score (%)",
        yaxis_title="Categories",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed category metrics
    st.subheader("📈 Detailed Metrics")
    
    for i, (category, data) in enumerate(category_scores.items()):
        category_name = category.replace('_', ' ').title()
        score_percent = data['score'] * 100
        weight_percent = data['weight'] * 100
        
        with st.expander(f"{category_name} - {score_percent:.1f}% (Weight: {weight_percent:.0f}%)"):
            # Progress bar
            st.progress(score_percent / 100)
            
            # Category-specific insights
            if category == 'format_compatibility':
                st.write("**Format Compatibility Checks:**")
                st.write("• Standard sections present")
                st.write("• No problematic formatting elements")
                st.write("• ATS-friendly file format")
                st.write("• Standard fonts used")
            
            elif category == 'keyword_optimization':
                st.write("**Keyword Optimization Analysis:**")
                st.write("• Industry-specific keywords")
                st.write("• Action verbs usage")
                st.write("• Technical skills mentioned")
                if 'job_description' in results and results.get('job_description'):
                    st.write("• Job description keyword matching")
            
            elif category == 'structure_quality':
                st.write("**Structure Quality Assessment:**")
                st.write("• Contact information completeness")
                st.write("• Professional summary presence")
                st.write("• Work experience formatting")
                st.write("• Education section structure")
                st.write("• Skills section organization")
            
            elif category == 'content_quality':
                st.write("**Content Quality Evaluation:**")
                st.write("• Quantified achievements")
                st.write("• Consistent formatting")
                st.write("• Professional tone")
                st.write("• Appropriate length")
                st.write("• Grammar and clarity")
    
    # Recommendations Section
    st.divider()
    st.subheader("💡 Recommendations")
    
    recommendations = results['recommendations']
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"**{i}.** {rec}")
    
    # Action Items
    st.subheader("🎯 Action Items")
    
    # Create actionable recommendations based on scores
    action_items = []
    
    for category, data in category_scores.items():
        score = data['score']
        if score < 0.7:  # Below 70%
            category_name = category.replace('_', ' ').title()
            
            if category == 'format_compatibility':
                action_items.append("🔧 **Format Issues:** Review and fix formatting problems, use standard fonts, remove tables/graphics")
            elif category == 'keyword_optimization':
                action_items.append("🔑 **Keyword Optimization:** Add more industry-specific keywords and action verbs")
            elif category == 'structure_quality':
                action_items.append("📋 **Structure Issues:** Ensure all standard sections are present and well-organized")
            elif category == 'content_quality':
                action_items.append("✍️ **Content Enhancement:** Add quantified achievements and improve professional tone")
    
    if action_items:
        for item in action_items:
            st.write(item)
    else:
        st.success("🎉 **Great job!** Your resume meets ATS compatibility standards across all categories.")
    
    # Export Results
    st.divider()
    st.subheader("📤 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create summary report
        report_text = f"""
ATS COMPATIBILITY ANALYSIS REPORT
================================

Overall Score: {overall_score}%

Category Breakdown:
"""
        for category, data in category_scores.items():
            category_name = category.replace('_', ' ').title()
            score_percent = data['score'] * 100
            report_text += f"- {category_name}: {score_percent:.1f}%\n"
        
        report_text += f"\nRecommendations:\n"
        for i, rec in enumerate(recommendations, 1):
            report_text += f"{i}. {rec}\n"
        
        st.download_button(
            label="📄 Download Analysis Report",
            data=report_text,
            file_name=f"ats_analysis_report_{overall_score}percent.txt",
            mime="text/plain"
        )
    
    with col2:
        # Create CSV data
        csv_data = pd.DataFrame([
            {"Category": "Overall Score", "Score": overall_score, "Weight": 100},
            *[{"Category": cat.replace('_', ' ').title(), "Score": data['score'] * 100, "Weight": data['weight'] * 100} 
              for cat, data in category_scores.items()]
        ])
        
        csv_string = csv_data.to_csv(index=False)
        
        st.download_button(
            label="📊 Download CSV Data",
            data=csv_string,
            file_name=f"ats_scores_{overall_score}percent.csv",
            mime="text/csv"
        )
