from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.ingestion_agent import IngestionAgent
from agents.embedding_agent import EmbeddingAgent
from agents.advisor_agent import AdvisorAgent
from agents.pdf_generator_agent import PDFGeneratorAgent


class AgentState(TypedDict):
    """ The state of the agentic RAG workflow. """
    resume_path: str
    jd_path: str
    raw_resume_text: str
    raw_jd_text: str
    cleaned_resume: List[str]
    cleaned_jd: List[str]
    similarity_score: float
    insights: dict
    output_pdf_path: str
    # chat_history: Annotated[List[BaseMessage], operator.add]

# Initialize agents
ingestion_agent = IngestionAgent()
embedding_agent = EmbeddingAgent()
advisor_agent = AdvisorAgent()
pdf_generator_agent = PDFGeneratorAgent()


# --- Agent Nodes ---

def ingest_node(state: AgentState):
    """Call ingestion once and extract all required data."""
    print("Ingesting documents...")
    ingested_data = ingestion_agent.ingest(state["resume_path"], state["jd_path"])
    print("Documents ingested successfully.")
    return {
        "raw_resume_text": ingested_data["raw_resume_text"],
        "raw_jd_text": ingested_data["raw_jd_text"],
        "cleaned_resume": ingested_data["cleaned_resume"],
        "cleaned_jd": ingested_data["cleaned_job_description"]
    }

def embed_node(state: AgentState):
    """Calculate similarity score."""
    print("Generating embeddings and calculating similarity...")
    score = embedding_agent.process(state["cleaned_resume"], state["cleaned_jd"])
    print(f"Similarity score calculated: {score:.4f}")
    return {"similarity_score": score}

def advise_node(state: AgentState):
    """Generate AI-driven insights."""
    print("Generating AI-driven insights and suggestions...")
    insights = advisor_agent.advise(
        state["raw_resume_text"], 
        state["raw_jd_text"], 
        state["similarity_score"]
    )
    print("Insights generated successfully.")
    return insights # Returns a dict that updates the state, including 'insights' key

def generate_pdf_node(state: AgentState):
    """Generate the tailored CV PDF."""
    print("--- Tailored CV Document Creation Phase ---")
    # REMOVED 'font_path=FONT_PATH'
    pdf_path = pdf_generator_agent.generate_cv(state["raw_resume_text"], state["raw_jd_text"])
    print(f"Tailored CV PDF generated at: {pdf_path}")
    return {"output_pdf_path": pdf_path}


# --- Build the LangGraph ---

workflow = StateGraph(AgentState)

workflow.add_node("ingest", ingest_node)
workflow.add_node("embed", embed_node)
workflow.add_node("advise", advise_node)
workflow.add_node("generate_pdf", generate_pdf_node)

workflow.set_entry_point("ingest")

# Ingestion runs first
workflow.add_edge("ingest", "embed") 

# After embeddings, both advice and PDF generation can start
# We only need the score for advise, but for simplicity, run all final steps concurrently from 'embed'
workflow.add_edge("embed", "advise")
workflow.add_edge("ingest", "generate_pdf")

# The graph ends when all branches reach END
workflow.add_edge("advise", END)
workflow.add_edge("generate_pdf", END)

app = workflow.compile()

if __name__ == "__main__":

    RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
    JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"
    
    initial_state = {"resume_path": RESUME_PATH, "jd_path": JD_PATH}
    print("Running the Resume Match Pipeline...")
    
    # Run the pipeline and print the final state
    final_state = {}
    for state in app.stream(initial_state):
        final_state.update(state) # Accumulate the state changes
    
    print("\n--- FINAL RESULTS ---")
    print(f"1. Similarity Score: {final_state.get('similarity_score', 'N/A'):.4f}")
    
    # Print insights cleanly
    print("\n2. AI GENERATED INSIGHTS:")
    insights = final_state.get('insights', {})
    for section, content in insights.items():
        print(f"\n--- {section.replace('_', ' ').upper()} ---")
        print(content)
        
    print(f"\n3. Tailored CV Path: {final_state.get('output_pdf_path', 'N/A')}")
    print("Pipeline finished.")