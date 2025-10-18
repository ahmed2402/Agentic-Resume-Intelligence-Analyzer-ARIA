from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import numpy as np

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.utils import process_documents

def generate_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2"): # type: ignore
    """
    Generates embeddings for a list of texts using HuggingFace Sentence Transformers.
    """
    embeddings_model = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings_model.embed_documents(texts)

def create_faiss_vector_db(texts: List[str], embeddings: HuggingFaceEmbeddings, db_path: str = "faiss_index"):
    """
    Creates a FAISS vector database from texts and their embeddings.
    """
    db = FAISS.from_texts(texts, embeddings)
    db.save_local(db_path)
    print(f"FAISS database created and saved at {db_path}")
    return db

def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculates the cosine similarity between two embedding vectors.
    """
    return cosine_similarity([embedding1], [embedding2])[0][0]

def process_and_embed(resume_path: str, jd_path: str, model_name: str = "all-MiniLM-L6-v2", db_path: str = "faiss_index"):
    """
    Loads and preprocesses resume and job description, generates embeddings,
    stores them in FAISS, and calculates similarity.
    """
    print("Processing documents...")
    processed_data = process_documents(resume_path, jd_path)
    cleaned_resume_tokens = processed_data["cleaned_resume"]
    cleaned_jd_tokens = processed_data["cleaned_job_description"]

    # Convert list of tokens back to a single string for embedding
    resume_text_for_embedding = " ".join(cleaned_resume_tokens)
    jd_text_for_embedding = " ".join(cleaned_jd_tokens)

    print("Generating embeddings...")
    embeddings_model = HuggingFaceEmbeddings(model_name=model_name)
    resume_embedding = embeddings_model.embed_query(resume_text_for_embedding)
    jd_embedding = embeddings_model.embed_query(jd_text_for_embedding)

    print("Creating/Updating FAISS vector database...")
    # For FAISS, we might want to store more than just the two documents.
    # For this task, we will just calculate similarity directly from embeddings.
    # If we were to use FAISS for search, we would add the documents to the DB.

    # Example of how you would add to FAISS if needed for search later
    # texts_to_embed = [resume_text_for_embedding, jd_text_for_embedding]
    # create_faiss_vector_db(texts_to_embed, embeddings_model, db_path)

    print("Calculating similarity...")
    similarity_score = calculate_similarity(resume_embedding, jd_embedding)

    return {
        "resume_embedding": resume_embedding,
        "jd_embedding": jd_embedding,
        "similarity_score": similarity_score
    }

if __name__ == "__main__":
    # Example Usage:
    RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
    JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

    try:
        results = process_and_embed(RESUME_PATH, JD_PATH)
        print("\n--- Results ---")
        print(f"Similarity Score: {results['similarity_score']:.4f}")
        print(f"Resume Embedding (first 5 values): {results['resume_embedding'][:5]}")
        print(f"JD Embedding (first 5 values): {results['jd_embedding'][:5]}")
    except Exception as e:
        print(f"An error occurred: {e}")
