import re
import math
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge
import numpy as np
from core.utils import load_resume, clean_text

class ATSAnalyzer:
    """
    ATS (Applicant Tracking System) Score Calculator
    Analyzes resume compatibility with ATS systems and provides a score
    """
    
    def __init__(self):
        self.ats_criteria = {
            'format_compatibility': {
                'weight': 0.25,
                'checks': [
                    'has_standard_sections',
                    'no_tables_or_columns',
                    'no_graphics_or_images',
                    'standard_fonts',
                    'proper_file_format'
                ]
            },
            'keyword_optimization': {
                'weight': 0.30,
                'checks': [
                    'relevant_keywords',
                    'industry_terms',
                    'skill_keywords',
                    'action_verbs'
                ]
            },
            'structure_quality': {
                'weight': 0.25,
                'checks': [
                    'clear_contact_info',
                    'professional_summary',
                    'work_experience_format',
                    'education_section',
                    'skills_section'
                ]
            },
            'content_quality': {
                'weight': 0.20,
                'checks': [
                    'quantified_achievements',
                    'consistent_formatting',
                    'no_grammar_errors',
                    'appropriate_length',
                    'professional_tone'
                ]
            }
        }
    
    def calculate_ats_score(self, resume_path: str, job_description: str = None) -> Dict:
        """
        Calculate comprehensive ATS score for a resume
        
        Args:
            resume_path: Path to the resume file
            job_description: Optional job description for keyword matching
            
        Returns:
            Dictionary containing score breakdown and recommendations
        """
        try:
            # Load and process resume
            resume_text = load_resume(resume_path)
            resume_tokens = clean_text(resume_text)
            
            # Calculate scores for each category
            scores = {}
            total_score = 0
            
            for category, config in self.ats_criteria.items():
                category_score = self._calculate_category_score(
                    category, resume_text, resume_tokens, job_description
                )
                scores[category] = {
                    'score': category_score,
                    'weight': config['weight'],
                    'weighted_score': category_score * config['weight']
                }
                total_score += scores[category]['weighted_score']
            
            # Generate recommendations
            recommendations = self._generate_recommendations(scores, resume_text)
            
            return {
                'overall_score': round(total_score * 100, 1),
                'category_scores': scores,
                'recommendations': recommendations,
                'resume_text': resume_text
            }
            
        except Exception as e:
            return {
                'overall_score': 0,
                'error': str(e),
                'category_scores': {},
                'recommendations': ['Error processing resume. Please check file format.']
            }
    
    def _calculate_category_score(self, category: str, resume_text: str, 
                                resume_tokens: List[str], job_description: str = None) -> float:
        """Calculate score for a specific ATS category"""
        
        if category == 'format_compatibility':
            return self._check_format_compatibility(resume_text)
        elif category == 'keyword_optimization':
            return self._check_keyword_optimization(resume_text, resume_tokens, job_description)
        elif category == 'structure_quality':
            return self._check_structure_quality(resume_text)
        elif category == 'content_quality':
            return self._check_content_quality(resume_text, resume_tokens)
        
        return 0.0
    
    def _check_format_compatibility(self, resume_text: str) -> float:
        """Check resume format compatibility with ATS systems"""
        score = 0.0
        checks = 0
        
        # Check for standard sections
        standard_sections = ['experience', 'education', 'skills', 'summary', 'objective']
        found_sections = sum(1 for section in standard_sections 
                           if section.lower() in resume_text.lower())
        score += (found_sections / len(standard_sections)) * 0.3
        checks += 1
        
        # Check for problematic elements
        problematic_patterns = [
            r'<table>', r'<img>', r'<graphic>', r'<image>',
            r'columns?', r'table', r'graphic', r'image'
        ]
        
        has_problematic = any(re.search(pattern, resume_text.lower()) 
                            for pattern in problematic_patterns)
        if not has_problematic:
            score += 0.3
        checks += 1
        
        # Check for standard fonts (basic check)
        font_patterns = [r'arial', r'times', r'calibri', r'helvetica']
        has_standard_font = any(re.search(pattern, resume_text.lower()) 
                              for pattern in font_patterns)
        if has_standard_font or not re.search(r'font', resume_text.lower()):
            score += 0.2
        checks += 1
        
        # Check file format (assuming PDF is good)
        score += 0.2  # PDF is ATS-friendly
        checks += 1
        
        return min(score, 1.0)
    
    def _check_keyword_optimization(self, resume_text: str, resume_tokens: List[str], 
                                  job_description: str = None) -> float:
        """Check keyword optimization"""
        score = 0.0
        
        # Common industry keywords
        industry_keywords = [
            'python', 'machine learning', 'ai', 'data analysis', 'sql',
            'javascript', 'react', 'node', 'api', 'database', 'cloud',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'agile'
        ]
        
        found_keywords = sum(1 for keyword in industry_keywords 
                           if keyword.lower() in resume_text.lower())
        score += min(found_keywords / 10, 1.0) * 0.4
        
        # Action verbs
        action_verbs = [
            'developed', 'implemented', 'managed', 'led', 'created',
            'designed', 'built', 'optimized', 'improved', 'delivered'
        ]
        
        found_verbs = sum(1 for verb in action_verbs 
                         if verb.lower() in resume_text.lower())
        score += min(found_verbs / 5, 1.0) * 0.3
        
        # Job description keyword matching
        if job_description:
            jd_tokens = clean_text(job_description)
            common_tokens = set(resume_tokens) & set(jd_tokens)
            if len(jd_tokens) > 0:
                keyword_match_ratio = len(common_tokens) / len(jd_tokens)
                score += min(keyword_match_ratio * 2, 1.0) * 0.3
        else:
            score += 0.3  # Default score if no job description
        
        return min(score, 1.0)
    
    def _check_structure_quality(self, resume_text: str) -> float:
        """Check resume structure quality"""
        score = 0.0
        
        # Check for contact information
        contact_patterns = [
            r'@\w+\.\w+',  # Email
            r'\(\d{3}\)\s*\d{3}-\d{4}',  # Phone
            r'\d{3}-\d{3}-\d{4}',  # Phone alternative
            r'linkedin\.com',  # LinkedIn
            r'github\.com'  # GitHub
        ]
        
        contact_found = sum(1 for pattern in contact_patterns 
                          if re.search(pattern, resume_text.lower()))
        score += min(contact_found / 3, 1.0) * 0.25
        
        # Check for professional summary
        summary_keywords = ['summary', 'profile', 'objective', 'about']
        has_summary = any(keyword in resume_text.lower() for keyword in summary_keywords)
        if has_summary:
            score += 0.2
        
        # Check for work experience section
        experience_keywords = ['experience', 'employment', 'work history', 'career']
        has_experience = any(keyword in resume_text.lower() for keyword in experience_keywords)
        if has_experience:
            score += 0.2
        
        # Check for education section
        education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master']
        has_education = any(keyword in resume_text.lower() for keyword in education_keywords)
        if has_education:
            score += 0.2
        
        # Check for skills section
        skills_keywords = ['skills', 'technical skills', 'competencies', 'expertise']
        has_skills = any(keyword in resume_text.lower() for keyword in skills_keywords)
        if has_skills:
            score += 0.15
        
        return min(score, 1.0)
    
    def _check_content_quality(self, resume_text: str, resume_tokens: List[str]) -> float:
        """Check content quality"""
        score = 0.0
        
        # Check for quantified achievements
        quantified_patterns = [
            r'\d+%', r'\$\d+', r'\d+x', r'\d+\+', r'\d+ years?',
            r'increased by \d+', r'reduced by \d+', r'improved by \d+'
        ]
        
        quantified_found = sum(1 for pattern in quantified_patterns 
                             if re.search(pattern, resume_text.lower()))
        score += min(quantified_found / 3, 1.0) * 0.3
        
        # Check resume length (not too short, not too long)
        word_count = len(resume_tokens)
        if 200 <= word_count <= 800:
            score += 0.3
        elif 100 <= word_count < 200 or 800 < word_count <= 1200:
            score += 0.15
        
        # Check for consistent formatting (basic check)
        lines = resume_text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        if len(non_empty_lines) > 10:  # Reasonable number of sections
            score += 0.2
        
        # Check for professional tone (basic keyword check)
        professional_keywords = ['achieved', 'developed', 'implemented', 'managed', 'led']
        professional_found = sum(1 for keyword in professional_keywords 
                               if keyword.lower() in resume_text.lower())
        score += min(professional_found / 3, 1.0) * 0.2
        
        return min(score, 1.0)
    
    def _generate_recommendations(self, scores: Dict, resume_text: str) -> List[str]:
        """Generate improvement recommendations based on scores"""
        recommendations = []
        
        for category, data in scores.items():
            score = data['score']
            
            if category == 'format_compatibility' and score < 0.7:
                recommendations.append("Improve format compatibility: Use standard fonts, avoid tables/graphics, ensure proper file format")
            
            elif category == 'keyword_optimization' and score < 0.7:
                recommendations.append("Optimize keywords: Include more industry-specific terms and action verbs")
            
            elif category == 'structure_quality' and score < 0.7:
                recommendations.append("Improve structure: Ensure all standard sections (contact, summary, experience, education, skills) are present")
            
            elif category == 'content_quality' and score < 0.7:
                recommendations.append("Enhance content: Add quantified achievements and maintain professional tone")
        
        if not recommendations:
            recommendations.append("Great job! Your resume has good ATS compatibility.")
        
        return recommendations

