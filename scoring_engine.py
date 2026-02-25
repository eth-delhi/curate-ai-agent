"""
Scoring engine for content analysis and recommendations
"""
import re
from typing import Tuple, Dict, List
from models import ReadabilityResponse
from asi_one_client import get_comprehensive_analysis

# Dynamic weights system loaded

def calculate_readability(text: str) -> ReadabilityResponse:
    """Calculate comprehensive readability metrics using multiple algorithms"""
    if not text.strip():
        return ReadabilityResponse(
            readabilityFleschKincaid=0.0,
            readabilityGunningFog=0.0,
            readabilityScore=0.0
        )
    
    # Basic text analysis
    sentences = max(len(re.findall(r"[.!?]+", text)), 1)
    words = [w for w in text.split() if w.strip()]
    word_count = len(words)
    
    if word_count == 0:
        return ReadabilityResponse(
            readabilityFleschKincaid=0.0,
            readabilityGunningFog=0.0,
            readabilityScore=0.0
        )
    
    # Improved syllable counting
    def count_syllables(word):
        """More accurate syllable counting"""
        word = word.lower().strip()
        if not word:
            return 0
        
        # Remove common suffixes that don't add syllables
        word = re.sub(r'(es|ed|ing)$', '', word)
        
        # Count vowel groups
        vowels = re.findall(r'[aeiouy]+', word)
        syllable_count = len(vowels)
        
        # Handle silent 'e' at the end
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        # Minimum 1 syllable per word
        return max(syllable_count, 1)
    
    total_syllables = sum(count_syllables(word) for word in words)
    avg_syllables_per_word = total_syllables / word_count
    avg_words_per_sentence = word_count / sentences
    
    # Flesch-Kincaid Grade Level (improved)
    fk = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59
    
    # Gunning Fog Index (improved)
    # Complex words: 3+ syllables, excluding proper nouns and common suffixes
    complex_words = 0
    for word in words:
        if count_syllables(word) >= 3:
            # Exclude common words that shouldn't be considered complex
            if not re.match(r'^[A-Z]', word) and word.lower() not in [
                'beautiful', 'wonderful', 'terrible', 'possible', 'different', 'important',
                'interesting', 'necessary', 'available', 'comfortable', 'responsible'
            ]:
                complex_words += 1
    
    gf = 0.4 * (avg_words_per_sentence + 100 * (complex_words / word_count))
    
    # Additional readability metrics
    # SMOG Index (Simple Measure of Gobbledygook)
    if sentences >= 30:
        smog = 1.043 * (30 * (complex_words / sentences)) ** 0.5 + 3.1291
    else:
        smog = 1.043 * (word_count * (complex_words / word_count)) ** 0.5 + 3.1291
    
    # Coleman-Liau Index
    chars = len(re.sub(r'\s', '', text))
    cl = 0.0588 * (chars / word_count * 100) - 0.296 * (sentences / word_count * 100) - 15.8
    
    # Average all metrics for a comprehensive score
    avg_readability = (fk + gf + smog + cl) / 4
    
    # Normalize to 0-100 scale (lower is better for readability)
    # Grade level 0-6 = excellent (90-100), 7-9 = good (80-89), 10-12 = fair (70-79), 13+ = poor (0-69)
    if avg_readability <= 6:
        normalized_score = 100
    elif avg_readability <= 9:
        normalized_score = 90 - (avg_readability - 6) * 3.33
    elif avg_readability <= 12:
        normalized_score = 80 - (avg_readability - 9) * 3.33
    else:
        normalized_score = max(0, 70 - (avg_readability - 12) * 5)
    
    return ReadabilityResponse(
        readabilityFleschKincaid=round(fk, 2),
        readabilityGunningFog=round(gf, 2),
        readabilityScore=round(normalized_score, 1)
    )

