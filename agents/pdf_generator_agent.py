import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.pdf_generator import generate_tailored_resume_pdf
from core.utils import process_documents
from agents.ingestion_agent import IngestionAgent
class PDFGeneratorAgent:
    """
    The PDFGeneratorAgent is responsible for orchestrating the generation of a tailored CV in PDF format.
    It utilizes the `generate_tailored_resume_pdf` function from `core/pdf_generator.py`.
    """
    def generate_cv(self, original_resume_text: str, original_jd_text: str) -> str | None:
        """
        Generates a tailored CV PDF based on the provided resume and job description.
        """
        output_pdf_path = generate_tailored_resume_pdf(original_resume_text,original_jd_text)
        return output_pdf_path

# if __name__ == "__main__":
#     # Example Usage:
#     RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
#     JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

#     ingestion_agent = IngestionAgent()
#     pdf_generator_agent = PDFGeneratorAgent()

#     try:
#         # Ingestion Phase
#         print("\n--- Ingestion Phase ---")
#         processed_data = ingestion_agent.ingest(RESUME_PATH, JD_PATH)
#         raw_resume = processed_data["raw_resume_text"]
#         raw_jd = processed_data["raw_jd_text"]

#         print("Starting Tailored CV Generation Workflow Example...")
#         output_pdf_path = pdf_generator_agent.generate_cv(raw_resume, raw_jd)

#         if output_pdf_path:
#             print(f"Tailored CV generation workflow completed. Output saved to: {os.path.abspath(output_pdf_path)}")
#         else:
#             print("Tailored CV generation workflow failed.")
#     except Exception as e:
#         print(f"An error occurred in the PDF generator agent workflow: {e}")



