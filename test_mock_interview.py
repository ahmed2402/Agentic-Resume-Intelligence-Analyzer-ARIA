"""
Test script for Mock Interview module
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def test_question_generator():
    """Test question generation"""
    try:
        from mock_interview.core.question_generator import QuestionGenerator
        
        print("Testing Question Generator...")
        generator = QuestionGenerator()
        
        # Test job description
        job_description = """
        We are looking for a Senior Software Engineer with 5+ years of experience in Python, 
        Django, and React. The ideal candidate should have experience with cloud platforms 
        like AWS, database design, and agile development methodologies. Strong communication 
        skills and leadership experience are required.
        """
        
        questions = generator.generate_questions(
            job_description=job_description,
            num_questions=3,
            question_types=["technical", "behavioral"]
        )
        
        print(f"Generated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q['question']}")
            print(f"   Type: {q['type']}, Difficulty: {q['difficulty']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"Error testing question generator: {e}")
        return False

def test_interview_analyzer():
    """Test interview analysis"""
    try:
        from mock_interview.core.interview_analyzer import InterviewAnalyzer
        
        print("Testing Interview Analyzer...")
        analyzer = InterviewAnalyzer()
        
        # Test analysis
        transcript = "I have 5 years of experience in Python development. I've worked on several web applications using Django and React. I'm comfortable with AWS and have led a team of 3 developers."
        question = "Tell me about your experience with Python and web development."
        job_description = "Looking for a Python developer with Django and React experience."
        
        analysis = analyzer.analyze_response(
            transcript=transcript,
            question=question,
            job_description=job_description
        )
        
        print("Analysis results:")
        for metric, data in analysis.items():
            if isinstance(data, dict) and 'score' in data:
                print(f"{metric}: {data['score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"Error testing interview analyzer: {e}")
        return False

def test_report_generator():
    """Test report generation"""
    try:
        from mock_interview.core.report_generator import InterviewReportGenerator
        
        print("Testing Report Generator...")
        generator = InterviewReportGenerator()
        
        # Mock session data
        session_data = {
            'job_description': 'Python developer role',
            'questions': [
                {'question': 'Tell me about your Python experience', 'type': 'technical'},
                {'question': 'Describe a challenging project', 'type': 'behavioral'}
            ],
            'responses': [
                'I have 5 years of Python experience',
                'I worked on a complex data processing system'
            ],
            'analyses': [
                {'overall_score': {'score': 0.8, 'grade': 'B'}},
                {'overall_score': {'score': 0.7, 'grade': 'C'}}
            ]
        }
        
        report = generator.generate_comprehensive_report(session_data)
        
        print("Report generated successfully!")
        print(f"Overall performance: {report['overall_performance']['overall_score']:.2f}")
        print(f"Strengths: {len(report['strengths_weaknesses']['strengths'])}")
        print(f"Weaknesses: {len(report['strengths_weaknesses']['weaknesses'])}")
        
        return True
        
    except Exception as e:
        print(f"Error testing report generator: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Mock Interview Module")
    print("=" * 40)
    
    tests = [
        ("Question Generator", test_question_generator),
        ("Interview Analyzer", test_interview_analyzer),
        ("Report Generator", test_report_generator)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 20)
        success = test_func()
        results.append((test_name, success))
    
    print("\n📊 Test Results")
    print("=" * 20)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    print(f"\nOverall: {'✅ All tests passed!' if all_passed else '❌ Some tests failed'}")
