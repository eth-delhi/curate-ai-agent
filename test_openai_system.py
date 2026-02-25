#!/usr/bin/env python3
"""
Test script for OpenAI-based content analysis system
"""
import asyncio
import os
from scoring_engine_openai import calculate_overall_score

async def test_system():
    """Test the OpenAI-based scoring system"""
    print("🧪 Testing OpenAI-based Content Analysis System")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        "This is a completely original piece of content that I wrote myself.",
        "As an AI language model, I cannot provide personal opinions.",
        "The weather is nice today and I feel happy about it.",
        "According to studies, this is a common phrase found online.",
        "I personally believe that this topic requires careful consideration."
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {text[:50]}...")
        print("-" * 30)
        
        try:
            overall_score, score_breakdown, recommendations = await calculate_overall_score(text)
            
            print(f"Overall Score: {overall_score}")
            print(f"Sentiment: {score_breakdown['sentiment']['final_score']:.1f}")
            print(f"Bias: {score_breakdown['bias']['final_score']:.1f}")
            print(f"Readability: {score_breakdown['readability']['final_score']:.1f}")
            print(f"Originality: {score_breakdown['originality']['final_score']:.1f}")
            print(f"Plagiarism: {score_breakdown['plagiarism']['final_score']:.1f}")
            print(f"Authenticity: {score_breakdown['authenticity']['final_score']:.1f}")
            print(f"Length: {score_breakdown['length']['final_score']:.1f}")
            
            if recommendations:
                print(f"Recommendations: {recommendations[0]}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_system())
