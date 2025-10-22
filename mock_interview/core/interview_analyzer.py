"""
Interview Analysis Engine for Mock Interview Analyzer
Analyzes speech for clarity, confidence, sentiment, and keyword matching
"""
import json
import os
from langchain_groq import ChatGroq
import re
import numpy as np
from typing import Dict, List, Tuple, Optional
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found. Please set in .env file.")
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")
# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class InterviewAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))

    def analyze_response(self, 
            transcript: str, 
            question: str = "",
            ideal_answer: str = "", 
            audio_features: Dict = None,
            job_description: str = "") -> Dict:
        """
        LLM-based analysis of interview response using Groq
        """
          # Make sure groq is installed and your API key is set
        prompt = f"""
You are an expert interview evaluator. Analyze the following response and provide scores (0-1) for:
- Clarity
- Confidence
- Fluency
- Relevance
- Sentiment (positive/neutral/negative)
- Keyword Match (to job description)
Return your analysis as a JSON object with keys: clarity, confidence, fluency, relevance, sentiment, keyword_match. Each should have a 'score' (0-1) and 'details'.

Interview Question: {question}
Job Description: {job_description}
Candidate Response: {transcript}
        """

        response = llm.invoke(prompt)
        print("Raw LLM response from InterviewAnalyzer:", response.content) # More specific debug print
    
        json_string = response.content.strip()
        start_index = json_string.find("```json")
        end_index = json_string.find("```", start_index + len("```json"))

        if start_index != -1 and end_index != -1:
            json_string = json_string[start_index + len("```json\n") : end_index].strip()
            print("Extracted JSON string (markdown block):", json_string) # Debug print
        else:
            print("Warning: JSON markdown block not found in interview_analyzer.py. Attempting to parse raw response as is.")
            print("Raw response being parsed as JSON:", json_string) # Debug print for fallback
        
        # Clean control characters before parsing
        cleaned_json_string = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', json_string)
        print("Cleaned JSON string before json.loads():", cleaned_json_string) # CRITICAL debug print
        
        analysis = json.loads(cleaned_json_string)
        # Calculate overall score as before
        analysis['overall_score'] = self._calculate_overall_score(analysis)
        return analysis

    def _analyze_clarity(self, text: str) -> Dict:
        """Analyze clarity of speech"""
        if not text or text.strip() == "":
            return {'score': 0, 'details': 'No speech detected'}
        # Remove filler words and analyze
        filler_words = ['um', 'uh', 'like', 'you know', 'so', 'well', 'actually']
        words = text.lower().split()
        filler_count = sum(1 for word in words if word in filler_words)
        total_words = len(words)
        filler_ratio = filler_count / total_words if total_words > 0 else 0
        # Sentence structure analysis
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        # Clarity score (0-1, higher is better)
        clarity_score = max(0, 1 - (filler_ratio * 2) - (0.1 if avg_sentence_length < 5 else 0))
        return {
            'score': min(1, max(0, clarity_score)),
            'filler_ratio': filler_ratio,
            'avg_sentence_length': avg_sentence_length,
            'details': f"Filler words: {filler_count}/{total_words} ({filler_ratio:.1%})"
        }

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the response"""
        if not text or text.strip() == "":
            return {'score': 0, 'label': 'neutral', 'details': 'No speech detected'}
        # Using TextBlob for sentiment
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        # Using VADER for more nuanced sentiment
        vader_scores = self.sia.polarity_scores(text)
        # Convert to 0-1 scale
        sentiment_score = (polarity + 1) / 2
        # Determine label
        if sentiment_score > 0.6:
            label = 'positive'
        elif sentiment_score < 0.4:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'score': sentiment_score,
            'label': label,
            'polarity': polarity,
            'vader_scores': vader_scores,
            'details': f"Sentiment: {label} (polarity: {polarity:.2f})"
        }
    
    def _analyze_keyword_match(self, transcript: str, ideal_answer: str) -> Dict:
        """Analyze keyword matching with ideal answer"""
        if not ideal_answer or not transcript:
            return {'score': 0.5, 'details': 'No ideal answer provided for comparison'}
        
        # Extract keywords from both texts
        transcript_words = set(word.lower() for word in word_tokenize(transcript) 
                             if word.isalpha() and word.lower() not in self.stop_words)
        ideal_words = set(word.lower() for word in word_tokenize(ideal_answer) 
                         if word.isalpha() and word.lower() not in self.stop_words)
        
        if not ideal_words:
            return {'score': 0.5, 'details': 'No meaningful keywords in ideal answer'}
        
        # Calculate overlap
        common_words = transcript_words.intersection(ideal_words)
        keyword_score = len(common_words) / len(ideal_words)
        
        return {
            'score': min(1, keyword_score),
            'matched_keywords': list(common_words),
            'total_ideal_keywords': len(ideal_words),
            'details': f"Matched {len(common_words)}/{len(ideal_words)} keywords"
        }
    
    def _analyze_fluency(self, text: str) -> Dict:
        """Analyze fluency and coherence"""
        if not text or text.strip() == "":
            return {'score': 0, 'details': 'No speech detected'}
        
        # Check for repetition
        words = text.lower().split()
        unique_words = set(words)
        repetition_ratio = 1 - (len(unique_words) / len(words)) if words else 0
        
        # Check for sentence completeness
        sentences = re.split(r'[.!?]+', text)
        complete_sentences = [s for s in sentences if len(s.strip().split()) > 3]
        completeness_ratio = len(complete_sentences) / len(sentences) if sentences else 0
        
        # Fluency score
        fluency_score = (1 - repetition_ratio) * completeness_ratio
        
        return {
            'score': min(1, max(0, fluency_score)),
            'repetition_ratio': repetition_ratio,
            'completeness_ratio': completeness_ratio,
            'details': f"Fluency: {fluency_score:.2f} (repetition: {repetition_ratio:.1%})"
        }
    
    def _analyze_confidence(self, audio_features: Dict) -> Dict:
        """Analyze confidence based on audio features"""
        if not audio_features:
            return {'score': 0.5, 'details': 'No audio data available'}
        
        # Factors that indicate confidence
        volume_score = min(1, audio_features.get('volume', 0) / 0.1)  # Normalize volume
        pause_penalty = min(0.3, audio_features.get('pause_count', 0) * 0.05)
        silence_penalty = audio_features.get('silence_ratio', 0) * 0.2
        
        # Pitch variation can indicate confidence (some variation is good)
        pitch_variation = audio_features.get('pitch_variation', 0)
        pitch_score = min(1, max(0, 1 - abs(pitch_variation - 0.1) * 5))
        
        confidence_score = (volume_score + pitch_score) / 2 - pause_penalty - silence_penalty
        
        return {
            'score': min(1, max(0, confidence_score)),
            'volume_score': volume_score,
            'pitch_score': pitch_score,
            'details': f"Confidence: {confidence_score:.2f} (volume: {volume_score:.2f})"
        }
    
    def _analyze_speech_quality(self, audio_features: Dict) -> Dict:
        """Analyze overall speech quality"""
        if not audio_features:
            return {'score': 0.5, 'details': 'No audio data available'}
        
        # Speech rate analysis
        speech_rate = audio_features.get('speech_rate', 0)
        rate_score = 1 - abs(speech_rate - 150) / 150 if speech_rate > 0 else 0.5  # Optimal ~150 WPM
        
        # Silence ratio (less silence is better)
        silence_ratio = audio_features.get('silence_ratio', 0)
        silence_score = 1 - silence_ratio
        
        # Volume consistency
        volume_std = audio_features.get('volume_std', 0)
        consistency_score = 1 - min(1, volume_std * 10)
        
        quality_score = (rate_score + silence_score + consistency_score) / 3
        
        return {
            'score': min(1, max(0, quality_score)),
            'rate_score': rate_score,
            'silence_score': silence_score,
            'consistency_score': consistency_score,
            'details': f"Quality: {quality_score:.2f} (rate: {speech_rate:.1f} WPM)"
        }
    
    def _calculate_overall_score(self, analysis: Dict) -> Dict:
        """Calculate overall interview score"""
        scores = []
        
        # Weighted scoring
        weights = {
            'clarity': 0.20,
            'confidence': 0.20,
            'sentiment': 0.10,
            'keyword_match': 0.15,
            'fluency': 0.15,
            'relevance': 0.20
        }
        
        for metric, weight in weights.items():
            if metric in analysis and 'score' in analysis[metric]:
                score_val = analysis[metric]['score']
                if isinstance(score_val, (int, float)):
                    scores.append(score_val * weight)
        
        overall_score = sum(scores) if scores else 0
        
        # Grade assignment
        if overall_score >= 0.9:
            grade = 'A'
        elif overall_score >= 0.8:
            grade = 'B'
        elif overall_score >= 0.7:
            grade = 'C'
        elif overall_score >= 0.6:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'score': overall_score,
            'grade': grade,
            'percentage': overall_score * 100,
            'details': f"Overall: {grade} ({overall_score:.1%})"
        }
    
    def generate_feedback(self, analysis: Dict) -> str:
        """Generate detailed feedback based on analysis"""
        feedback = []
        
        # Clarity feedback
        clarity = analysis.get('clarity', {})
        clarity_score = clarity.get('score', 0)
        if isinstance(clarity_score, (int, float)):
            if clarity_score < 0.6:
                feedback.append("• Reduce filler words (um, uh, like) for better clarity")
            elif clarity_score > 0.8:
                feedback.append("• Excellent clarity and articulation")

        # Confidence feedback
        confidence = analysis.get('confidence', {})
        confidence_score = confidence.get('score', 0)
        if isinstance(confidence_score, (int, float)):
            if confidence_score < 0.6:
                feedback.append("• Speak with more confidence and volume")
            elif confidence_score > 0.8:
                feedback.append("• Great confidence in delivery")

        # Sentiment feedback
        sentiment = analysis.get('sentiment', {})
        if sentiment.get('label') == 'negative':
            feedback.append("• Maintain a more positive tone")
        elif sentiment.get('label') == 'positive':
            feedback.append("• Good positive attitude")

        # Keyword match feedback
        keyword_match = analysis.get('keyword_match', {})
        keyword_score = keyword_match.get('score', 0)
        if isinstance(keyword_score, (int, float)):
            if keyword_score < 0.5:
                feedback.append("• Include more relevant keywords from the job description")
            elif keyword_score > 0.7:
                feedback.append("• Excellent use of relevant keywords")

        # Fluency feedback
        fluency = analysis.get('fluency', {})
        fluency_score = fluency.get('score', 0)
        if isinstance(fluency_score, (int, float)):
            if fluency_score < 0.6:
                feedback.append("• Practice speaking more fluently and coherently")
            elif fluency_score > 0.8:
                feedback.append("• Very fluent and coherent delivery")
        
        return "\n".join(feedback) if feedback else "• Good overall performance"
    
    def _analyze_relevance(self, transcript: str, question: str, job_description: str) -> Dict:
        """Analyze how relevant the response is to the question and job"""
        if not transcript or not question:
            return {'score': 0.5, 'details': 'Insufficient data for relevance analysis'}
        
        # Extract keywords from question and job description
        question_words = set(word.lower() for word in word_tokenize(question) 
                           if word.isalpha() and word.lower() not in self.stop_words)
        
        job_words = set()
        if job_description:
            job_words = set(word.lower() for word in word_tokenize(job_description) 
                          if word.isalpha() and word.lower() not in self.stop_words)
        
        transcript_words = set(word.lower() for word in word_tokenize(transcript) 
                             if word.isalpha() and word.lower() not in self.stop_words)
        
        # Calculate relevance scores
        question_relevance = 0
        if question_words:
            question_overlap = transcript_words.intersection(question_words)
            question_relevance = len(question_overlap) / len(question_words)
        
        job_relevance = 0
        if job_words:
            job_overlap = transcript_words.intersection(job_words)
            job_relevance = len(job_overlap) / len(job_words)
        
        # Combined relevance score
        relevance_score = (question_relevance * 0.6 + job_relevance * 0.4) if job_words else question_relevance
        
        return {
            'score': min(1, max(0, relevance_score)),
            'question_relevance': question_relevance,
            'job_relevance': job_relevance,
            'details': f"Relevance: {relevance_score:.2f} (question: {question_relevance:.2f}, job: {job_relevance:.2f})"
        }