def calculate_length_score(word_count: int) -> float:
    """Calculate length score using sigmoid function for smooth penalties"""
    import math
    
    if word_count == 0:
        return 0.0
    
    # Sigmoid function parameters
    # Steep penalty for content < 50 words, smooth transition after
    # Formula: 1 / (1 + exp(-k * (x - midpoint)))
    # k controls steepness, midpoint controls transition point
    
    k = 0.15  # Steepness factor - higher = steeper penalty
    midpoint = 50  # Transition point where penalty starts decreasing
    
    # Calculate sigmoid value (0 to 1)
    sigmoid_value = 1 / (1 + math.exp(-k * (word_count - midpoint)))
    
    # Scale to 0-100 range with minimum score of 5 for very short content
    # This ensures even 1-word posts get some score but very low
    min_score = 5.0
    max_score = 100.0
    
    length_score = min_score + (max_score - min_score) * sigmoid_value
    
    # Additional penalty for extremely short content (< 10 words)
    if word_count < 10:
        # Apply additional exponential penalty
        penalty_factor = math.exp(-0.3 * word_count)  # Heavier penalty for fewer words
        length_score = length_score * penalty_factor
    
    return max(0.0, min(100.0, length_score))

async def calculate_overall_score(sentiment_score: float, bias_score: float, readability_fk: float, 
                          originality_score: float, plagiarism_score: float, text: str = "") -> Tuple[int, Dict, List[str]]:
    """Calculate overall content score with ASI:One integration and averaged scoring"""
    
    # Get comprehensive analysis from ASI:One in single API call
    asi_analysis = await get_comprehensive_analysis(text)
    
    # Calculate text length score
    word_count = len(text.split()) if text else 0
    length_score = calculate_length_score(word_count)
    
    # Normalize our calculated scores to 0-100 scale
    sentiment_normalized = ((sentiment_score + 1) / 2) * 100  # -1 to +1 -> 0 to 100
    bias_normalized = (1 - bias_score) * 100  # 0 to 1 -> 100 to 0 (lower bias = higher score)
    readability_normalized = min(readability_fk, 100)  # Cap at 100
    originality_normalized = originality_score * 100  # 0 to 1 -> 0 to 100
    
    # Normalize ASI scores to 0-100 scale
    asi_sentiment_normalized = ((asi_analysis["sentiment"] + 1) / 2) * 100
    asi_plagiarism_normalized = asi_analysis["plagiarism"] * 100
    asi_originality_normalized = (1 - asi_analysis["plagiarism"]) * 100  # Convert plagiarism to originality
    asi_ai_detection_normalized = (1 - asi_analysis["ai_detection"]) * 100  # Convert AI detection to authenticity score
    
    print(f"🔍 AI Detection in scoring: {asi_analysis.get('ai_detection', 'NOT FOUND')}")
    print(f"🔍 Authenticity score: {asi_ai_detection_normalized}")
    
    # Dynamic weight adjustment based on length score
    if length_score < 20:  # Very short content (< ~25 words)
        weights = {
            'sentiment': 0.05,
            'bias': 0.10,
            'readability': 0.05,
            'originality': 0.10,
            'authenticity': 0.10,
            'length': 0.60
        }
    elif length_score < 40:  # Short content (~25-50 words)
        weights = {
            'sentiment': 0.10,
            'bias': 0.15,
            'readability': 0.05,
            'originality': 0.15,
            'authenticity': 0.15,
            'length': 0.40
        }
    elif length_score < 60:  # Medium-short content (~50-75 words)
        weights = {
            'sentiment': 0.12,
            'bias': 0.18,
            'readability': 0.08,
            'originality': 0.22,
            'authenticity': 0.20,
            'length': 0.20
        }
    else:  # Normal content (75+ words)
        weights = {
            'sentiment': 0.15,
            'bias': 0.20,
            'readability': 0.10,
            'originality': 0.30,
            'authenticity': 0.15,
            'length': 0.10
        }
    
    # Ensure weights sum to 1.0
    total_weight = sum(weights.values())
    if total_weight != 1.0:
        for key in weights:
            weights[key] = weights[key] / total_weight
    
    # Calculate base score WITHOUT AI detection and originality (they will be multipliers)
    base_weights = {
        'sentiment': weights['sentiment'],
        'bias': weights['bias'],
        'readability': weights['readability'],
        'length': weights['length']
    }
    
    # Normalize base weights to sum to 1.0
    base_weight_sum = sum(base_weights.values())
    for key in base_weights:
        base_weights[key] = base_weights[key] / base_weight_sum
    
    # Calculate base score without AI and originality
    base_score = (
        sentiment_normalized * base_weights['sentiment'] +
        bias_normalized * base_weights['bias'] +
        readability_normalized * base_weights['readability'] +
        length_score * base_weights['length']
    )
    
    # Calculate multiplier from AI detection and originality
    # Formula: (AI score + Originality score) / 2
    ai_score_normalized = asi_ai_detection_normalized / 100  # Convert to 0-1 scale
    originality_score_normalized = asi_originality_normalized / 100  # Convert to 0-1 scale
    multiplier = (ai_score_normalized + originality_score_normalized) / 2
    
    # Apply multiplier to base score
    our_score = base_score * multiplier
    
    # Get ASI's overall score
    asi_score = asi_analysis["overall_score"]
    
    # Average our score with ASI's score for balanced assessment
    # Weight: 80% our calculation, 20% ASI assessment
    final_score = int((our_score * 0.65) + (asi_score * 0.35))
    final_score = max(0, min(100, final_score))
    
    # Create detailed breakdown showing both our scores and ASI scores
    score_breakdown = {
        'sentiment': {
            'our_score': 'N/A',
            'asi_score': round(asi_sentiment_normalized, 1),
            'final_score': round(asi_sentiment_normalized, 1),
            'weight': weights['sentiment'],
            'contribution': round((asi_sentiment_normalized) * weights['sentiment'], 1)
        },
        'bias': {
            'our_score': round(bias_normalized, 1),
            'asi_score': 'N/A',  # ASI doesn't provide bias analysis
            'final_score': round(bias_normalized, 1),
            'weight': weights['bias'],
            'contribution': round(bias_normalized * weights['bias'], 1)
        },
        'readability': {
            'our_score': round(readability_normalized, 1),
            'asi_score': 'N/A',  # ASI doesn't provide readability analysis
            'final_score': round(readability_normalized, 1),
            'weight': weights['readability'],
            'contribution': round(readability_normalized * weights['readability'], 1)
        },
        'originality': {
            'our_score': 'N/A',
            'asi_score': round(asi_originality_normalized, 1),
            'final_score': round(asi_originality_normalized, 1),
            'weight': weights['originality'],
            'contribution': round((asi_originality_normalized) * weights['originality'], 1)
        },
        'plagiarism': {
            'our_score': 'N/A',
            'asi_score': round(asi_plagiarism_normalized, 1),
            'final_score': round(asi_plagiarism_normalized, 1),
            'weight': weights['originality'],
            'contribution': round((asi_plagiarism_normalized) * weights['originality'], 1)
        },
        'authenticity': {
            'our_score': 'N/A',
            'asi_score': round(asi_ai_detection_normalized, 1),
            'final_score': round(asi_ai_detection_normalized, 1),
            'weight': weights['authenticity'],
            'contribution': round((asi_ai_detection_normalized) * weights['authenticity'], 1),
            'ai_detection_score': round(asi_analysis["ai_detection"] * 100, 1)
        },
        'length': {
            'our_score': round(length_score, 1),
            'asi_score': 'N/A',  # ASI doesn't provide length analysis
            'final_score': round(length_score, 1),
            'weight': weights['length'],
            'contribution': round(length_score * weights['length'], 1),
            'word_count': word_count
        },
        'overall': {
            'base_score': round(base_score, 1),
            'ai_originality_multiplier': round(multiplier, 3),
            'our_calculation': round(our_score, 1),
            'asi_assessment': round(asi_score, 1),
            'final_averaged': round(final_score, 1),
            'asi_reasoning': asi_analysis["reasoning"]
        }
    }
    
    # Generate recommendations based on scores
    recommendations = []
    
    if asi_analysis.get("ai_detection", 0.0) > 0.7:
        recommendations.append("Content appears to be AI-generated. Consider adding more human perspective and personal insights.")
    
    if asi_analysis.get("plagiarism", 0.5) > 0.7:
        recommendations.append("High plagiarism detected. Ensure content is original and properly attributed.")
    
    if bias_score > 0.7:
        recommendations.append("Content shows significant bias. Consider presenting multiple perspectives.")
    
    if readability_fk < 30:
        recommendations.append("Content is difficult to read. Consider simplifying language and sentence structure.")
    
    if asi_analysis.get("plagiarism", 0.5) < 0.3:  # Low plagiarism = high originality
        if word_count < 30:
            recommendations.append("Content is too short. Expand with more details, examples, or explanations.")
    
    if not recommendations:
        recommendations.append("Content meets quality standards across all metrics.")
    
    return final_score, score_breakdown, recommendations
