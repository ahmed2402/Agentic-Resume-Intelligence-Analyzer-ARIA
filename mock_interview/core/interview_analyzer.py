"""
Interview Analysis Engine for Mock Interview Analyzer
Analyzes speech for clarity, confidence, sentiment, and keyword matching
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Optional
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import streamlit as st

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class InterviewAnalyzer:
    """Analyzes interview responses for various metrics"""
    
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
    def analyze_response(self, 
                        transcript: str, 
                        ideal_answer: str = "", 
                        audio_features: Dict = None) -> Dict:
        """
        Comprehensive analysis of interview response
        
        Args:
            transcript: Speech-to-text transcript
            ideal_answer: Ideal answer for keyword matching
            audio_features: Audio analysis features
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {}
        
        # Text-based analysis
        analysis['clarity'] = self._analyze_clarity(transcript)
        analysis['sentiment'] = self._analyze_sentiment(transcript)
        analysis['keyword_match'] = self._analyze_keyword_match(transcript, ideal_answer)
        analysis['fluency'] = self._analyze_fluency(transcript)
        
        # Audio-based analysis
        if audio_features:
            analysis['confidence'] = self._analyze_confidence(audio_features)
            analysis['speech_quality'] = self._analyze_speech_quality(audio_features)
        else:
            analysis['confidence'] = {'score': 0.5, 'details': 'No audio data available'}
            analysis['speech_quality'] = {'score': 0.5, 'details': 'No audio data available'}
        
        # Overall score
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
            'clarity': 0.25,
            'confidence': 0.25,
            'sentiment': 0.15,
            'keyword_match': 0.20,
            'fluency': 0.15
        }
        
        for metric, weight in weights.items():
            if metric in analysis and 'score' in analysis[metric]:
                scores.append(analysis[metric]['score'] * weight)
        
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
        if clarity.get('score', 0) < 0.6:
            feedback.append("• Reduce filler words (um, uh, like) for better clarity")
        elif clarity.get('score', 0) > 0.8:
            feedback.append("• Excellent clarity and articulation")
        
        # Confidence feedback
        confidence = analysis.get('confidence', {})
        if confidence.get('score', 0) < 0.6:
            feedback.append("• Speak with more confidence and volume")
        elif confidence.get('score', 0) > 0.8:
            feedback.append("• Great confidence in delivery")
        
        # Sentiment feedback
        sentiment = analysis.get('sentiment', {})
        if sentiment.get('label') == 'negative':
            feedback.append("• Maintain a more positive tone")
        elif sentiment.get('label') == 'positive':
            feedback.append("• Good positive attitude")
        
        # Keyword match feedback
        keyword_match = analysis.get('keyword_match', {})
        if keyword_match.get('score', 0) < 0.5:
            feedback.append("• Include more relevant keywords from the job description")
        elif keyword_match.get('score', 0) > 0.7:
            feedback.append("• Excellent use of relevant keywords")
        
        # Fluency feedback
        fluency = analysis.get('fluency', {})
        if fluency.get('score', 0) < 0.6:
            feedback.append("• Practice speaking more fluently and coherently")
        elif fluency.get('score', 0) > 0.8:
            feedback.append("• Very fluent and coherent delivery")
        
        return "\n".join(feedback) if feedback else "• Good overall performance"
