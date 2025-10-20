import os
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from rag_loader import load_interview_json_files, chunk_documents

KB_DIR = os.path.join(os.path.dirname(__file__), "interview_prep_kb")
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), "vectorstores", "interview_prep_faiss")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-l6-v2"

# --- Build Hybrid Retriever ---
def get_hybrid_retriever(k):
    # 1. Load FAISS vectorstore
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectordb = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    faiss_retriever = vectordb.as_retriever(search_kwargs={"k": k})

    # 2. Load docs for BM25 (in-memory)
    docs = load_interview_json_files(KB_DIR)  # not chunked (BM25 often works better w/ whole Q&A)
    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = k

    # 3. Compose with RRF
    hybrid_retriever = EnsembleRetriever(
        retrievers=[faiss_retriever, bm25_retriever],
        weights=None,       # None = use RRF automatically
        search_type="rrf"   # enables Reciprocal Rank Fusion
    )

    return hybrid_retriever

if __name__ == "__main__":
    k = 10
    query = "How do you handle authentication in REST APIs?"
    print("HYBRID KB RETRIEVAL (vector+bm25+rrf)")
    retriever = get_hybrid_retriever(k)
    print(retriever.invoke(query))
