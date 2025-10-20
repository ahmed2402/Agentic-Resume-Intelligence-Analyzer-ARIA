from fpdf import FPDF
import os
import matplotlib.pyplot as plt
import uuid
from io import BytesIO

class ResumeReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 10, "Resume Analysis Report", ln=True, align="C")
        self.ln(5)

    def add_section(self, title, content):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, title, ln=True)
        self.ln(2)
        self.set_font("Helvetica", "", 12)
        self.multi_cell(0, 7, content)
        self.ln(4)

    def add_image(self, image_bytes, w=150):
        """Add an image to the PDF (skills chart) from bytes"""
        self.image(image_bytes, x=(210-w)/2, w=w)  # center horizontally
        self.ln(10)

def generate_skills_chart(skills: dict):
    """
    Generates a bar chart of skills and returns a BytesIO image.
    """
    if not skills:
        return None

    plt.figure(figsize=(6, 4))
    names = list(skills.keys())
    values = list(skills.values())
    plt.barh(names, values, color="#4CAF50")
    plt.xlabel("Proficiency Level")
    plt.title("Skills Chart")
    plt.tight_layout()

    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='PNG')
    plt.close()
    img_bytes.seek(0)
    return img_bytes

def generate_pdf_report(insights: dict, score: float, resume_name: str = "Candidate",
                        skills: dict = None, output_dir="data/output/analysis_reports/"):
    """
    Generates a professional PDF report with:
    - Resume insights
    - Similarity score
    - Skills chart (at the beginning, after the score)
    - Unique ID for each report
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique ID for PDF
    unique_id = str(uuid.uuid4())[:8]
    pdf_filename = f"{resume_name.replace(' ', '_')}_{unique_id}_report.pdf"
    output_path = os.path.join(output_dir, pdf_filename)

    # Create PDF
    pdf = ResumeReport()
    pdf.add_page()

    # Header info
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Candidate: {resume_name}", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Match Score: {round(score * 100, 2)} / 100", ln=True)
    pdf.ln(5)

    # Add skills chart immediately after score
    if skills:
        chart_bytes = generate_skills_chart(skills)
        if chart_bytes:
            pdf.add_section("Skills Chart", "")
            pdf.add_image(chart_bytes)

    # Add insights sections
    pdf.add_section("1. Strengths", insights.get("strengths", "No strengths found."))
    pdf.add_section("2. Missing Skills", insights.get("missing_skills", "No missing skills found."))
    pdf.add_section("3. Areas of Improvement", insights.get("improvements", "No improvements suggested."))
    pdf.add_section("4. Weaknesses", insights.get("weaknesses", "No weaknesses detected."))
    pdf.add_section("5. Suggestions", insights.get("suggestions", "No suggestions provided."))

    # Save PDF
    pdf.output(output_path)
    print(f"✅ Report successfully saved at {output_path}")
    return output_path
