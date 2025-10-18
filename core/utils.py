import os
from langchain_community.document_loaders import PyPDFLoader
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data 
# nltk.download('stopwords')
# nltk.download('wordnet')

def load_resume(file_path: str):
    """
    Loads a resume from a PDF file using Langchain's PyPDFLoader.
    For .doc files, this function currently raises a NotImplementedError.
    """
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return " ".join([doc.page_content for doc in documents])
    elif file_path.endswith('.doc') or file_path.endswith('.docx'):
        raise NotImplementedError("Loading .doc/.docx files is not yet implemented. Please convert to PDF or plain text.")
    else:
        raise ValueError("Unsupported file type. Only PDF and (placeholder for) DOC/DOCX are accepted.")

def load_job_description(file_path: str) -> str:
    """
    Loads a job description from a text file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Job description file not found at {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def clean_text(text: str) -> list[str]:
    """
    Performs NLP-based text preprocessing on the input text.
    Steps include lowercasing, removing punctuation, numbers, stopwords, and lemmatization.
    Returns a list of cleaned tokens.
    """
    text = text.lower() # Lowercasing
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text) # Remove punctuation
    text = re.sub(r'\d+', '', text) # Remove numbers

    tokens = nltk.word_tokenize(text) # Tokenization

    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words] # Remove stopwords

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens] # Lemmatization

    return tokens

def process_documents(resume_path: str, jd_path: str) -> dict:
    """
    Loads and preprocesses both the resume and job description.
    Returns a dictionary containing the cleaned text for both.
    """
    resume_text = load_resume(resume_path)
    jd_text = load_job_description(jd_path)

    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(jd_text)

    return {
        "cleaned_resume": cleaned_resume,
        "cleaned_job_description": cleaned_jd
    }

# if __name__ == "__main__":
#     # Example usage of the process_documents function
#     resume_path = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
#     jd_path = "../data/raw/job_descriptions/ai_engineer.txt"
    
#     try:
#         processed_data = process_documents(resume_path, jd_path)
#         print("Successfully processed documents:")
#         print(f"Resume tokens: {len(processed_data['cleaned_resume'])} tokens")
#         print(f"Job description tokens: {len(processed_data['cleaned_job_description'])} tokens")
#         print("\nFirst 20 resume tokens:", processed_data['cleaned_resume'][:20])
#         print("First 20 JD tokens:", processed_data['cleaned_job_description'][:20])
#     except FileNotFoundError as e:
#         print(f"File error: {e}")
#     except NotImplementedError as e:
#         print(f"Feature not implemented: {e}")
#     except Exception as e:
#         print(f"Error processing documents: {e}")

