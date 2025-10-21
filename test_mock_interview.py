"""
Test script for Mock Interview Analyzer
"""

import sys
import os

# Add the mock_interview module to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mock_interview'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from mock_interview.core.audio_processor import AudioProcessor
        from mock_interview.core.interview_analyzer import InterviewAnalyzer
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_analyzer():
    """Test the interview analyzer with sample data"""
    try:
        from mock_interview.core.interview_analyzer import InterviewAnalyzer
        
        analyzer = InterviewAnalyzer()
        
        # Test with sample transcript
        sample_transcript = "I have experience with Python programming and machine learning. I worked on several projects involving data analysis and model development."
        sample_ideal = "Python, machine learning, data analysis, model development, programming"
        
        analysis = analyzer.analyze_response(
            transcript=sample_transcript,
            ideal_answer=sample_ideal
        )
        
        print("✅ Analysis completed successfully")
        print(f"Overall Score: {analysis.get('overall_score', {}).get('score', 0):.1%}")
        return True
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Mock Interview Analyzer...")
    
    # Test imports
    if test_imports():
        print("Testing analyzer functionality...")
        test_analyzer()
    
    print("Test completed!")
