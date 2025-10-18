import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.embedding import calculate_resume_jd_similarity
# from agents.ingestion_agent import IngestionAgent

class EmbeddingAgent:
    """
    The EmbeddingAgent generates embeddings for cleaned resume and job description texts
    and calculates their similarity score.
    It utilizes functions from `core/embedding.py`.
    """
    def process(self, cleaned_resume_text: str, cleaned_jd_text: str, store_faiss: bool = False) -> float:
        """
        Generates embeddings for the cleaned resume and job description and calculates
        their cosine similarity.

        Args:
            cleaned_resume_text (str): The preprocessed text of the resume.
            cleaned_jd_text (str): The preprocessed text of the job description.
            store_faiss (bool): Whether to store the embeddings in a FAISS vector database. Defaults to False.

        Returns:
            float: The cosine similarity score between the resume and job description embeddings.
        """
        print("Generating embeddings and calculating similarity...")
        try:
            similarity_score = calculate_resume_jd_similarity(cleaned_resume_text, cleaned_jd_text, store_faiss=store_faiss)
            print(f"Similarity score calculated: {similarity_score:.4f}")
            return similarity_score
        except Exception as e:
            print(f"Error during embedding generation or similarity calculation: {e}")
            raise

# if __name__ == "__main__":
    # Example Usage:
    RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
    JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

    ingestion_agent = IngestionAgent()
    embedding_agent = EmbeddingAgent()

    try:
        # Ingest documents first
        print("\n--- Ingestion Phase ---")
        processed_data = ingestion_agent.ingest(RESUME_PATH, JD_PATH)
        cleaned_resume = " ".join(processed_data["cleaned_resume"])
        cleaned_jd = " ".join(processed_data["cleaned_job_description"])

        # Process with Embedding Agent
        print("\n--- Embedding Phase ---")
        similarity_score = embedding_agent.process(cleaned_resume, cleaned_jd, store_faiss=True)

        print("\n--- Results ---")
        print(f"Final Resume-JD Similarity Score: {similarity_score:.4f}")

    except Exception as e:
        print(f"An error occurred in the embedding agent workflow: {e}")
