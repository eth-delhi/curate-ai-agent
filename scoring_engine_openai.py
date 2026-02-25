"""
OpenAI-based scoring engine for content analysis and recommendations
"""
import re
from typing import Tuple, Dict, List
from models import ReadabilityResponse
from openai_client import analyze_content_with_openai, calculate_readability_openai

# Dynamic weights for different content types
WEIGHTS = {
    "sentiment": 0.15,
    "bias": 0.20,
    "readability": 0.15,
    "originality": 0.20,
    "authenticity": 0.20,  # AI detection penalty
    "length": 0.10
}

def calculate_readability(text: str) -> ReadabilityResponse:
    """Calculate comprehensive readability metrics using OpenAI"""
    if not text.strip():
        return ReadabilityResponse(
            readabilityFleschKincaid=0.0,
            readabilityGunningFog=0.0,
            readabilityScore=0.0
        )
    
    # Get readability from OpenAI analysis
    analysis = analyze_content_with_openai(text)
    readability_score = analysis["readability"]
    
    # Convert to Flesch-Kincaid and Gunning Fog scales
    # Higher readability score = lower grade level = easier to read
    fk_grade = max(0, (100 - readability_score) / 10)  # Convert to grade level
    fog_index = max(0, (100 - readability_score) / 8)   # Convert to fog index
    
    return ReadabilityResponse(
        readabilityFleschKincaid=fk_grade,
        readabilityGunningFog=fog_index,
        readabilityScore=readability_score
    )

def calculate_length_score(text: str) -> float:
    """Calculate length-based score with penalties for very short content"""
    if not text.strip():
        return 0.0
    
    word_count = len(text.split())
    
    # Length scoring with penalties for short content
    if word_count < 10:
        return max(0.0, word_count * 2)  # Very short content gets low score
    elif word_count < 25:
        return max(0.0, 20 + (word_count - 10) * 1.5)  # Short content penalty
    elif word_count < 50:
        return max(0.0, 42.5 + (word_count - 25) * 1.0)  # Medium content
    elif word_count < 100:
        return max(0.0, 67.5 + (word_count - 50) * 0.5)  # Good length
    else:
        return max(0.0, 92.5 + min(word_count - 100, 50) * 0.15)  # Long content bonus

