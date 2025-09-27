"""
ASI:One API client for sentiment analysis, topic extraction, and similarity analysis
"""
import requests
import os
import uuid
import json
import hashlib

# ASI:One configuration
ASI_API_KEY = os.getenv("ASI_API_KEY", "sk_9689b877472544e58079d7067bd9af5bae7fbfb048e34e5ebae251a9fae8cf68")
ASI_BASE_URL = "https://api.asi1.ai/v1"


def get_headers():
    """Get standard headers for ASI:One API requests"""
    return {
        "Authorization": f"Bearer {ASI_API_KEY}",
        "Content-Type": "application/json",
        "x-session-id": str(uuid.uuid4())
    }


async def get_comprehensive_analysis(text: str) -> dict:
    """Get comprehensive analysis using single ASI:One API call with improved consistency"""
    try:
        print(f"🔑 ASI_API_KEY status: {'SET' if ASI_API_KEY else 'NOT SET'}")
        
        if not ASI_API_KEY:
            print("❌ ASI_API_KEY not found, returning default values")
            return {
                "sentiment": 0.0,
                "main_topic": "General",
                "secondary_topics": ["AI", "Technology"],
                "plagiarism": 0.5,
                "overall_score": 50.0,
                "reasoning": "No API key available"
            }
        
            
        print(f"🔍 Calling ASI:One for comprehensive analysis...")
        url = f"{ASI_BASE_URL}/chat/completions"
        payload = {
            "model": "asi1-mini",
            "messages": [
                {
                    "role": "system", 
                    "content": """You are an expert plagiarism detector. Analyze the text and determine if it appears to be copied from the internet or contains common internet phrases.

Return ONLY a valid JSON object with these exact fields:

{
  "sentiment": <number from -1.0 to 1.0>,
  "main_topic": "<string>",
  "secondary_topics": ["<string>", "<string>", "<string>"],
  "plagiarism": <number from 0.0 to 1.0>,
  "ai_detection": <number from 0.0 to 1.0>,
  "overall_score": <number from 0 to 100>,
  "reasoning": "<brief explanation of the overall score>"
}

CRITICAL PLAGIARISM DETECTION RULES:
- plagiarism: 0.0 (completely original) to 1.0 (copied from internet)
- Check if content appears to be copied from common internet sources
- Look for exact phrases commonly found online
- Consider if content matches typical internet patterns
- Very short content (1-5 words) is often copied = high plagiarism
- AI disclaimers are very common online = high plagiarism
- Generic greetings are common online = high plagiarism
- Long, detailed content is usually original = low plagiarism

PLAGIARISM INDICATORS (high plagiarism):
- Exact phrases like "hello world", "as an ai language model"
- Common internet patterns like "according to", "studies show"
- Very short content that's generic
- Content that sounds like it came from a template
- Repetitive or formulaic language

ORIGINALITY INDICATORS (low plagiarism):
- Personal opinions and experiences
- Specific details and examples
- Unique phrasing and word choice
- Long, detailed explanations
- Content that shows personal thought

PLAGIARISM SCORING GUIDE:
- 0.0-0.2: Completely original content with unique phrasing
- 0.3-0.5: Some common phrases but mostly original
- 0.6-0.8: Contains many common internet patterns
- 0.9-1.0: Appears to be copied from internet or very generic

CRITICAL SCORING RULES - BE EXTREMELY CONSISTENT:
- For very short content (1-5 words): overall_score MUST be 0-20 maximum
- For short content (6-20 words): overall_score MUST be 0-40 maximum  
- For medium content (21-50 words): overall_score MUST be 0-70 maximum
- For longer content (50+ words): overall_score can be 0-100
- Content length is a MAJOR factor - very short posts cannot receive high scores
- Single words should get scores of 0-10 maximum regardless of sentiment
- AI-GENERATED CONTENT PENALTY: If ai_detection > 0.5, reduce overall_score by 30-50 points
- AI-GENERATED CONTENT PENALTY: If ai_detection > 0.3, reduce overall_score by 15-25 points
- AI-GENERATED CONTENT PENALTY: If ai_detection > 0.2, reduce overall_score by 5-15 points

EXACT SCORING FORMULA - FOLLOW EXACTLY:
1. Count words: {word_count}
2. If word_count <= 5: max_score = 20
3. If word_count <= 20: max_score = 40
4. If word_count <= 50: max_score = 70
5. If word_count > 50: max_score = 100
6. Apply AI penalty: if ai_detection > 0.5: subtract 40 points
7. Apply AI penalty: if ai_detection > 0.3: subtract 20 points
8. Apply AI penalty: if ai_detection > 0.2: subtract 10 points
9. Final score = max(0, min(max_score, base_score - penalties))

CRITICAL CONSISTENCY REQUIREMENTS - BE EXTREMELY CONSISTENT:
- Use the EXACT SAME scoring criteria for similar content types
- Apply penalties IDENTICALLY for same conditions - never vary
- Be strict with very short content - never give high scores
- AI-generated content should ALWAYS receive significant penalties
- Content that is not helpful or informative should ALWAYS receive significant penalties
- Content that is not factually accurate should ALWAYS receive significant penalties
- Content that is not well-written should ALWAYS receive significant penalties
- Content that is not well-structured should ALWAYS receive significant penalties
- Content that is not well-organized should ALWAYS receive significant penalties
- Content that is not well-formatted should ALWAYS receive significant penalties

SCORING CONSISTENCY RULES:
- Identical content length = identical length penalties
- Identical AI detection = identical AI penalties  
- Identical content type = identical base scores
- Same word count range = same maximum possible score
- Never vary scores for identical conditions

IMPORTANT:
- Any thing harmful and violent, even a slightest bit of it should ALWAYS receive 0 overall score and not more than 0.05 in any other metric (Including sentiment, topic and originality)
- Similarity and AI Detection should be 0.95 for harmful and violent content
- Same for meaningless gibberish with random characters and numbers.

Where:
- sentiment: -1.0 (very negative) to +1.0 (very positive)
- main_topic: Primary subject matter
- secondary_topics: 2-3 related topics
- plagiarism: 0.0 (completely original) to 1.0 (copied from internet)
- ai_detection: 0.0 (definitely human) to 1.0 (definitely AI-generated)
- overall_score: Overall content quality from 0-100 (HEAVILY PENALIZE SHORT CONTENT AND AI-GENERATED CONTENT)
- reasoning: Brief explanation of the overall score including length and AI detection consideration"""
                },
                {"role": "user", "content": f"Text: {text}"}
            ],
            "max_tokens": 300,
            "temperature": 0.05
        }
        
        response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
        print(f"📡 ASI:One response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ ASI:One error: {response.status_code} - {response.text}")
            return {
                "sentiment": 0.0,
                "main_topic": "General",
                "secondary_topics": ["AI", "Technology"],
                "plagiarism": 0.5,
                "ai_detection": 0.0,
                "overall_score": 50.0,
                "reasoning": "API error"
            }
            
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        print(f"✅ ASI:One result: {content}")
        
        # Clean the content to ensure it's valid JSON
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Try to find JSON object in the content
        if "{" in content and "}" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            content = content[start:end]
        
        # Parse JSON response
        try:
            parsed = json.loads(content)
            print(f"🔍 Parsed ASI response: {parsed}")
            
            # Validate and clamp values
            ai_detection = parsed.get("ai_detection", 0.0)
            print(f"🔍 AI Detection from ASI: {ai_detection}")
            
            # Post-process for fairness and consistency
            word_count = len(text.split())
            asi_ai_detection = max(0.0, min(1.0, float(ai_detection)))
            raw_score = float(parsed.get("overall_score", 50.0))
            
            # Apply consistent scoring rules
            if word_count <= 5:
                max_score = 20
            elif word_count <= 20:
                max_score = 40
            elif word_count <= 50:
                max_score = 70
            else:
                max_score = 100
            
            # Use ASI detection directly
            final_ai_detection = asi_ai_detection
            
            # Apply AI penalties consistently
            ai_penalty = 0
            if final_ai_detection > 0.5:
                ai_penalty = 40
            elif final_ai_detection > 0.3:
                ai_penalty = 20
            elif final_ai_detection > 0.2:
                ai_penalty = 10
            
            # Calculate final score
            final_score = max(0, min(max_score, raw_score - ai_penalty))
            
            print(f"🔍 Post-processing: word_count={word_count}, max_score={max_score}, ai_detection={final_ai_detection}, ai_penalty={ai_penalty}, final_score={final_score}")
            
            return {
                "sentiment": max(-1.0, min(1.0, float(parsed.get("sentiment", 0.0)))),
                "main_topic": str(parsed.get("main_topic", "General")),
                "secondary_topics": list(parsed.get("secondary_topics", ["AI", "Technology"])),
                "plagiarism": max(0.0, min(1.0, float(parsed.get("plagiarism", 0.5)))),
                "ai_detection": final_ai_detection,
                "overall_score": final_score,
                "reasoning": str(parsed.get("reasoning", "No reasoning provided"))
            }
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"❌ Could not parse ASI response: {e}")
            print(f"🔍 Raw content: {repr(content)}")
            return {
                "sentiment": 0.0,
                "main_topic": "General",
                "secondary_topics": ["AI", "Technology"],
                "plagiarism": 0.5,
                "ai_detection": 0.0,
                "overall_score": 50.0,
                "reasoning": "Parse error"
            }
        
    except Exception as e:
        print(f"❌ ASI:One comprehensive analysis failed: {e}")
        return {
            "sentiment": 0.0,
            "main_topic": "General",
            "secondary_topics": ["AI", "Technology"],
            "similarity": 0.5,
            "ai_detection": 0.0,
            "overall_score": 50.0,
            "reasoning": "Exception occurred"
        }

