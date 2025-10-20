import os
import sys 
import json
import datetime 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from fpdf import FPDF # For PDF generation

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.utils import process_documents
load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")

groq_llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
is_mock_llm = False

# --- LLM Content Generation Function (THE INTELLIGENCE) ---

def generate_tailored_cv_content_from_llm(original_resume_text: str, original_jd_text: str) -> str:
    """
    Generates tailored CV content using an LLM, structured for a new CV document.
    """
    if is_mock_llm:
        print("MOCK LLM: Returning structured placeholder content.")
        return """
#John Mockup Doe | Senior Python Engineer#

**CONTACT INFORMATION**
Phone: (555) 123-4567
Email: john.doe@example.com
LinkedIn: linkedin.com/in/johndoe
GitHub: github.com/johndoe
---

**SUMMARY**
Results-driven Senior Python Engineer with 5+ years of experience specializing in scalable microservices architecture. Optimized data processing pipelines, **reducing latency by 45%** and achieving 99.9% uptime. Successfully led a team of 4 engineers to deploy three major product features.
---

**WORK EXPERIENCE**

Senior Software Engineer | TechCorp Global | Jan 2022 - Present
* Architected a new microservice system using Flask, supporting **over 1,000 requests per second (RPS)**.
* Optimized database queries and caching mechanisms, leading to a **40% reduction in cloud infrastructure costs**.
* Mentored junior engineers on clean code practices, improving team code quality scores by **25%** within six months.

Software Developer | Startup X | Jun 2019 - Dec 2021
* Developed core features for a financial dashboard used by **50,000+ monthly users**.
* Engineered robust unit and integration tests, decreasing production bugs by **18%**.
---

**SELECTED PROJECTS**

Scalable Data API | Python / Flask
* Designed and deployed a containerized API that handled **10 million data points daily**, providing real-time analytics.
* Improved API response time by **200 milliseconds** through efficient data structure choices.
---

**EDUCATION**

M.Sc. Computer Science | University of Innovation | 2019
B.Sc. Computer Engineering | State University | 2017

**TECHNICAL SKILLS**

Programming Languages: Python (Expert), JavaScript, TypeScript
Frameworks: Flask, Django, React
Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD
Databases: PostgreSQL, MongoDB, Redis
"""

    # Real LLM call if API key is present
    prompt = f"""
You are the **Executive Resume Editor**. Your task is to rewrite the candidate's provided resume to be a high-impact, single-page professional document perfectly tailored to the job description.

**STRICT GENERATION RULES:**
1.  **Achievement-Only Bullets:** Every bullet point MUST start with a strong, capitalized action verb (e.g., Engineered, Optimized, Architected).
2.  **Mandatory Quantification:** Every bullet point MUST include a numerical result (e.g., percentage, time saved, user count, or data scale) to demonstrate clear impact.
3.  **Bolding for Headers:** You MUST use **double asterisks (**) ** to bold the Candidate Name and all Section Headings (SUMMARY, WORK EXPERIENCE, etc.).
4.  **Bullet Points:** Use a simple asterisk (*) for all bullet points.
5.  **Date Format:** Use a simple hyphen (-) for date ranges (e.g., Jan 2025 - Present).
6.  **Horizontal Separators:** Place '---' immediately after the Contact Information, Summary, Work Experience, and Selected Projects sections.

Here is the candidate's **original resume content**:
<ORIGINAL_RESUME>
{original_resume_text}
</ORIGINAL_RESUME>

Here is the **target job description**:
<JOB_DESCRIPTION>
{original_jd_text}
</JOB_DESCRIPTION>

**Generate the final, fully tailored CV content in clean, plain text, structured as follows:**
  ...(see the prompt structure for user input for details )...
"""
    try:
        response = groq_llm.invoke(prompt)
        clean_content = response.content
        clean_content = clean_content.encode('ascii', 'ignore').decode('ascii')
        clean_content = clean_content.replace("# ", "").replace("  ", " ")
        return clean_content
    except Exception as e: 
        print(f"Error generating tailored CV content with LLM: {e}")
        # Return a simple, safe structure on failure to prevent the PDF generator from crashing on empty input
        return f"**GENERATION ERROR**\n\nError: {e}\n---"


# --- PDF Document Creation Function (NEWLY ACTIVATED AND MODIFIED) ---

        
# --- [The rest of the code: generate_tailored_resume_pdf and __main__ remains the same] ---
# ... (The rest of the file content) ...

class PDF(FPDF):
    """Custom FPDF class for CV generation."""
    
    def add_bullet_point(self, text, indent=8, bullet_size=2):
        """
        Adds a bullet point with indentation, robustly handles positioning
        to avoid 'Not enough horizontal space' error.
        """
        start_y = self.get_y()
        
        # 1. Print the bullet (dot)
        self.set_fill_color(0, 0, 0)
        # Position the bullet based on the left margin
        self.circle(self.l_margin + indent - 3, start_y + self.font_size / 2, bullet_size, 'F')
        
        # 2. Print the text:
        # Set the X position for the text to start after the bullet
        self.set_x(self.l_margin + indent)
        
        # Calculate the available width: 
        # Page Width - Left Margin - Right Margin - Bullet Indent
        SAFE_WIDTH = self.w - self.l_margin - self.r_margin - indent
            
        # Fallback check to prevent zero/negative width error
        if SAFE_WIDTH < 10: 
            SAFE_WIDTH = self.w - self.l_margin - self.r_margin # Use full printable width as emergency fallback

        self.multi_cell(SAFE_WIDTH, 5, text, 0, 'L')
        self.ln(1) # Extra space after bullet