async def calculate_overall_score(text: str = "") -> Tuple[int, Dict, List[str]]:
    """Calculate overall content score using OpenAI analysis"""
    
    if not text.strip():
        return 0, {
            'sentiment': {'our_score': 0, 'final_score': 0, 'weight': WEIGHTS['sentiment'], 'contribution': 0},
            'bias': {'our_score': 0, 'final_score': 0, 'weight': WEIGHTS['bias'], 'contribution': 0},
            'readability': {'our_score': 0, 'final_score': 0, 'weight': WEIGHTS['readability'], 'contribution': 0},
            'originality': {'our_score': 0, 'final_score': 0, 'weight': WEIGHTS['originality'], 'contribution': 0},
            'plagiarism': {'our_score': 0, 'final_score': 0, 'weight': WEIGHTS['originality'], 'contribution': 0},
            'authenticity': {'our_score': 0, 'final_score': 0, 'weight': WEIGHTS['authenticity'], 'contribution': 0},
            'length': {'our_score': 0, 'final_score': 0, 'weight': WEIGHTS['length'], 'contribution': 0},
            'overall': {'final_score': 0, 'reasoning': 'Empty content provided'}
        }, ["Empty content provided"]
    
    # Get comprehensive analysis from OpenAI
    analysis = analyze_content_with_openai(text)
    
    # Extract scores
    sentiment_score = analysis["sentiment"]
    bias_score = analysis["bias"]
    readability_score = analysis["readability"]
    originality_score = analysis["originality"]
    plagiarism_score = analysis["plagiarism"]
    ai_detection_score = analysis["ai_detection"]
    
    # Calculate length score
    length_score = calculate_length_score(text)
    
    # Normalize scores to 0-100 scale
    sentiment_normalized = ((sentiment_score + 1) / 2) * 100  # -1 to +1 -> 0 to 100
    bias_normalized = (1 - bias_score) * 100  # 0 to 1 -> 100 to 0 (lower bias = higher score)
    readability_normalized = readability_score  # Already 0-100
    originality_normalized = originality_score * 100  # 0 to 1 -> 0 to 100
    plagiarism_normalized = plagiarism_score * 100  # 0 to 1 -> 0 to 100
    authenticity_normalized = (1 - ai_detection_score) * 100  # Convert AI detection to authenticity score
    
    # Apply AI detection penalty
    ai_penalty = ai_detection_score * 50  # Up to 50 point penalty for AI content
    final_sentiment = max(0, sentiment_normalized - ai_penalty)
    final_bias = max(0, bias_normalized - ai_penalty)
    final_readability = max(0, readability_normalized - ai_penalty)
    final_originality = max(0, originality_normalized - ai_penalty)
    final_plagiarism = min(100, plagiarism_normalized + ai_penalty)  # Increase plagiarism for AI content
    final_authenticity = max(0, authenticity_normalized - ai_penalty)
    
    # Calculate weighted overall score
    overall_score = (
        final_sentiment * WEIGHTS['sentiment'] +
        final_bias * WEIGHTS['bias'] +
        final_readability * WEIGHTS['readability'] +
        final_originality * WEIGHTS['originality'] +
        final_authenticity * WEIGHTS['authenticity'] +
        length_score * WEIGHTS['length']
    )
    
    # Round to integer
    final_score = max(0, min(100, round(overall_score)))
    
    # Generate recommendations
    recommendations = []
    
    if ai_detection_score > 0.7:
        recommendations.append("Content appears to be AI-generated. Consider adding more human perspective and personal insights.")
    
    if plagiarism_score > 0.7:
        recommendations.append("High plagiarism detected. Ensure content is original and properly attributed.")
    
    if bias_score > 0.7:
        recommendations.append("Content shows significant bias. Consider presenting multiple perspectives.")
    
    if readability_score < 30:
        recommendations.append("Content is difficult to read. Consider simplifying language and sentence structure.")
    
    if originality_score < 0.3:
        recommendations.append("Content lacks originality. Add unique insights, examples, or personal experiences.")
    
    if length_score < 30:
        recommendations.append("Content is too short. Expand with more details, examples, or explanations.")
    
    if not recommendations:
        recommendations.append("Content meets quality standards across all metrics.")
    
    # Prepare detailed score breakdown
    score_breakdown = {
        'sentiment': {
            'our_score': round(sentiment_normalized, 1),
            'final_score': round(final_sentiment, 1),
            'weight': WEIGHTS['sentiment'],
            'contribution': round(final_sentiment * WEIGHTS['sentiment'], 1)
        },
        'bias': {
            'our_score': round(bias_normalized, 1),
            'final_score': round(final_bias, 1),
            'weight': WEIGHTS['bias'],
            'contribution': round(final_bias * WEIGHTS['bias'], 1)
        },
        'readability': {
            'our_score': round(readability_normalized, 1),
            'final_score': round(final_readability, 1),
            'weight': WEIGHTS['readability'],
            'contribution': round(final_readability * WEIGHTS['readability'], 1)
        },
        'originality': {
            'our_score': round(originality_normalized, 1),
            'final_score': round(final_originality, 1),
            'weight': WEIGHTS['originality'],
            'contribution': round(final_originality * WEIGHTS['originality'], 1)
        },
        'plagiarism': {
            'our_score': round(plagiarism_normalized, 1),
            'final_score': round(final_plagiarism, 1),
            'weight': WEIGHTS['originality'],
            'contribution': round(final_plagiarism * WEIGHTS['originality'], 1)
        },
        'authenticity': {
            'our_score': round(authenticity_normalized, 1),
            'final_score': round(final_authenticity, 1),
            'weight': WEIGHTS['authenticity'],
            'contribution': round(final_authenticity * WEIGHTS['authenticity'], 1)
        },
        'length': {
            'our_score': round(length_score, 1),
            'final_score': round(length_score, 1),
            'weight': WEIGHTS['length'],
            'contribution': round(length_score * WEIGHTS['length'], 1)
        },
        'overall': {
            'final_score': final_score,
            'reasoning': analysis.get("reasoning", "Analysis completed")
        }
    }
    
    return final_score, score_breakdown, recommendations
