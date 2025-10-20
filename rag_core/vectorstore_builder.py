import os
from rag_loader import load_interview_json_files, chunk_documents
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- CONFIGS ---
KB_DIR = os.path.join(os.path.dirname(__file__), "interview_prep_kb")
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "vectorstores")
VECTORSTORE_PATH = os.path.join(VECTORSTORE_DIR, "interview_prep_faiss")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-l6-v2"


def build_faiss_vectorstore(chunks, persist_dir):
    #Step 1: Intialize embeddings model
    print("🧠 Initializing embedding model (HuggingFace MiniLM)...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Step 2: Build FAISS index
    print("⚙️ Creating FAISS index and adding document chunks...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(persist_dir, exist_ok=True)
    vectorstore.save_local(persist_dir)
    print(f"✅ FAISS vector store created and saved at: {persist_dir}")
    print(f"📊 Total chunks stored: {len(chunks)}")

    return vectorstore

if __name__ == "__main__":
    print("Loading and chunking knowledge base...")
    docs = load_interview_json_files(KB_DIR)

    chunked_docs = chunk_documents(docs, chunk_size=512, chunk_overlap=80)
    print(f"Total chunks for embedding: {len(chunked_docs)}")

    build_faiss_vectorstore(chunked_docs,VECTORSTORE_PATH)

