import streamlit as st
import os
import sys
import time # For simulating typing effect
import uuid

# Add the parent directory to the sys.path to allow importing rag_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main conversational chain and the LLM instance from your RAG core
from rag_core.retriever import get_full_conversational_chain, llm
from langchain_core.messages import HumanMessage, AIMessage # For displaying chat history correctly

def show_interview_prep_ui():
    # --- Global styles ---
    st.markdown(
        """
        <style>
            /* Remove Streamlit's default spacing */
            .main .block-container {padding-top: 1rem !important; padding-bottom: 1rem !important;}
            .stApp > div:first-child {padding-top: 1rem !important;}
            
            .app-container {max-width: 800px; margin: 0 auto; padding: 0 1rem;}
            .aria-header h1 {margin-bottom: 0.25rem; text-align: center;}
            .aria-sub {color: #6b7280; margin-top: 0; text-align: center;}
            
            /* Professional chat layout */
            .chat-container {
                max-width: 800px;
                margin: 0.5rem auto 0; /* minimal top margin */
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            /* Chat messages area */
            .chat-messages {
                overflow-y: auto;
                padding: 0.25rem 0; /* minimal padding */
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: #fafafa;
                margin-top: 0.25rem; /* minimal top margin */
            }
            
            /* Chat message styling */
            [data-testid="stChatMessage"] {
                font-size: 0.95rem;
                line-height: 1.6;
                margin: 0.5rem 0;
                padding: 0.75rem 1rem;
                border-radius: 12px;
                max-width: 85%;
            }
            
            /* User messages */
            [data-testid="stChatMessage"][data-message-author="user"] {
                background: #3b82f6;
                color: white;
                margin-left: auto;
                margin-right: 0;
            }
            
            /* Assistant messages */
            [data-testid="stChatMessage"][data-message-author="assistant"] {
                background: white;
                color: #1f2937;
                margin-left: 0;
                margin-right: auto;
                border: 1px solid #e5e7eb;
            }
            
            /* Chat input styling */
            .stChatFloatingInputContainer, .stChatInputContainer {
                max-width: 800px;
                margin: 0.25rem auto 0; /* minimal spacing above input */
                position: static; /* avoid extra reserved space from sticky */
                background: transparent;
                padding: 0; /* remove extra padding */
                border-top: none;
            }
            
            /* Input field styling - fix double outline and make fully rounded */
            [data-testid="stChatInput"] textarea, .stTextInput textarea, .stChatInput textarea {
                border: 1px solid #cbd5e1 !important; /* slate-300 */
                border-radius: 9999px !important; /* pill shape */
                padding: 12px 16px !important;
                font-size: 0.95rem !important;
                resize: none !important;
                outline: none !important;
                box-shadow: none !important;
                background: #ffffff !important;
                color: #111827 !important; /* black text for readability */
                caret-color: #111827 !important;
            }
            /* Placeholder color */
            [data-testid="stChatInput"] textarea::placeholder, .stTextInput textarea::placeholder, .stChatInput textarea::placeholder {
                color: #6b7280 !important; /* gray-500 */
                opacity: 1 !important;
            }
            /* Remove wrapper borders/shadows that create double outlines */
            [data-testid="stChatInput"] div, .stTextInput div {
                box-shadow: none !important;
                outline: none !important;
                border: none !important;
                background: transparent !important;
            }
            
            [data-testid="stChatInput"] textarea:focus, .stTextInput textarea:focus, .stChatInput textarea:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
                outline: none !important;
            }
            
            /* Prompt suggestions */
            .suggestions-container {
                max-width: 800px;
                margin: 0 auto 1rem;
                padding: 0 1rem;
            }
            
            .suggestions-container .stButton > button {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                color: #475569;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 0.9rem;
                transition: all 0.2s;
            }
            
            .suggestions-container .stButton > button:hover {
                background: #e2e8f0;
                border-color: #cbd5e1;
                transform: translateY(-1px);
            }
            
            /* Divider */
            .soft-divider {
                height: 1px;
                background: linear-gradient(90deg, rgba(0,0,0,0), rgba(0,0,0,0.06), rgba(0,0,0,0));
                margin: 0.5rem 0 0.75rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="app-container">', unsafe_allow_html=True)
        st.markdown('<div class="aria-header">', unsafe_allow_html=True)
        st.title("💬 Interview Prep Chatbot")
        st.markdown("<p class='aria-sub'>Ask about data structures, system design, ML, or interview strategy. Backed by a curated knowledge base and hybrid retrieval.</p>", unsafe_allow_html=True)
        st.markdown('<div class="soft-divider" style="margin: 0.1rem 0 0.25rem"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Session State Initialization ---
    if "k_retrieval" not in st.session_state:
        st.session_state.k_retrieval = 5
    
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = get_full_conversational_chain(llm, st.session_state.k_retrieval)
    
    if "streamlit_messages" not in st.session_state:
        st.session_state.streamlit_messages = []
        # Add a welcome message from the assistant on first load
        st.session_state.streamlit_messages.append({"role": "assistant", "content": "Hello! I'm your AI Interview Prep Assistant. How can I help you prepare today?"})

    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""

    # Fresh session_id for each new chat to avoid remembering old history
    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = str(uuid.uuid4())

    # Handle pending reset with loader
    if st.session_state.get("resetting_chat", False):
        with st.spinner("Starting a new chat..."):
            # Clear and reinitialize state
            st.session_state.streamlit_messages = []
            st.session_state.rag_chain = get_full_conversational_chain(llm, 5)
            st.session_state.chat_session_id = str(uuid.uuid4())
            st.session_state.pop("chat_input", None)
            time.sleep(0.6)
        st.session_state.resetting_chat = False
        st.rerun()

    # --- Professional Chat Layout ---
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # --- Prompt suggestions (only show if no conversation yet) ---
    if len(st.session_state.streamlit_messages) <= 1:  # Only welcome message
        st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
        suggestions = [
            "Explain Big-O for common operations with examples.",
            "Design a scalable URL shortener system.",
            "What is the difference between bagging and boosting?",
            "How to approach behavioral questions using STAR?",
            "Python: explain generators vs iterators with code."
        ]
        cols = st.columns(min(4, len(suggestions)))
        for i, s in enumerate(suggestions):
            with cols[i % len(cols)]:
                if st.button(s, use_container_width=True):
                    st.session_state.chat_input = s
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Chat Messages Area ---
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    for message in st.session_state.streamlit_messages:
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Chat Input at Bottom ---
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container
    
    if prompt := st.chat_input("Ask about Data Structures, System Design, ML algorithms, or interview tips...", key="chat_input"):
        # Add user message to Streamlit's display history
        st.session_state.streamlit_messages.append({"role": "user", "content": prompt})
        
        # Generate AI response
        with st.spinner("AI is thinking..."):
            try:
                # Prepare chat history for LangChain
                langchain_chat_history = []
                for msg in st.session_state.streamlit_messages:
                    if msg["role"] == "user":
                        langchain_chat_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        langchain_chat_history.append(AIMessage(content=msg["content"]))
                
                # Get response from RAG chain
                response_content = st.session_state.rag_chain.invoke(
                    {"input": prompt, "chat_history": langchain_chat_history},
                    config={"configurable": {"session_id": st.session_state.chat_session_id}}
                )
                
                # Add AI response to messages
                st.session_state.streamlit_messages.append({"role": "assistant", "content": response_content})
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.streamlit_messages.append({"role": "assistant", "content": "I apologize, but I couldn't generate a response at this moment. Please try again."})
        
        # Re-render the chat area with new messages
        st.rerun()

    # --- ChatGPT-style Sidebar ---
    st.sidebar.markdown("### 💬 Interview Prep")
    
    # New Chat Button (ChatGPT style)
    if st.sidebar.button("➕ New Chat", use_container_width=True, type="primary"):
        # Trigger loader-based reset
        st.session_state.resetting_chat = True
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Minimal spacer
    st.sidebar.markdown("&nbsp;", unsafe_allow_html=True)
    
    # Quick Prompts (ChatGPT style)
    st.sidebar.markdown("#### Quick Prompts")
    if st.sidebar.button("🌳 Data Structures", use_container_width=True):
        st.session_state.chat_input = "What are AVL trees and how do rotations work?"
        st.rerun()
    if st.sidebar.button("🏗️ System Design", use_container_width=True):
        st.session_state.chat_input = "Compare write-through vs write-back caches and trade-offs."
        st.rerun()
    if st.sidebar.button("🤖 Machine Learning", use_container_width=True):
        st.session_state.chat_input = "L1 vs L2 regularization: intuition and when to use each?"
        st.rerun()
    if st.sidebar.button("💼 Interview Tips", use_container_width=True):
        st.session_state.chat_input = "How to approach behavioral questions using STAR method?"
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Info (minimal)
    st.sidebar.markdown("#### About")
    st.sidebar.caption("AI-powered interview prep with hybrid retrieval (semantic + BM25) and Groq LLM.")
    
    # Close app container wrapper
    st.markdown('</div>', unsafe_allow_html=True)

# When this file is run directly (e.g., as part of a larger Streamlit app)
if __name__ == "__main__":
    show_interview_prep_ui()
    
