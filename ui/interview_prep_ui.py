import streamlit as st
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

def show_interview_prep_ui():
    st.header("💬 Interview Prep Chatbot")
    st.write("Practice your interview skills with our AI-powered chatbot. Get personalized feedback and tips!")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Job description input
    st.subheader("Job Information")
    job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer, Data Analyst")
    job_description = st.text_area("Job Description", height=150, 
                                  placeholder="Paste the job description here for more tailored practice")
    
    # Chat interface
    st.subheader("Chat with Interview Coach")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask interview questions or practice your responses..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Initialize Groq LLM
                groq_api_key = os.environ.get("GROQ_API_KEY")
                if groq_api_key:
                    llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
                    
                    # Create context-aware prompt
                    context_prompt = f"""
                    You are an experienced interview coach helping a candidate prepare for a job interview.
                    Job Title: {job_title if job_title else 'Not specified'}
                    Job Description: {job_description if job_description else 'Not provided'}
                    
                    Candidate's question/practice: {prompt}
                    
                    Provide helpful, constructive feedback and guidance. If they're practicing an answer, 
                    suggest improvements and alternative approaches. If they're asking about interview preparation,
                    give practical advice and tips.
                    """
                    
                    response = llm.invoke(context_prompt)
                    full_response = response.content
                else:
                    full_response = "⚠️ GROQ_API_KEY not configured. Please set up your API key in the .env file."
                    
            except Exception as e:
                full_response = f"❌ Error generating response: {str(e)}"
            
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Interview tips section
    st.subheader("💡 Quick Interview Tips")
    st.write("""
    - Research the company and role thoroughly
    - Prepare STAR method answers (Situation, Task, Action, Result)
    - Practice common behavioral questions
    - Have 2-3 thoughtful questions ready for the interviewer
    - Dress professionally and test your technology beforehand
    """)
