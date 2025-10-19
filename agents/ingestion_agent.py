import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.utils import process_documents

class IngestionAgent:
    """
    The IngestionAgent handles the loading and initial preprocessing of resumes and job descriptions.
    It utilizes functions from `core/utils.py` for document processing.
    """
    def ingest(self, resume_path: str, jd_path: str) -> dict:
        """
        Loads and preprocesses the resume and job description.
        
        Args:
            resume_path (str): The file path to the resume (e.g., PDF).
            jd_path (str): The file path to the job description (e.g., plain text).
            
        Returns:
            dict: A dictionary containing the raw resume and job description text, and their cleaned text (lists of tokens).
        """
        print(f"Ingesting documents: Resume - {resume_path}, Job Description - {jd_path}")
        try:
            ingested_data = process_documents(resume_path, jd_path)
            return ingested_data
        except Exception as e:
            print(f"Error during ingestion: {e}")
            raise

# if __name__ == "__main__":
#     # Example Usage:
#     RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
#     JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

#     ingestion_agent = IngestionAgent()

#     try:
#         ingested_data = ingestion_agent.ingest(RESUME_PATH, JD_PATH)
#         print("\n--- Ingestion Results ---")
#         print(f"Raw Resume Text (first 100 chars): {ingested_data['raw_resume_text'][:100]}...")
#         print(f"Raw Job Description Text (first 100 chars): {ingested_data['raw_jd_text'][:100]}...")
#         print(f"Cleaned Resume (first 20 tokens): {ingested_data['cleaned_resume'][:20]}")
#         print(f"Cleaned Job Description (first 20 tokens): {ingested_data['cleaned_job_description'][:20]}")
#     except Exception as e:
#         print(f"An error occurred during ingestion: {e}")