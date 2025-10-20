import os
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import json

def load_interview_json_files(directory: str) -> List[Document]:
    docs = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            loader = JSONLoader(
                file_path=filepath,
                jq_schema=".[]",
                text_content=False
            )
            raw = loader.load()
            skipped = 0
            file_docs = []
            for doc in raw:
                qa = None
                try:
                    if isinstance(doc.page_content, dict):
                        qa = doc.page_content
                    elif isinstance(doc.page_content, str):
                        qa = json.loads(doc.page_content)
                    else:
                        qa = {}
                except Exception as e:
                    qa = {}
                question = qa.get('question', '').strip() if qa else ''
                answer = qa.get('answer', '').strip() if qa else ''
                if not question or not answer:
                    skipped += 1
                    continue
                content = f"Q: {question}\nA: {answer}"
                metadata = {
                    "topic": qa.get("topic"),
                    "domain": qa.get("domain"),
                    "difficulty": qa.get("difficulty"),
                    "id": qa.get("id"),
                    "filename": filename
                }
                doc_obj = Document(page_content=content, metadata=metadata)
                docs.append(doc_obj)
                file_docs.append(doc_obj)
            # Optional: print skipped files if debugging
            # if skipped:
            #     print(f"Skipped {skipped} Q&A in {filename} due to missing Q/A fields.")
    return docs

def chunk_documents(
    docs: List[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 80
) -> List[Document]:
    """
    Splits documents into smaller chunks for better embedding/retrieval. Small Q&A are not split (default), but for longer content like explanations, you may adjust chunk_size.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    # Most Q&A will not be split due to their short size (unless you increase chunk_size)
    chunked_docs = splitter.split_documents(docs)
    return chunked_docs

if __name__ == "__main__":
    kb_dir = "./interview_prep_kb"
    all_docs = load_interview_json_files(kb_dir)
    print(f"Loaded {len(all_docs)} Q&A documents from {kb_dir}")
    chunked = chunk_documents(all_docs, chunk_size=512, chunk_overlap=80)
    print(f"Final number of chunks: {len(chunked)}")
    # Optionally show a few example chunks
    for d in chunked[:3]:
        print("---\n", d.page_content, "\nMETA:", d.metadata)