def create_ats_score_circle(score: float, save_path: str = None) -> str:
    """
    Create a circular percentage display for ATS score
    
    Args:
        score: ATS score (0-100)
        save_path: Optional path to save the image
        
    Returns:
        Path to saved image or displays the plot
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect('equal')
    
    # Remove axes
    ax.axis('off')
    
    # Define colors based on score
    if score >= 80:
        color = '#2E8B57'  # Sea Green
        bg_color = '#E8F5E8'
    elif score >= 60:
        color = '#FF8C00'  # Dark Orange
        bg_color = '#FFF8E8'
    else:
        color = '#DC143C'  # Crimson
        bg_color = '#FFE8E8'
    
    # Create background circle
    background_circle = Circle((0, 0), 1, color=bg_color, alpha=0.3)
    ax.add_patch(background_circle)
    
    # Create progress circle
    theta = np.linspace(0, 2 * np.pi * (score / 100), 1000)
    x = np.cos(theta)
    y = np.sin(theta)
    
    # Plot the progress arc
    ax.plot(x, y, color=color, linewidth=20, alpha=0.8)
    
    # Add score text
    ax.text(0, 0.1, f'{score:.1f}%', fontsize=48, fontweight='bold', 
            ha='center', va='center', color=color)
    ax.text(0, -0.2, 'ATS Score', fontsize=20, fontweight='normal', 
            ha='center', va='center', color='#333333')
    
    # Add title
    ax.text(0, 1.3, 'Resume ATS Compatibility', fontsize=24, fontweight='bold', 
            ha='center', va='center', color='#333333')
    
    # Add score interpretation
    if score >= 80:
        interpretation = "Excellent ATS Compatibility"
    elif score >= 60:
        interpretation = "Good ATS Compatibility"
    else:
        interpretation = "Needs Improvement"
    
    ax.text(0, -0.4, interpretation, fontsize=16, fontweight='normal', 
            ha='center', va='center', color=color)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        return save_path
    else:
        plt.show()
        return ""

# Example usage and testing
if __name__ == "__main__":
    # Initialize ATS analyzer
    ats_analyzer = ATSAnalyzer()
    
    # Example resume path (update with your actual path)
    resume_path = "../data/raw/resumes/Ahmed Raza - AI Engineer.pdf"
    
    try:
        # Calculate ATS score
        result = ats_analyzer.calculate_ats_score(resume_path)
        
        print("=== ATS Score Analysis ===")
        print(f"Overall ATS Score: {result['overall_score']}%")
        print("\nCategory Breakdown:")
        
        for category, data in result['category_scores'].items():
            print(f"  {category.replace('_', ' ').title()}: {data['score']:.1%} "
                  f"(Weight: {data['weight']:.1%})")
        
        print("\nRecommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        # Create and save circular score display
        score_circle_path = create_ats_score_circle(
            result['overall_score'], 
            "ats_score_circle.png"
        )
        print(f"\nScore visualization saved to: {score_circle_path}")
        
    except Exception as e:
        print(f"Error: {e}")