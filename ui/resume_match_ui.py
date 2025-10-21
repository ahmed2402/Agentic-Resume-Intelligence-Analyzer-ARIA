import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from dotenv import load_dotenv
import tempfile
import shutil
from workflows.resume_match_pipeline import app 

load_dotenv()

def show_resume_match_ui():
    st.header("📄 Resume Matcher")
    st.write("Upload your resume and a job description to generate a tailored CV.")
    
    # File upload section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Your Resume")
        uploaded_resume = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"], key="resume_upload")
    
    with col2:
        st.subheader("Enter Job Description")
        jd_text_input = st.text_area(
            "Paste Job Description text here", 
            height=300, 
            key="jd_text_input",
            placeholder="Paste the job description content here..."
        )
  
    
    if uploaded_resume is not None and jd_text_input:
        st.success(f"Resume uploaded: {uploaded_resume.name}")
        st.success("Job description text entered.")
        
        # Generate tailored CV button
        if st.button("Generate Similarity Score, Insights and Tailored CV", type="primary"):
            with st.spinner("Generating tailored CV and insights..."):
                temp_dir = None
                try:
                    # Create a temporary directory to save uploaded files
                    temp_dir = tempfile.mkdtemp()
                    
                    # Save uploaded resume to a temporary file
                    resume_path = os.path.join(temp_dir, uploaded_resume.name)
                    with open(resume_path, "wb") as f:
                        f.write(uploaded_resume.getbuffer())
                    
                        
                    # Prepare initial state for the pipeline
                    initial_state = {"resume_path": resume_path, "jd_text": jd_text_input}
                    
                    # Run the pipeline
                    final_state = {}
                    for state in app.stream(initial_state):
                        final_state.update(state) # Accumulate the state changes
                    
                    st.success("Pipeline executed successfully!")
                    
                    # Display Results
                    st.subheader("Results")
                    
                    # Similarity Score
                    embed_output = final_state.get('embed', {})
                    similarity_score = embed_output.get('similarity_score')
                    if similarity_score is not None:
                        st.metric(label="Resume-Job Description Similarity Score", value=f"{similarity_score:.2%}")
                    else:
                        st.warning("Similarity score could not be determined.")

                    # AI Generated Insights
                    advise_output = final_state.get('advise', {})
                    insights = advise_output.get('insights', {})
                    if insights:
                        st.subheader("AI-Generated Insights:")
                        for section, content in insights.items():
                            with st.expander(f"**{section.replace('_', ' ').upper()}**"):
                                st.markdown(content)
                    else:
                        st.warning("No insights were generated.")
                        
                    # Tailored CV Download
                    pdf_output = final_state.get('generate_pdf', {})
                    output_pdf_path = pdf_output.get('output_pdf_path')
                    if output_pdf_path and os.path.exists(output_pdf_path):
                        st.subheader("Tailored CV")
                        with open(output_pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        
                        st.download_button(
                            label="Download Tailored CV",
                            data=pdf_bytes,
                            file_name=os.path.basename(output_pdf_path),
                            mime="application/pdf"
                        )
                        # st.info(f"Tailored CV PDF generated at: `{output_pdf_path}`")
                    else:
                        st.error("Failed to generate tailored CV. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred during pipeline execution: {str(e)}")
                finally:
                    # Clean up temporary directory
                    if temp_dir and os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                        # st.info("Cleaned up temporary files.")
    else:
        st.info("Please upload both your resume and a job description to generate a tailored CV.")