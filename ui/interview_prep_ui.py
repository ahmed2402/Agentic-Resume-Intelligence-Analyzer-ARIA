import streamlit as st
import os
import sys
import time # For simulating typing effect

# Add the parent directory to the sys.path to allow importing rag_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main conversational chain and the LLM instance from your RAG core
from rag_core.retriever import get_full_conversational_chain, llm
from langchain_core.messages import HumanMessage, AIMessage # For displaying chat history correctly

def show_interview_prep_ui():
    st.header("🧠 AI Interview Prep Assistant")
    st.write("Ask me anything about interview prep, technical concepts, or general career advice. I'll use a knowledge base to give you accurate answers!")

    # --- Session State Initialization ---
    if "k_retrieval" not in st.session_state:
        st.session_state.k_retrieval = 5
    
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = get_full_conversational_chain(llm, st.session_state.k_retrieval)
    
    if "streamlit_messages" not in st.session_state:
        st.session_state.streamlit_messages = []
        # Add a welcome message from the assistant on first load
        st.session_state.streamlit_messages.append({"role": "assistant", "content": "Hello! I'm your AI Interview Prep Assistant. How can I help you prepare today?"})
    
    # --- Chat Display ---
    for message in st.session_state.streamlit_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Chat Input and Response Generation ---
    if prompt := st.chat_input("Ask about Data Structures, System Design, ML algorithms, or interview tips..."):
        # Add user message to Streamlit's display history
        st.session_state.streamlit_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate typing/thinking
            message_placeholder.markdown("AI is thinking...") 
            
            
            try:
                # Prepare chat history for LangChain
                # Convert Streamlit's display messages to LangChain's HumanMessage/AIMessage format
                langchain_chat_history = []
                for msg in st.session_state.streamlit_messages:
                    if msg["role"] == "user":
                        langchain_chat_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        langchain_chat_history.append(AIMessage(content=msg["content"]))
                
                # The session_id here is crucial for LangChain's RunnableWithMessageHistory
                # to correctly manage chat history. We use a fixed ID for this Streamlit session.
                response_content = st.session_state.rag_chain.invoke(
                    {"input": prompt, "chat_history": langchain_chat_history}, # <--- MODIFIED HERE
                    config={"configurable": {"session_id": "streamlit_user_session"}}
                )
                full_response = response_content

            except Exception as e:
                st.error(f"It seems I'm having trouble connecting or processing. Error: {e}")
                full_response = "I apologize, but I couldn't generate a response at this moment. Please check your API key, ensure the backend is running, and try again."
            
            message_placeholder.markdown(full_response)
            st.session_state.streamlit_messages.append({"role": "assistant", "content": full_response})

    # --- Controls ---
    st.sidebar.header("Settings")
    new_k_retrieval = st.sidebar.slider(
        "Number of documents to retrieve (k)",
        min_value=1, max_value=15, value=st.session_state.k_retrieval, step=1,
        help="Adjusts how many relevant documents the AI considers for its answer."
    )
    if new_k_retrieval != st.session_state.k_retrieval:
        st.session_state.k_retrieval = new_k_retrieval
        st.session_state.rag_chain = get_full_conversational_chain(llm, st.session_state.k_retrieval)
        st.sidebar.success(f"Retriever k set to {new_k_retrieval}. Chain reinitialized.")

    # More prominent "New Chat" button
    if st.sidebar.button("✨ Start New Chat", help="Clear current conversation and start fresh."):
        st.session_state.streamlit_messages = []
        st.session_state.rag_chain = get_full_conversational_chain(llm, st.session_state.k_retrieval) # Resets LangChain history
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info(
        "This chatbot uses a hybrid retrieval system (semantic + BM25) with Reciprocal Rank Fusion (RRF) "
        "and a Groq LLM to provide relevant interview preparation answers. "
        "It can engage in casual conversation or answer RAG-based technical questions."
    )

# When this file is run directly (e.g., as part of a larger Streamlit app)
if __name__ == "__main__":
    show_interview_prep_ui()
