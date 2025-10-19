import os
import json
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.utils import process_documents
from core.embedding import calculate_resume_jd_similarity

load_dotenv()
groq_api_key = os.environ["GROQ_API_KEY"]

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")

groq_llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")

def generate_insights(resume_text: str, jd_text: str, similarity_score: float) -> dict:
    """
    Generates insights for a resume based on a job description and their matching score
    using an LLM. Insights include Missing Skills, Improvements, Strengths, Weaknesses,
    and Suggestions.
    """
    prompt = f"""
You are an AI assistant specialized in resume analysis and career counseling.
Your task is to provide a detailed analysis of a candidate's resume against a given job description.

Here is the resume text:
<RESUME_TEXT>
{resume_text}
</RESUME_TEXT>

Here is the job description text:
<JD_TEXT>
{jd_text}
</JD_TEXT>

The calculated similarity score between the resume and job description is: {similarity_score:.4f}

Based on the provided resume, job description, and similarity score, please generate the following insights:
1.  **Missing Skills**: List specific skills mentioned in the job description that are not clearly present in the resume.
2.  **Improvements**: Suggest areas where the resume could be enhanced to better match the job description (e.g., phrasing, quantifiable achievements, relevant experience emphasis).
3.  **Strengths**: Highlight key aspects of the resume that strongly align with the job description requirements.
4.  **Weaknesses**: Point out significant gaps or areas in the resume that might be detrimental to the candidate's application for this specific role.
5.  **Suggestions**: Provide actionable advice for the candidate to improve their chances of getting hired for this role, beyond just resume modifications (e.g., interview tips, portfolio suggestions, learning new technologies).

Format your response as a JSON object with the following keys: "missing_skills", "improvements", "strengths", "weaknesses", "suggestions". Each key should have a string value containing the detailed insight.
"""

    try:
        response = groq_llm.invoke(prompt)
        # print("Raw LLM response:", response.content) 
        json_string = response.content.strip()
        start_index = json_string.find("```json")
        end_index = json_string.find("```", start_index + len("```json"))

        if start_index != -1 and end_index != -1:
            json_string = json_string[start_index + len("```json\n") : end_index].strip()
        else:
            # If markdown not found, try to parse the whole string as a fallback
            print("Warning: JSON markdown block not found. Attempting to parse raw response.")
        insights = json.loads(json_string)
        return insights
    except Exception as e:
        print(f"Error generating insights with LLM: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Example Usage:
    RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
    JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

    try:
        print("Loading and cleaning documents...")
        processed_data = process_documents(RESUME_PATH, JD_PATH)
        raw_resume = processed_data["raw_resume_text"]
        raw_jd = processed_data["raw_jd_text"]
        cleaned_resume = processed_data["cleaned_resume"]
        cleaned_jd = processed_data["cleaned_job_description"]
        print("Calculating similarity score...")
        similarity_score = calculate_resume_jd_similarity(cleaned_resume, cleaned_jd)

        print(f"\nResume-JD Similarity Score: {similarity_score:.4f}")

        print("\nGenerating insights...")
        insights = generate_insights(raw_resume, raw_jd, similarity_score)

        if "error" not in insights:
            print("--- AI Generated Insights ---")
            for key, value in insights.items():
                print(f"\n**{key.replace('_', ' ').title()}**:\n{value}")
        else:
            print(f"Failed to generate insights: {insights['error']}")

    except FileNotFoundError as e:
        print(f"File error: {e}")
    except NotImplementedError as e:
        print(f"Feature not implemented: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
