import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.pdf_generator import generate_tailored_resume_pdf
from core.utils import load_resume, load_job_description

class PDFGeneratorAgent:
    """
    The PDFGeneratorAgent is responsible for orchestrating the generation of a tailored CV in PDF format.
    It utilizes the `generate_tailored_resume_pdf` function from `core/pdf_generator.py`.
    """
    def generate_cv(self, resume_path: str, jd_path: str, output_dir: str = "../data/output") -> str | None:
        """
        Generates a tailored CV PDF based on the provided resume and job description.

        Args:
            resume_path (str): The file path to the user's original resume.
            jd_path (str): The file path to the job description.
            output_dir (str): The directory where the generated PDF will be saved. Defaults to "../data/output".

        Returns:
            str | None: The path to the generated PDF file if successful, otherwise None.
        """
        print("\n--- PDF Generator Agent: Initiating Tailored CV Generation ---")
        try:
            # 1. Ingestion Phase: Process documents to get cleaned text
            print("PDF Generator Agent")
            resume_text = load_resume(resume_path)
            jd_text = load_job_description(jd_path)

            # 2. PDF Generation Phase: Call the core function with cleaned texts
            output_pdf_path = generate_tailored_resume_pdf(resume_text, jd_text, output_dir=output_dir)
            
            if output_pdf_path:
                print(f"PDF Generator Agent: Tailored CV successfully generated at {output_pdf_path}")
            else:
                print("PDF Generator Agent: Tailored CV generation failed.")
            return output_pdf_path
        except Exception as e:
            print(f"PDF Generator Agent: An error occurred during CV generation: {e}")
            return None

# if __name__ == "__main__":
#     # Example Usage:
#     RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
#     JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

#     pdf_generator_agent = PDFGeneratorAgent()

#     print("Starting Tailored CV Generation Workflow Example...")
#     output_pdf_path = pdf_generator_agent.generate_cv(RESUME_PATH, JD_PATH)

#     if output_pdf_path:
#         print(f"Tailored CV generation workflow completed. Output saved to: {os.path.abspath(output_pdf_path)}")
#     else:
#         print("Tailored CV generation workflow failed.")
