#!/usr/bin/env python3
"""
ATS Score Calculator Script
Usage: python agents/ats_agent.py <resume_path> [job_description_path]
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.ats import ATSAnalyzer, create_ats_score_circle
from core.utils import load_job_description

class ATSAgent:
    """
    Thin agent wrapper around core ATS analyzer for use in workflows.
    """
    def __init__(self):
        self._analyzer = ATSAnalyzer()

    def analyze(self, resume_path: str, job_description_text: str | None = None) -> dict:
        """
        Analyze a resume for ATS compatibility.

        Args:
            resume_path: Path to the resume file.
            job_description_text: Optional raw JD text to inform keyword checks.

        Returns:
            Dict with overall_score, category_scores, recommendations, and resume_text.
        """
        return self._analyzer.calculate_ats_score(resume_path, job_description_text)

def main():
    if len(sys.argv) < 2:
        print("Usage: python agents/ats_agent.py <resume_path> [job_description_path]")
        print("Example: python agents/ats_agent.py data/raw/resumes/resume.pdf data/raw/job_descriptions/job.txt")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    job_description_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate resume path
    if not os.path.exists(resume_path):
        print(f"Error: Resume file not found at {resume_path}")
        sys.exit(1)
    
    # Load job description if provided
    job_description = None
    if job_description_path:
        if not os.path.exists(job_description_path):
            print(f"Warning: Job description file not found at {job_description_path}")
        else:
            job_description = load_job_description(job_description_path)
    
    # Initialize ATS analyzer
    ats_analyzer = ATSAnalyzer()
    
    print("🔍 Analyzing resume for ATS compatibility...")
    print(f"📄 Resume: {resume_path}")
    if job_description:
        print(f"📋 Job Description: {job_description_path}")
    print("-" * 50)
    
    try:
        # Calculate ATS score
        result = ats_analyzer.calculate_ats_score(resume_path, job_description)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        # Display results
        print(f"🎯 Overall ATS Score: {result['overall_score']}%")
        print("\n📊 Category Breakdown:")
        
        for category, data in result['category_scores'].items():
            category_name = category.replace('_', ' ').title()
            score_percent = data['score'] * 100
            weight_percent = data['weight'] * 100
            print(f"  • {category_name}: {score_percent:.1f}% (Weight: {weight_percent:.0f}%)")
        
        print("\n💡 Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        # Create circular score visualization
        output_path = f"ats_score_{Path(resume_path).stem}.png"
        create_ats_score_circle(result['overall_score'], output_path)
        print(f"\n📈 Score visualization saved to: {output_path}")
        
        # Determine overall assessment
        score = result['overall_score']
        if score >= 80:
            print("\n✅ Excellent! Your resume has great ATS compatibility.")
        elif score >= 60:
            print("\n⚠️  Good, but there's room for improvement.")
        else:
            print("\n❌ Your resume needs significant improvements for ATS compatibility.")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()