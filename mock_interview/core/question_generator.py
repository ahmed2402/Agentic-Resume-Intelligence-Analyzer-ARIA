"""
Interview Question Generator
Generates relevant interview questions based on job description using LLM
"""

import os
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class QuestionGenerator:
    """Generates interview questions based on job description"""
    
    def __init__(self):
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
    
    def generate_questions(self, job_description: str, num_questions: int = 5, 
                          question_types: List[str] = None) -> List[Dict]:
        """
        Generate interview questions based on job description
        
        Args:
            job_description: The job description text
            num_questions: Number of questions to generate (default: 5)
            question_types: Types of questions to include (technical, behavioral, general)
            
        Returns:
            List of question dictionaries with text, type, and difficulty
        """
        if not question_types:
            question_types = ["technical", "behavioral", "general"]
        
        prompt = f"""
You are an expert interview coach and HR professional. Generate {num_questions} relevant interview questions based on the following job description.

Job Description:
{job_description}

Requirements:
1. Generate questions that are specifically relevant to this role and industry
2. Include a mix of question types: {', '.join(question_types)}
3. Questions should test both technical skills and soft skills relevant to the role
4. Include behavioral questions that relate to the job requirements
5. Make questions specific to the role, not generic
6. Vary the difficulty level (some easy, some challenging)
7. Focus on skills, experience, and competencies mentioned in the job description

Format your response as a JSON array where each question is an object with:
- "question": The interview question text
- "type": One of "technical", "behavioral", "general", or "situational"
- "difficulty": "easy", "medium", or "hard"
- "focus_area": Brief description of what this question tests
- "ideal_answer_keywords": List of key terms that should be mentioned in a good answer

Example format:
```json
[
  {{
    "question": "Tell me about your experience with [specific technology mentioned in JD]",
    "type": "technical",
    "difficulty": "medium",
    "focus_area": "Technical expertise in [technology]",
    "ideal_answer_keywords": ["experience", "projects", "challenges", "solutions"]
  }}
]
```

Generate exactly {num_questions} questions that are highly relevant to this specific job description.
"""

        try:
            response = self.llm.invoke(prompt)
            json_string = response.content.strip()
            
            # Extract JSON from markdown if present
            start_index = json_string.find("```json")
            end_index = json_string.find("```", start_index + len("```json"))
            
            if start_index != -1 and end_index != -1:
                json_string = json_string[start_index + len("```json\n"):end_index].strip()
            
            # Clean the JSON string
            cleaned_json_string = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', json_string)
            
            questions = json.loads(cleaned_json_string)
            
            # Validate and clean the questions
            validated_questions = []
            for q in questions:
                if isinstance(q, dict) and 'question' in q:
                    validated_questions.append({
                        'question': q.get('question', ''),
                        'type': q.get('type', 'general'),
                        'difficulty': q.get('difficulty', 'medium'),
                        'focus_area': q.get('focus_area', ''),
                        'ideal_answer_keywords': q.get('ideal_answer_keywords', [])
                    })
            
            return validated_questions[:num_questions]
            
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error in generate_questions: {e}")
            return self._get_fallback_questions(job_description, num_questions)
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions(job_description, num_questions)
    
    def _get_fallback_questions(self, job_description: str, num_questions: int) -> List[Dict]:
        """Fallback questions if LLM generation fails"""
        fallback_questions = [
            {
                "question": "Tell me about yourself and your relevant experience for this role.",
                "type": "general",
                "difficulty": "easy",
                "focus_area": "Self-introduction and experience",
                "ideal_answer_keywords": ["experience", "skills", "achievements", "background"]
            },
            {
                "question": "Why are you interested in this position?",
                "type": "general",
                "difficulty": "easy",
                "focus_area": "Motivation and interest",
                "ideal_answer_keywords": ["interest", "passion", "career goals", "company"]
            },
            {
                "question": "Describe a challenging project you worked on and how you overcame obstacles.",
                "type": "behavioral",
                "difficulty": "medium",
                "focus_area": "Problem-solving and project management",
                "ideal_answer_keywords": ["challenge", "solution", "teamwork", "results"]
            },
            {
                "question": "How do you stay updated with industry trends and new technologies?",
                "type": "technical",
                "difficulty": "medium",
                "focus_area": "Continuous learning and adaptability",
                "ideal_answer_keywords": ["learning", "training", "certifications", "industry"]
            },
            {
                "question": "Where do you see yourself in 5 years?",
                "type": "general",
                "difficulty": "easy",
                "focus_area": "Career planning and goals",
                "ideal_answer_keywords": ["goals", "growth", "career", "development"]
            }
        ]
        
        return fallback_questions[:num_questions]
    
    def generate_follow_up_questions(self, original_question: str, candidate_response: str) -> List[str]:
        """
        Generate follow-up questions based on candidate's response
        
        Args:
            original_question: The original interview question
            candidate_response: The candidate's response
            
        Returns:
            List of follow-up questions
        """
        prompt = f"""
You are an expert interviewer conducting a mock interview. Based on the candidate's response to the original question, generate 2-3 relevant follow-up questions that would help you better understand their experience and skills.

Original Question: {original_question}
Candidate's Response: {candidate_response}

Generate follow-up questions that:
1. Dig deeper into specific experiences mentioned
2. Ask for more details about technical aspects
3. Explore behavioral situations further
4. Test problem-solving abilities
5. Are natural conversation flow

Return as a JSON array of strings:
["Follow-up question 1", "Follow-up question 2", "Follow-up question 3"]
"""

        try:
            response = self.llm.invoke(prompt)
            json_string = response.content.strip()
            
            # Extract JSON from markdown if present
            start_index = json_string.find("```json")
            end_index = json_string.find("```", start_index + len("```json"))
            
            if start_index != -1 and end_index != -1:
                json_string = json_string[start_index + len("```json\n"):end_index].strip()
            
            # Clean the JSON string
            cleaned_json_string = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', json_string)
            
            follow_ups = json.loads(cleaned_json_string)
            return follow_ups if isinstance(follow_ups, list) else []
            
        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return [
                "Can you provide more details about that experience?",
                "How did you handle the challenges in that situation?",
                "What would you do differently if you faced a similar situation?"
            ]
