"""
Interview Report Generator
Generates comprehensive reports for mock interview sessions
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class InterviewReportGenerator:
    """Generates detailed interview reports with AI insights"""
    
    def __init__(self):
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
    
    def generate_comprehensive_report(self, 
                                    interview_session: Dict,
                                    job_description: str = "") -> Dict:
        """
        Generate a comprehensive interview report
        
        Args:
            interview_session: Session data with questions, responses, and analyses
            job_description: Job description for context
            
        Returns:
            Comprehensive report dictionary
        """
        report = {
            'session_info': self._generate_session_info(interview_session),
            'overall_performance': self._calculate_overall_performance(interview_session),
            'question_analysis': self._analyze_individual_questions(interview_session),
            'strengths_weaknesses': self._identify_strengths_weaknesses(interview_session),
            'ai_insights': self._generate_ai_insights(interview_session, job_description),
            'recommendations': self._generate_recommendations(interview_session),
            'improvement_plan': self._create_improvement_plan(interview_session)
        }
        
        return report
    
    def _generate_session_info(self, session: Dict) -> Dict:
        """Generate session information"""
        return {
            'total_questions': len(session.get('questions', [])),
            'completed_responses': len([r for r in session.get('responses', []) if r.strip()]),
            'session_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'average_response_length': self._calculate_average_response_length(session)
        }
    
    def _calculate_overall_performance(self, session: Dict) -> Dict:
        """Calculate overall performance metrics"""
        analyses = session.get('analyses', [])
        if not analyses:
            return {'overall_score': 0, 'grade': 'N/A', 'summary': 'No responses analyzed'}
        
        # Calculate average scores
        scores = []
        for analysis in analyses:
            if 'overall_score' in analysis and 'score' in analysis['overall_score']:
                scores.append(analysis['overall_score']['score'])
        
        if not scores:
            return {'overall_score': 0, 'grade': 'N/A', 'summary': 'No valid scores found'}
        
        avg_score = sum(scores) / len(scores)
        
        # Determine grade
        if avg_score >= 0.9:
            grade = 'A'
        elif avg_score >= 0.8:
            grade = 'B'
        elif avg_score >= 0.7:
            grade = 'C'
        elif avg_score >= 0.6:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'overall_score': avg_score,
            'grade': grade,
            'percentage': avg_score * 100,
            'summary': f"Overall performance: {grade} ({avg_score:.1%})"
        }
    
    def _analyze_individual_questions(self, session: Dict) -> List[Dict]:
        """Analyze individual question performance"""
        questions = session.get('questions', [])
        responses = session.get('responses', [])
        analyses = session.get('analyses', [])
        
        question_analysis = []
        
        for i, (question, response, analysis) in enumerate(zip(questions, responses, analyses)):
            if not response.strip():
                continue
                
            question_data = {
                'question_number': i + 1,
                'question': question,
                'response': response,
                'response_length': len(response.split()),
                'scores': {}
            }
            
            # Extract individual scores
            metrics = ['clarity', 'confidence', 'sentiment', 'keyword_match', 'fluency', 'relevance']
            for metric in metrics:
                if metric in analysis and 'score' in analysis[metric]:
                    question_data['scores'][metric] = analysis[metric]['score']
            
            # Overall score for this question
            if 'overall_score' in analysis:
                question_data['overall_score'] = analysis['overall_score'].get('score', 0)
                question_data['grade'] = analysis['overall_score'].get('grade', 'N/A')
            
            question_analysis.append(question_data)
        
        return question_analysis
    
    def _identify_strengths_weaknesses(self, session: Dict) -> Dict:
        """Identify strengths and weaknesses across all responses"""
        analyses = session.get('analyses', [])
        if not analyses:
            return {'strengths': [], 'weaknesses': []}
        
        # Aggregate scores by metric
        metric_scores = {}
        for analysis in analyses:
            for metric, data in analysis.items():
                if isinstance(data, dict) and 'score' in data:
                    if metric not in metric_scores:
                        metric_scores[metric] = []
                    metric_scores[metric].append(data['score'])
        
        # Calculate averages
        avg_scores = {}
        for metric, scores in metric_scores.items():
            avg_scores[metric] = sum(scores) / len(scores)
        
        # Identify strengths (scores > 0.7)
        strengths = []
        for metric, score in avg_scores.items():
            if score > 0.7:
                strengths.append(f"Strong {metric.replace('_', ' ')} ({(score*100):.1f}%)")
        
        # Identify weaknesses (scores < 0.6)
        weaknesses = []
        for metric, score in avg_scores.items():
            if score < 0.6:
                weaknesses.append(f"Needs improvement in {metric.replace('_', ' ')} ({(score*100):.1f}%)")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'average_scores': avg_scores
        }
    
    def _generate_ai_insights(self, session: Dict, job_description: str) -> str:
        """Generate AI-powered insights using LLM"""
        # Prepare context for LLM
        questions = session.get('questions', [])
        responses = session.get('responses', [])
        analyses = session.get('analyses', [])
        
        # Create context string
        context_parts = []
        for i, (question, response, analysis) in enumerate(zip(questions, responses, analyses)):
            if not response.strip():
                continue
                
            context_parts.append(f"Q{i+1}: {question}")
            context_parts.append(f"A{i+1}: {response}")
            
            # Add analysis scores
            if 'overall_score' in analysis:
                score = analysis['overall_score'].get('score', 0)
                grade = analysis['overall_score'].get('grade', 'N/A')
                context_parts.append(f"Score: {score:.1%} (Grade: {grade})")
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        prompt = f"""
You are an expert interview coach and career counselor. Analyze the following mock interview session and provide comprehensive insights.

