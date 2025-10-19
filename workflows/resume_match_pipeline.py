from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableParallel
from langchain_community.llms import Ollama
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

# Build the LangGraph
workflow = StateGraph(AgentState)

workflow.add_node("ingest", lambda state: {
    "raw_resume_text": ingestion_agent.ingest(state["resume_path"], state["jd_path"])["raw_resume_text"],
    "raw_jd_text": ingestion_agent.ingest(state["resume_path"], state["jd_path"])["raw_jd_text"],
    "cleaned_resume": ingestion_agent.ingest(state["resume_path"], state["jd_path"])["cleaned_resume"],
    "cleaned_jd": ingestion_agent.ingest(state["resume_path"], state["jd_path"])["cleaned_job_description"]
})
workflow.add_node("embed", lambda state: {"similarity_score": embedding_agent.process(state["cleaned_resume"], state["cleaned_jd"])})
workflow.add_node("advise", lambda state: advisor_agent.advise(state["raw_resume_text"], state["raw_jd_text"], state["similarity_score"]))
workflow.add_node("generate_pdf", lambda state: {"output_pdf_path": pdf_generator_agent.generate_cv(state["raw_resume_text"], state["raw_jd_text"])})

workflow.set_entry_point("ingest")
workflow.add_edge("ingest", "embed")
workflow.add_edge("ingest", "generate_pdf")
workflow.add_edge("embed", "advise")
workflow.add_edge("advise", END)
workflow.add_edge("generate_pdf", END)

app = workflow.compile()

if __name__ == "__main__":
    # Example Usage:
    RESUME_PATH = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
    JD_PATH = "../data/raw/job_descriptions/ai_engineer.txt"

    initial_state = {"resume_path": RESUME_PATH, "jd_path": JD_PATH}
    print("Running the Resume Match Pipeline...")
    for state in app.stream(initial_state):
        print(state)
        print("------")
    
    print("Pipeline finished.")
