import os
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
# from langchain.retrievers import EnsembleRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from rag_loader import load_interview_json_files, chunk_documents
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


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


load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found. Please set in .env file.")
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")

# --- Prompt Template ---
# This prompt will guide the LLM to answer questions based on the retrieved context.
template = """
You are an expert technical interviewer assistant. Use the following pieces of retrieved context
to answer the question. If you don't know the answer, just say that you don't know.
Do not make up an answer.

Context:
{context}

Question: {question}

Answer:
"""
context_prompt = ChatPromptTemplate.from_template(template)

# --- Retrieval Chain ---
def get_qa_retrieval_chain(k=5):
    hybrid_retriever = get_hybrid_retriever(k=k)

    rag_chain = (
        {"context": hybrid_retriever, "question": RunnablePassthrough()}
        | context_prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

# Initialize ChatMessageHistory
chat_history = ChatMessageHistory()

# Define a function to get session history
def get_session_history(session_id: str) -> ChatMessageHistory:
    """
    Returns the chat message history for a given session ID.
    
    This function is used by the RunnableWithMessageHistory to retrieve
    the appropriate chat history for each conversation session. Currently,
    it returns a single global chat_history instance for all sessions.
    
    Parameters:
    session_id (str): The unique identifier for the conversation session
    
    Returns:
    ChatMessageHistory: The chat history object containing all messages
                        for the specified session
    """
    return chat_history

# Create a chain with message history
conversational_retrieval_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Given a chat history and the latest user question "
                   "which might reference context in the chat history, "
                   "formulate a standalone question which can be understood without "
                   "the chat history. Do NOT answer the question, just reformulate it "
                   "if necessary and otherwise return it as is."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    groq_llm,
    retriever,
    contextualize_q_prompt
)

# Combine the history-aware retriever with the document chain
qa_chain = create_stuff_documents_chain(groq_llm, prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)



# 1. Intent Classification
# We'll create a simple LLM chain to classify the intent
# For simplicity, we'll use a direct prompt for classification.
# In a more advanced scenario, you might fine-tune a smaller model for this.

classification_prompt = ChatPromptTemplate.from_template(
    """Given the following chat history and user question, classify the user's intent as either 'chit_chat' or 'rag_query'. 
    Only return 'chit_chat' or 'rag_query'. Do not include any other text.

Chat History: {chat_history}
User Question: {input}"""
)

classification_chain = classification_prompt | groq_llm

# 2. Chit-Chat Chain
chit_chat_prompt = ChatPromptTemplate.from_template(
    """You are a friendly AI assistant. Engage in a casual conversation with the user.
    Keep your responses concise and relevant to the user's input.

Chat History: {chat_history}
User Question: {input}"""
)

chit_chat_chain = chit_chat_prompt | groq_llm

# 3. RAG Chain (already defined as rag_chain, but we need to ensure it uses chat_history properly)
# The rag_chain already handles chat_history for query rewriting.

# Define the overall conversational chain with routing
# This code creates a conversational chain that routes user queries based on intent classification
# The RunnableWithMessageHistory wraps the chain to maintain conversation history across interactions
# RunnableBranch conditionally routes to either chit_chat_chain or rag_chain:
# - If classification_chain determines the intent is 'chit_chat', it uses chit_chat_chain
# - Otherwise, it defaults to the rag_chain for document-based question answering
# The lambda function extracts input and chat_history to pass to the classification chain
# get_session_history manages conversation history storage by session_id
# input_messages_key and history_messages_key specify the field names for current input and historical messages

full_conversational_chain = RunnableWithMessageHistory(
    RunnableBranch(
        (
            lambda x: classification_chain.invoke({"input": x["input"], "chat_history": x["chat_history"]}).content == "chit_chat",
            chit_chat_chain,
        ),
        rag_chain,
    ),
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)