def create_pdf_document(content: str, output_path: str, title: str = "Tailored Resume"):
    """
    Parses the LLM-generated plain text content and creates a PDF using FPDF.
    """
    pdf = PDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Use consistent margins (20mm all around)
    pdf.set_margins(20, 20, 20) 
    pdf.add_page()
    
    # Use Helvetica to avoid Deprecation Warnings
    
    # Simple line-by-line parsing
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(4)
            continue
            
        # 📌 CRITICAL FIX: Ensure the cursor is always reset to the left margin
        #    before drawing a new major element. This fixes the 'Not enough horizontal space' issue.
        pdf.set_x(pdf.l_margin) 

        # 1. Check for Horizontal Rule
        if line == '---':
            pdf.ln(1)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(3)
            continue

        # 2. Check for Bullet Points
        if line.startswith('* '):
            bullet_text = line[2:]
            pdf.set_font('Helvetica', '', 10)
            pdf.add_bullet_point(bullet_text, indent=8)
            continue
            
        # 3. Check for BOLD headers (enclosed in **)
        if line.startswith('**') and line.endswith('**'):
            clean_line = line.replace('**', '')
            
            # Special handling for Name/Title (biggest font)
            if ' | ' in clean_line.split('\n')[0]:
                pdf.set_font('Helvetica', 'B', 16)
                pdf.set_text_color(20, 20, 20)
                # Ensure the cell starts at the left margin before centering
                pdf.set_x(pdf.l_margin) 
                pdf.multi_cell(0, 8, clean_line.split(' | ')[0], 0, 'C')
                pdf.set_font('Helvetica', '', 11)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(0, 5, clean_line.split(' | ')[1], 0, 'C')
                pdf.ln(2)
            # Regular Section Headers
            elif len(clean_line) < 30 and clean_line.isupper():
                pdf.ln(2)
                pdf.set_font('Helvetica', 'B', 12)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6, clean_line, 0, 'L')
                pdf.set_line_width(0.2)
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + pdf.get_string_width(clean_line) + 5, pdf.get_y())
                pdf.ln(1)
            else:
                # Other bold lines (like Job Title | Company | Dates)
                pdf.set_font('Helvetica', 'B', 10)
                pdf.multi_cell(0, 5, clean_line, 0, 'L')
                pdf.ln(1)

        # 4. Standard Text (Contact Info, Education, Skills, Summary prose)
        else:
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(50, 50, 50)
            # Ensure text starts at the left margin
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, line, 0, 'L')
            
    try:
        pdf.output(output_path, 'F')
        return True
    except Exception as e:
        print(f"Error saving PDF file: {e}")
        return False

# --- Workflow Orchestration Function ---
def generate_tailored_resume_pdf(original_resume_text: str, original_jd_text: str, output_filename_prefix: str = "Tailored_CV", output_dir: str = "../data/output") -> str | None:
    print("\n--- Starting Tailored CV Generation Workflow ---")
    
    try:
        # 1. CV Content Generation Phase
        print("\n--- Tailored CV Content Generation Phase ---")
        tailored_cv_content = generate_tailored_cv_content_from_llm(original_resume_text, original_jd_text)

        # 2. FILE CREATION: Write to PDF
        print("\n--- Creating PDF Output File ---")
        os.makedirs(output_dir, exist_ok=True)
        
        # --- FILENAME LOGIC ---
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        output_filename_base = os.path.join(output_dir, f"{output_filename_prefix}_{timestamp}_CV")
        
        output_pdf_filename = f"{output_filename_base}.pdf"
        
        if create_pdf_document(tailored_cv_content, output_pdf_filename):
            print(f"\nFull workflow successful.")
            print(f"  --> Tailored PDF Content Saved Here: {os.path.abspath(output_pdf_filename)}")
            print("--- CV Generation Workflow Completed Successfully ---")
            return output_pdf_filename
        else:
            # Fallback to saving raw content if PDF creation fails
            output_md_filename = f"{output_filename_base}.md"
            with open(output_md_filename, 'w', encoding='utf-8') as f:
                f.write(tailored_cv_content)
            print(f"PDF creation failed. Raw content saved to {output_md_filename}")
            return None

    except Exception as e:
        print(f"An unexpected error occurred during the CV generation workflow: {e}")
        return None
    
if __name__ == "__main__":
    # Example Usage:
    RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
    JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

    # Import for example usage only, simulating agent output

    print("Starting Tailored CV Generation Example...")
    try:
        print("Loading and cleaning documents for example (simulating Ingestion Agent output)...")
        processed_data = process_documents(RESUME_PATH, JD_PATH)
        original_resume_text = processed_data["raw_resume_text"]
        original_jd_text = processed_data["raw_jd_text"]

        output_pdf_path = generate_tailored_resume_pdf(original_resume_text, original_jd_text)

        if output_pdf_path:
            print(f"Full workflow completed. Tailored CV saved to: {os.path.abspath(output_pdf_path)}")
        else:
            print("Full workflow failed.")
    except Exception as e:
        print(f"An error occurred in the example usage: {e}")
