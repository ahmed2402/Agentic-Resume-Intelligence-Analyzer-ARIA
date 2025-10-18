import os
import sys
from typing import List

import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.utils import process_documents

load_dotenv()
groq_api_key = os.environ["GROQ_API_KEY"]
hf_api_key = os.environ["HUGGINGFACEHUB_API_TOKEN"]
groq_llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
huggingface_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-l6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}

)

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of texts using the pre-initialized HuggingFace Sentence Transformers model.
    """
    return huggingface_embeddings.embed_documents(texts)

def store_embeddings_in_faiss(texts: List[str], db_path: str = "../data/embeddings/faiss_index"):
    """
    Creates and stores a FAISS vector database from texts using the pre-initialized embeddings model.
    """
    db = FAISS.from_texts(texts, huggingface_embeddings)
    db.save_local(db_path)
    print(f"FAISS database created and saved at {db_path}")
    return db

def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculates the cosine similarity between two embedding vectors.
    """
    return cosine_similarity([embedding1], [embedding2])[0][0]

def calculate_resume_jd_similarity(cleaned_resume_text: str, cleaned_jd_text: str, store_faiss: bool = False, db_path: str = "../data/embeddings/faiss_index") -> float:
    """
    Calculates the cosine similarity between a cleaned resume and job description.
    Optionally stores the embeddings in a FAISS vector database.
    """
    # Generate embeddings
    texts_to_embed = [cleaned_resume_text, cleaned_jd_text]
    embeddings = create_embeddings(texts_to_embed)
    resume_embedding = embeddings[0]
    jd_embedding = embeddings[1]

    # Optionally store in FAISS
    if store_faiss:
        store_embeddings_in_faiss(texts_to_embed, db_path)

    # Calculate similarity
    similarity_score = calculate_similarity(resume_embedding, jd_embedding)
    return similarity_score


# if __name__ == "__main__":
#     # Example Usage:
#     RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
#     JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

#     try:
#         print("Loading and cleaning documents...")
#         processed_data = process_documents(RESUME_PATH, JD_PATH)
#         cleaned_resume = " ".join(processed_data["cleaned_resume"])
#         cleaned_jd = " ".join(processed_data["cleaned_job_description"])

#         print("Calculating similarity score...")
#         similarity = calculate_resume_jd_similarity(cleaned_resume, cleaned_jd, store_faiss=True)

#         print("\n--- Results ---")
#         print(f"Resume-JD Similarity Score: {similarity:.4f}")

#     except Exception as e:
#         print(f"An error occurred: {e}")