import os
import nltk
from core.utils import process_documents
from core.embedding import calculate_resume_jd_similarity
from core.llm_interface import generate_insights
from core.report_generator import generate_pdf_report

# --- DOWNLOAD NLTK DATA ---
nltk.download("punkt")       # regular tokenizer
nltk.download("punkt_tab")   # fix for LangChain/PyPDFLoader issue
nltk.download("stopwords")
nltk.download("wordnet")

# --- PATHS ---
RESUMES_DIR = "data/raw/resumes"
JD_PATH = "data/raw/job_descriptions/ai_engineer.txt"
OUTPUT_DIR = "data/output"
ANALYSIS_DIR = os.path.join(OUTPUT_DIR, "analysis_reports")
os.makedirs(ANALYSIS_DIR, exist_ok=True)

# --- EXAMPLE SKILLS DICTIONARY ---
skills_dict = {
    "Python": 80,
    "C++": 70,
    "SQL": 65,
    "JavaScript": 60
}

# --- LOOP THROUGH RESUMES ---
for resume_file in os.listdir(RESUMES_DIR):
    if not resume_file.lower().endswith(".pdf"):
        continue

    resume_path = os.path.join(RESUMES_DIR, resume_file)
    print(f"Processing resume: {resume_file}")

    try:
        # --- Load and preprocess resume + JD ---
        processed = process_documents(resume_path, JD_PATH)
        cleaned_resume = " ".join(processed["cleaned_resume"])
        cleaned_jd = " ".join(processed["cleaned_job_description"])

        # --- Calculate similarity score ---
        similarity_score = calculate_resume_jd_similarity(cleaned_resume, cleaned_jd)

        # --- Generate insights from LLM ---
        insights = generate_insights(cleaned_resume, cleaned_jd, similarity_score)

        # --- FIX: Convert lists in insights to strings for proper PDF formatting ---
        for key in insights:
            if isinstance(insights[key], list):
                insights[key] = "\n\n".join(insights[key])  # join list items into paragraphs

        # --- Generate PDF report ---
        report_path = generate_pdf_report(
            insights=insights,
            score=similarity_score,
            resume_name=os.path.splitext(resume_file)[0],
            skills=skills_dict,
            output_dir=ANALYSIS_DIR
        )

        print(f"✅ Report generated at: {report_path}\n")

    except Exception as e:
        print(f"❌ Error while processing {resume_file}: {e}\n")