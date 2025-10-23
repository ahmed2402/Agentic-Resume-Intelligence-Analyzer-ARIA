from prefect import flow, task
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ats import ATSAnalyzer
from core.utils import load_resume,clean_text

@task
def load_and_clean_resume(resume_path: str):
    """Loads resume text and cleans it."""
    print(f"Loading and cleaning resume from: {resume_path}")
    resume_text = load_resume(resume_path)
    resume_tokens = clean_text(resume_text)
    return resume_text, resume_tokens
@flow(name="ATS Analysis Flow", log_prints=True)
def ats_analysis_flow(resume_path: str, job_description: str = None):
    """
    Orchestrates the full ATS analysis by running individual checks as tasks.
    """
    analyzer = ATSAnalyzer()
    ats_criteria = analyzer.ats_criteria

    # 1. Load and preprocess resume
    resume_text, resume_tokens = load_and_clean_resume(resume_path)

    # 2. Run analysis tasks
    print("Running individual analysis tasks...")
    format_score = analyzer.check_format_compatibility(resume_text)
    keyword_score = analyzer.check_keyword_optimization(resume_text, resume_tokens, job_description)
    structure_score = analyzer.check_structure_quality(resume_text)
    content_score = analyzer.check_content_quality(resume_text, resume_tokens)

    # 3. Aggregate scores (this logic runs inside the flow)
    print("Aggregating scores...")
    category_scores_data = {
        'format_compatibility': format_score,
        'keyword_optimization': keyword_score,
        'structure_quality': structure_score,
        'content_quality': content_score
    }
    
    scores = {}
    total_score = 0
    for category, score in category_scores_data.items():
        config = ats_criteria[category]
        scores[category] = {
            'score': score,
            'weight': config['weight'],
            'weighted_score': score * config['weight']
        }
        total_score += scores[category]['weighted_score']

    # 4. Generate recommendations
    recommendations = analyzer.generate_recommendations(scores, resume_text)

    # 5. Compile final results
    result = {
        'overall_score': round(total_score * 100, 1),
        'category_scores': scores,
        'recommendations': recommendations,
    }
    
    print("ATS Analysis Complete:")
    print(f"Overall Score: {result['overall_score']}%")
    return result

if __name__ == "__main__":
    jd = """Job Title: AI Engineer Company Overview:
We are a forward-thinking technology company at the forefront of artificial intelligence innovation. Our mission is to develop cutting-edge AI solutions that transform industries and create meaningful impact. We're looking for a talented AI Engineer to join our dynamic team and help shape the future of AI.

Position Summary:
The AI Engineer will be responsible for designing, developing, and deploying machine learning models and AI systems. You will work closely with data scientists, software engineers, and product managers to create scalable AI solutions that solve complex business problems.

Key Responsibilities:
- Design, develop, and implement machine learning models and algorithms
- Build and maintain data pipelines for model training and deployment
- Optimize AI models for performance, scalability, and efficiency
- Collaborate with cross-functional teams to integrate AI solutions into production systems
- Conduct experiments and A/B testing to validate model performance
- Stay current with the latest advancements in AI/ML technologies and methodologies
- Document technical specifications and maintain code quality through best practices
- Troubleshoot and resolve issues in production AI systems

Required Qualifications:
- Bachelor's or Master's degree in Computer Science, Artificial Intelligence, Machine Learning, or related field
- 3+ years of experience in AI/ML engineering or related role
- Strong programming skills in Python and experience with ML frameworks (TensorFlow, PyTorch, scikit-learn)
- Experience with cloud platforms (AWS, GCP, or Azure) and containerization technologies
- Solid understanding of machine learning algorithms, deep learning, and neural networks
- Experience with data processing and ETL pipelines
- Familiarity with version control systems (Git) and CI/CD practices

Preferred Qualifications:
- Experience with natural language processing (NLP) and computer vision
- Knowledge of MLOps practices and tools
- Experience with distributed computing frameworks
- Publications or contributions to open-source AI projects
- Strong problem-solving skills and ability to work in a fast-paced environment

What We Offer:
- Competitive salary and equity package
- Comprehensive health benefits
- Flexible work arrangements
- Professional development opportunities
- State-of-the-art technology stack
- Collaborative and innovative work environment

Application Process:
Please submit your resume, cover letter, and any relevant project portfolios or GitHub repositories.

Equal Opportunity Employer:
We are committed to creating a diverse environment and are proud to be an equal opportunity employer. All qualified applicants will receive consideration for employment without regard to race, color, religion, gender, gender identity or expression, sexual orientation, national origin, genetics, disability, age, or veteran status.
"""
    ats_analysis_flow("../data/raw/resumes/Ahmed Raza - AI Engineer.pdf", jd)
