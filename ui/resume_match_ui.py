import streamlit as st
import os
from dotenv import load_dotenv
# from core.pdf_generator import generate_tailored_resume_pdf
# from core.utils import process_documents

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
        st.subheader("Upload Job Description")
        uploaded_jd = st.file_uploader("Choose a TXT or PDF file", type=["txt", "pdf"], key="jd_upload")
    
    if uploaded_resume is not None and uploaded_jd is not None:
        st.success(f"Resume uploaded: {uploaded_resume.name}")
        st.success(f"Job description uploaded: {uploaded_jd.name}")
        
        # Generate tailored CV button
        if st.button("Generate Tailored CV", type="primary"):
            with st.spinner("Generating tailored CV..."):
                try:
                    # Process documents
                    processed_data = process_documents(uploaded_resume, uploaded_jd)
                    original_resume_text = processed_data["raw_resume_text"]
                    original_jd_text = processed_data["raw_jd_text"]
                    
                    # Generate tailored PDF
                    output_pdf_path = generate_tailored_resume_pdf(original_resume_text, original_jd_text)
                    
                    if output_pdf_path:
                        st.success("Tailored CV generated successfully!")
                        
                        # Display download button
                        with open(output_pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        
                        st.download_button(
                            label="Download Tailored CV",
                            data=pdf_bytes,
                            file_name=os.path.basename(output_pdf_path),
                            mime="application/pdf"
                        )
                    else:
                        st.error("Failed to generate tailored CV. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload both your resume and a job description to generate a tailored CV.")