Job Description Context:
{job_description}

Interview Session:
{context}

Please provide detailed insights covering:
1. Overall performance assessment
2. Communication effectiveness
3. Technical/domain knowledge demonstration
4. Areas of excellence
5. Critical improvement areas
6. Specific actionable advice for each weakness
7. Career development suggestions

Be specific, constructive, and actionable in your feedback. Focus on helping the candidate improve their interview skills and career prospects.
"""

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"AI insights generation failed: {str(e)}. Please review the analysis metrics manually."
    
    def _generate_recommendations(self, session: Dict) -> List[str]:
        """Generate specific recommendations based on performance"""
        recommendations = []
        
        # Analyze overall performance
        overall_perf = self._calculate_overall_performance(session)
        overall_score = overall_perf.get('overall_score', 0)
        
        if overall_score < 0.6:
            recommendations.append("Focus on fundamental interview skills - practice common questions")
            recommendations.append("Work on confidence and clarity in speech delivery")
        elif overall_score < 0.8:
            recommendations.append("Continue practicing to refine your interview skills")
            recommendations.append("Focus on specific weak areas identified in the analysis")
        else:
            recommendations.append("Excellent performance! Continue practicing to maintain skills")
            recommendations.append("Consider advanced interview techniques and leadership scenarios")
        
        # Specific recommendations based on weaknesses
        strengths_weaknesses = self._identify_strengths_weaknesses(session)
        for weakness in strengths_weaknesses.get('weaknesses', []):
            if 'clarity' in weakness.lower():
                recommendations.append("Practice speaking clearly and reduce filler words")
            elif 'confidence' in weakness.lower():
                recommendations.append("Work on vocal confidence and body language")
            elif 'relevance' in weakness.lower():
                recommendations.append("Study the job description and practice relevant examples")
        
        return recommendations
    
    def _create_improvement_plan(self, session: Dict) -> Dict:
        """Create a structured improvement plan"""
        plan = {
            'immediate_actions': [],
            'short_term_goals': [],
            'long_term_development': [],
            'practice_schedule': {}
        }
        
        # Immediate actions based on performance
        overall_perf = self._calculate_overall_performance(session)
        if overall_perf.get('overall_score', 0) < 0.7:
            plan['immediate_actions'].extend([
                "Practice basic interview questions daily",
                "Record yourself answering questions and review",
                "Work on reducing filler words and improving clarity"
            ])
        
        # Short-term goals
        plan['short_term_goals'].extend([
            "Complete 5 mock interviews in the next 2 weeks",
            "Practice with different question types (technical, behavioral)",
            "Improve specific weak areas identified in analysis"
        ])
        
        # Long-term development
        plan['long_term_development'].extend([
            "Develop industry-specific knowledge and examples",
            "Build a portfolio of relevant projects and achievements",
            "Practice advanced interview scenarios and leadership questions"
        ])
        
        # Practice schedule
        plan['practice_schedule'] = {
            'daily': "15 minutes of question practice",
            'weekly': "2-3 full mock interviews",
            'monthly': "Review and update your examples and stories"
        }
        
        return plan
    
    def _calculate_average_response_length(self, session: Dict) -> float:
        """Calculate average response length in words"""
        responses = session.get('responses', [])
        if not responses:
            return 0
        
        total_words = sum(len(response.split()) for response in responses if response.strip())
        return total_words / len([r for r in responses if r.strip()]) if responses else 0
    
    def generate_text_report(self, report_data: Dict) -> str:
        """Generate a formatted text report"""
        report_lines = []
        
        # Header
        report_lines.append("MOCK INTERVIEW ANALYSIS REPORT")
        report_lines.append("=" * 50)
        report_lines.append(f"Generated: {report_data['session_info']['session_date']}")
        report_lines.append("")
        
        # Overall Performance
        overall = report_data['overall_performance']
        report_lines.append("OVERALL PERFORMANCE")
        report_lines.append("-" * 20)
        report_lines.append(f"Overall Score: {overall['overall_score']:.1%}")
        report_lines.append(f"Grade: {overall['grade']}")
        report_lines.append(f"Summary: {overall['summary']}")
        report_lines.append("")
        
        # Individual Questions
        report_lines.append("QUESTION-BY-QUESTION ANALYSIS")
        report_lines.append("-" * 30)
        for qa in report_data['question_analysis']:
            report_lines.append(f"Question {qa['question_number']}: {qa['question'][:50]}...")
            report_lines.append(f"Response Length: {qa['response_length']} words")
            report_lines.append(f"Overall Score: {qa.get('overall_score', 0):.1%} (Grade: {qa.get('grade', 'N/A')})")
            
            for metric, score in qa['scores'].items():
                report_lines.append(f"  {metric.title()}: {score:.1%}")
            report_lines.append("")
        
        # Strengths and Weaknesses
        sw = report_data['strengths_weaknesses']
        report_lines.append("STRENGTHS")
        report_lines.append("-" * 10)
        for strength in sw['strengths']:
            report_lines.append(f"• {strength}")
        report_lines.append("")
        
        report_lines.append("AREAS FOR IMPROVEMENT")
        report_lines.append("-" * 20)
        for weakness in sw['weaknesses']:
            report_lines.append(f"• {weakness}")
        report_lines.append("")
        
        # AI Insights
        report_lines.append("AI-POWERED INSIGHTS")
        report_lines.append("-" * 20)
        report_lines.append(report_data['ai_insights'])
        report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 15)
        for i, rec in enumerate(report_data['recommendations'], 1):
            report_lines.append(f"{i}. {rec}")
        report_lines.append("")
        
        # Improvement Plan
        plan = report_data['improvement_plan']
        report_lines.append("IMPROVEMENT PLAN")
        report_lines.append("-" * 15)
        
        report_lines.append("Immediate Actions:")
        for action in plan['immediate_actions']:
            report_lines.append(f"• {action}")
        
        report_lines.append("\nShort-term Goals:")
        for goal in plan['short_term_goals']:
            report_lines.append(f"• {goal}")
        
        report_lines.append("\nLong-term Development:")
        for dev in plan['long_term_development']:
            report_lines.append(f"• {dev}")
        
        report_lines.append("\nPractice Schedule:")
        for period, activity in plan['practice_schedule'].items():
            report_lines.append(f"• {period.title()}: {activity}")
        
        return "\n".join(report_lines)
