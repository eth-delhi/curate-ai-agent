"""
Ollama client for content analysis and scoring (FREE, LOCAL, UNLIMITED)
"""
import os
import json
import re
from typing import Dict, List, Tuple
from openai import OpenAI

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    # python-dotenv not installed, continue without it
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")

# Initialize Ollama client (compatible with OpenAI API format, runs locally)
# Ollama runs on localhost:11434 by default
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")  # Default to llama3.2, can use: llama3.1, mistral, phi3, etc.

try:
    # Ollama is compatible with OpenAI API format, just change the base_url
    # No API key needed for local Ollama
    client = OpenAI(
        api_key="ollama",  # Dummy key, not used by local Ollama
        base_url=ollama_base_url
    )
    print(f"✅ Ollama client initialized successfully")
    print(f"   Using model: {ollama_model}")
    print(f"   Base URL: {ollama_base_url}")
    print("   💡 Make sure Ollama is running: ollama serve")
except Exception as e:
    print(f"❌ Failed to initialize Ollama client: {e}")
    print("   💡 Install Ollama: https://ollama.ai/download")
    print("   💡 Start Ollama: ollama serve")
    print("   💡 Pull a model: ollama pull llama3.2")
    client = None

def analyze_content_with_openai(text: str) -> Dict:
    """
    Comprehensive content analysis using Ollama (local LLM)
    Returns sentiment, bias, readability, originality, and AI detection scores
    """
    if not text.strip():
        return {
            "sentiment": 0.0,
            "bias": 0.0,
            "readability": 50.0,
            "originality": 0.5,
            "plagiarism": 0.5,
            "ai_detection": 0.5,
            "main_topic": "General",
            "secondary_topics": ["General"],
            "reasoning": "Empty content provided"
        }
    
    prompt = f"""
Analyze the following text and provide a comprehensive content analysis. Return ONLY a valid JSON object with the following structure:

{{
  "sentiment": <number from -1.0 to 1.0>,
  "bias": <number from 0.0 to 1.0>,
  "readability": <number from 0 to 100>,
  "originality": <number from 0.0 to 1.0>,
  "plagiarism": <number from 0.0 to 1.0>,
  "ai_detection": <number from 0.0 to 1.0>,
  "main_topic": "<string>",
  "secondary_topics": ["<string>", "<string>", "<string>"],
  "reasoning": "<brief explanation of the analysis>"
}}

SCORING GUIDELINES:

SENTIMENT (-1.0 to 1.0):
- -1.0: Very negative, critical, pessimistic
- 0.0: Neutral, factual, balanced
- 1.0: Very positive, optimistic, enthusiastic

BIAS (0.0 to 1.0):
- 0.0: Completely neutral, objective, balanced
- 0.5: Somewhat biased, shows preference
- 1.0: Heavily biased, one-sided, prejudiced

READABILITY (0 to 100):
- 0-30: Very difficult, academic, complex
- 31-50: Difficult, technical, formal
- 51-70: Standard, average reader
- 71-90: Easy, conversational
- 91-100: Very easy, simple language

ORIGINALITY (0.0 to 1.0):
- 0.0: Completely unoriginal, generic, template-like
- 0.5: Somewhat original, mixed content
- 1.0: Highly original, unique, creative

PLAGIARISM (0.0 to 1.0):
- 0.0: Completely original, not found online
- 0.5: Some common phrases, mostly original
- 1.0: Appears copied from internet sources

AI DETECTION (0.0 to 1.0):
- 0.0: Definitely human-written
- 0.5: Unclear, could be either
- 1.0: Definitely AI-generated

Text to analyze: "{text}"
"""

    if not client:
        print("❌ Ollama client not initialized. Please make sure Ollama is running.")
        print("   Install: https://ollama.ai/download")
        print("   Start: ollama serve")
        print("   Pull model: ollama pull llama3.2")
        return {
            "sentiment": 0.0,
            "bias": 0.5,
            "readability": 50.0,
            "originality": 0.5,
            "plagiarism": 0.5,
            "ai_detection": 0.5,
            "main_topic": "General",
            "secondary_topics": ["General"],
            "reasoning": "Ollama not running or not configured"
        }
    
    try:
        response = client.chat.completions.create(
            model=ollama_model,
            messages=[
                {"role": "system", "content": "You are an expert content analyst. Analyze text and provide accurate scores. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content.strip()
        
        # Clean up the response to extract JSON
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        # Parse JSON
        result = json.loads(content)
        
        # Validate and clamp values
        result["sentiment"] = max(-1.0, min(1.0, float(result.get("sentiment", 0.0))))
        result["bias"] = max(0.0, min(1.0, float(result.get("bias", 0.5))))
        result["readability"] = max(0.0, min(100.0, float(result.get("readability", 50.0))))
        result["originality"] = max(0.0, min(1.0, float(result.get("originality", 0.5))))
        result["plagiarism"] = max(0.0, min(1.0, float(result.get("plagiarism", 0.5))))
        result["ai_detection"] = max(0.0, min(1.0, float(result.get("ai_detection", 0.5))))
        result["main_topic"] = str(result.get("main_topic", "General"))
        result["secondary_topics"] = list(result.get("secondary_topics", ["General"]))
        result["reasoning"] = str(result.get("reasoning", "Analysis completed"))
        
        return result
        
    except Exception as e:
        print(f"❌ Ollama analysis error: {e}")
        print("   💡 Make sure Ollama is running: ollama serve")
        print(f"   💡 Make sure model is pulled: ollama pull {ollama_model}")
        # Return default values on error
        return {
            "sentiment": 0.0,
            "bias": 0.5,
            "readability": 50.0,
            "originality": 0.5,
            "plagiarism": 0.5,
            "ai_detection": 0.5,
            "main_topic": "General",
            "secondary_topics": ["General"],
            "reasoning": f"Analysis failed: {str(e)}"
        }

def calculate_readability_openai(text: str) -> Dict:
    """
    Calculate readability metrics (using local calculation, not API)
    """
    if not text.strip():
        return {
            "readabilityFleschKincaid": 0.0,
            "readabilityGunningFog": 0.0,
            "readabilityScore": 0.0
        }
    
    # Basic text analysis for fallback
    sentences = max(len(re.findall(r"[.!?]+", text)), 1)
    words = [w for w in text.split() if w.strip()]
    word_count = len(words)
    
    if word_count == 0:
        return {
            "readabilityFleschKincaid": 0.0,
            "readabilityGunningFog": 0.0,
            "readabilityScore": 0.0
        }
    
    # Simple readability calculation as fallback
    def count_syllables(word):
        word = word.lower().strip()
        if not word:
            return 0
        word = re.sub(r'(es|ed|ing)$', '', word)
        vowels = re.findall(r'[aeiouy]+', word)
        syllable_count = len(vowels)
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        return max(syllable_count, 1)
    
    total_syllables = sum(count_syllables(word) for word in words)
    avg_syllables_per_word = total_syllables / word_count
    avg_words_per_sentence = word_count / sentences
    
    # Flesch-Kincaid Grade Level
    fk_score = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59
    
    # Gunning Fog Index
    complex_words = sum(1 for word in words if count_syllables(word) > 2)
    fog_score = 0.4 * (avg_words_per_sentence + (complex_words / word_count) * 100)
    
    # Convert to 0-100 scale
    readability_score = max(0, min(100, 100 - fk_score * 2))
    
    return {
        "readabilityFleschKincaid": max(0.0, fk_score),
        "readabilityGunningFog": max(0.0, fog_score),
        "readabilityScore": max(0.0, min(100.0, readability_score))
    }
