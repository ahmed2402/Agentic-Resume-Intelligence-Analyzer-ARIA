import os
import sys
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# --- CONFIGURABLE PARAMETERS ---
DOMAINS = ["Software Engineering", "Data Science", "Machine Learning", "DevOps", "Cloud Computing", "Cybersecurity", "Database Management", "Web Development", "Mobile Development", "AI Ethics", "Product Management", "UX/UI Design", "Blockchain", "Quantum Computing", "Game Development"]
TOPICS_BY_DOMAIN = {
    "Software Engineering": ["Data Structures", "Algorithms", "OOP", "System Design", "Design Patterns", "Testing", "API Design", "Microservices", "Refactoring", "Code Review"],
    "Data Science": ["Statistics", "Data Visualization", "Preprocessing", "Feature Engineering", "Time Series Analysis", "Big Data", "Data Warehousing", "ETL Processes", "Predictive Modeling", "A/B Testing"],
    "Machine Learning": ["Supervised Learning", "Unsupervised Learning", "Model Evaluation", "Deep Learning", "Natural Language Processing", "Computer Vision", "Reinforcement Learning", "Transfer Learning", "Ensemble Methods", "Hyperparameter Tuning"],
    "DevOps": ["CI/CD", "Containerization", "Infrastructure as Code", "Monitoring", "Automation", "Deployment Strategies", "Configuration Management", "Performance Optimization", "Disaster Recovery", "GitOps"],
    "Cloud Computing": ["AWS", "Azure", "GCP", "Cloud Architecture", "Serverless", "Storage Solutions", "Networking", "Security & Compliance", "Cost Optimization", "Multi-cloud Strategies"],
    "Cybersecurity": ["Network Security", "Application Security", "Cryptography", "Threat Detection", "Incident Response", "Compliance", "Penetration Testing", "Security Auditing", "Identity & Access Management", "Zero Trust Architecture"],
    "Database Management": ["SQL", "NoSQL", "Database Design", "Query Optimization", "Transactions", "Indexing", "Replication", "Backup & Recovery", "Data Modeling", "极速数据库"],
    "Web Development": ["Frontend Frameworks", "Backend Development", "REST APIs", "GraphQL", "极速安全", "Performance Optimization", "Progressive Web Apps", "Single Page Applications", "Web Accessibility", "SEO"],
    "Mobile Development": ["iOS Development", "Android Development", "Cross-platform Frameworks", "Mobile UI/UX", "App Performance", "Push Notifications", "In-app Purchases", "Offline Functionality", "App Store Optimization", "Mobile Security"],
    "AI Ethics": ["Bias & Fairness", "Privacy & Data Protection", "Transparency & Explainability", "Accountability", "Social Impact", "Regulatory Compliance", "Ethical Decision Making", "AI Governance", "Human-AI Collaboration", "Responsible AI Development"],
    "Product Management": ["Product Strategy", "Roadmapping", "User Research", "Market Analysis", "Prioritization", "Metrics & Analytics", "Stakeholder Management", "Agile Methodologies", "Go-to-Market Strategy", "Product Lifecycle"],
    "UX/UI Design": ["User Research", "Wireframing", "Prototyping", "Usability Testing", "Information Architecture", "Interaction Design", "Visual Design", "Design Systems", "Accessibility", "Design Thinking"],
    "Blockchain": ["Smart Contracts", "Cryptocurrencies", "Distributed Ledgers", "Consensus Mechanisms", "DeFi", "NFTs", "Tokenomics", "Blockchain Security", "Scalability Solutions", "Web3 Development"],
    "Quantum Computing": ["Quantum Algorithms", "Qubits & Gates", "Quantum Supremacy", "Quantum Error Correction", "Quantum Cryptography", "Quantum Machine Learning", "Quantum Hardware", "Quantum Simulation", "Quantum Complexity", "Quantum Applications"],
    "Game Development": ["Game Design", "Game Engines", "Physics Simulation", "AI in Games", "Multiplayer Networking", "Graphics Programming", "Sound Design", "Level Design", "Game Monetization", "VR/AR Development"]
}
DIFFICULTIES = ["Easy", "Medium", "Hard"]
N_QUESTIONS_PER_TOPIC = 5
OUTPUT_DIR = "./interview_prep_kb"
OUTPUT_FILENAME = "interview_prep_mock_data.json"
MODEL_NAME = "llama-3.1-8b-instant"

# --- LLM Setup ---
load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found. Please set in .env file.")
llm = ChatGroq(groq_api_key=groq_api_key, model_name=MODEL_NAME)

# --- Prompt Template ---
LLM_PROMPT = '''
Generate {n} independent mock interview questions (with answers) for the following settings, each as a JSON object in a list. Use this schema:
{{
  "id": "q#",  
  "domain": "<domain>",
  "topic": "<topic>",
  "difficulty": "<difficulty>",
  "question": "...",
  "answer": "..."
}}

Instructions:
- Avoid duplicates and trivial variations.
- Vary the question style (conceptual, scenario, code, etc).
- Questions and answers should be clear, concise, and technically accurate.
- Each question must have a different id.

Domain: {domain}
Topic: {topic}
Difficulty: {difficulty}
Number: {n}
Respond ONLY with a JSON array of the objects, no markdown/title.
'''

def generate_qas(domain, topic, difficulty, n=2):
    prompt = LLM_PROMPT.format(domain=domain, topic=topic, difficulty=difficulty, n=n)
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        # Some LLMs may return markdown code block; clean it up (if exists)
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        data = json.loads(content)
        # Patch missing IDs if LLM skips them
        for idx, item in enumerate(data):
            item.setdefault("id", f"{domain[:2]}_{topic[:2]}_{difficulty[0]}_{idx+1}")
        return data
    except Exception as e:
        print(f"Failed to generate questions for {domain}/{topic}/{difficulty}: {e}")
        return []

def safe_filename(s: str) -> str:
    return s.replace(' ', '_').replace('/', '_').replace('\\', '_')

def main():
    total_qas = 0
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for domain in DOMAINS:
        topics = TOPICS_BY_DOMAIN.get(domain, [])
        safe_domain = safe_filename(domain)
        for topic in topics:
            safe_topic = safe_filename(topic)
            domain_topic_qas = []
            for difficulty in DIFFICULTIES:
                qas = generate_qas(domain, topic, difficulty, N_QUESTIONS_PER_TOPIC)
                domain_topic_qas.extend(qas)
            output_filename = f"{safe_domain}__{safe_topic}.json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(domain_topic_qas, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(domain_topic_qas)} Q&A to {output_path}")
            total_qas += len(domain_topic_qas)
    print(f"Total Q&A generated/saved: {total_qas}")

if __name__ == "__main__":
    main()
