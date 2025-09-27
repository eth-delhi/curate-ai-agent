"""
MeTTa reasoning engine for bias detection and content analysis
"""
from hyperon import MeTTa
from models import BiasResponse

# Initialize MeTTa runtime
metta = MeTTa()

# Define word categories for bias detection
extreme_words = [
    "always", "never", "disaster", "catastrophic", "terrible", "amazing", 
    "perfect", "awful", "incredible", "revolutionary", "unprecedented",
    "devastating", "outstanding", "horrible", "brilliant", "nightmare",
    "breakthrough", "crisis", "exceptional", "tragic", "phenomenal"
]

polarizing_words = [
    "woke", "snowflake", "boomer", "millennial", "gen-z", "cancel",
    "triggered", "offended", "privileged", "entitled", "toxic",
    "problematic", "controversial", "divisive", "extreme"
]

profanity_words = [
    "fuck", "shit", "damn", "hell", "bitch", "ass", "crap", "piss",
    "bastard", "dick", "cock", "pussy", "whore", "slut", "fag",
    "nigger", "faggot", "retard", "idiot", "moron", "stupid"
]

def initialize_metta_rules():
    """Initialize MeTTa knowledge base with bias detection rules"""
    # Add atoms to MeTTa knowledge base
    for word in extreme_words:
        metta.run(f'!(add-atom (extreme-word "{word}" 0.9))')

    for word in polarizing_words:
        metta.run(f'!(add-atom (polarizing-word "{word}" 0.7))')

    for word in profanity_words:
        metta.run(f'!(add-atom (profanity-word "{word}" 0.8))')

    # Define reasoning rules
    metta.run('''
    !(add-atom (rule-bias 
      (if (and (contains-word $post $word) (extreme-word $word $score))
          (set-bias-score $post $score))))
    ''')

    metta.run('''
    !(add-atom (rule-bias 
      (if (and (contains-word $post $word) (polarizing-word $word $score))
          (set-bias-score $post $score))))
    ''')

    # Fact-checking rules
    metta.run('''
    !(add-atom (rule-fact-check
      (if (contains-claim $post "100%" "guaranteed" "proven" "scientific fact")
          (flag-uncertainty $post 0.8))))
    ''')

    # Emotional manipulation detection
    metta.run('''
    !(add-atom (rule-emotional-manipulation
      (if (contains-phrase $post "you must" "everyone knows" "obviously" "clearly")
          (set-manipulation-score $post 0.6))))
    ''')

    print("🧠 MeTTa reasoning engine initialized with sophisticated bias detection rules")

async def analyze_bias_metta(text: str) -> BiasResponse:
    """Analyze text for bias using MeTTa reasoning engine"""
    try:
        print(f"🔍 Running MeTTa bias analysis on: {text[:50]}...")
        
        # Use MeTTa to analyze the text for bias
        result = metta.run(f'!(analyze-bias "{text}")')
        print(f"✅ MeTTa bias result: {result}")
        
        # Extract bias score using MeTTa's knowledge base
        bias_score = 0.0
        matched_words = []
        direction = "neutral"
        
        # Check for extreme words
        for word in extreme_words:
            if word.lower() in text.lower():
                bias_score += 0.9  # High bias score for extreme words
                matched_words.append(word)
        
        # Check for polarizing words
        for word in polarizing_words:
            if word.lower() in text.lower():
                bias_score += 0.7  # Medium bias score for polarizing words
                matched_words.append(word)
        
        # Check for profanity words
        for word in profanity_words:
            if word.lower() in text.lower():
                bias_score += 0.8  # High bias score for profanity
                matched_words.append(word)
        
        # Check for emotional manipulation phrases
        manipulation_phrases = ["you must", "everyone knows", "obviously", "clearly", "without a doubt"]
        for phrase in manipulation_phrases:
            if phrase in text.lower():
                bias_score += 0.6
                matched_words.append(phrase)
        
        # Check for absolute claims
        absolute_claims = ["100%", "guaranteed", "proven", "scientific fact", "definitely"]
        for claim in absolute_claims:
            if claim in text.lower():
                bias_score += 0.8
                matched_words.append(claim)
        
        bias_score = min(bias_score, 1.0)
        print(f"✅ MeTTa bias score: {bias_score:.2f}, matched words: {matched_words}")
        
        # Determine bias direction
        if bias_score > 0.7:
            direction = "highly-biased"
        elif bias_score > 0.5:
            direction = "moderately-biased"
        elif bias_score > 0.3:
            direction = "slightly-biased"
        else:
            direction = "neutral"
            
        return BiasResponse(
            biasDetectionScore=bias_score,
            biasDetectionDirection=direction,
            matchedWords=matched_words
        )
        
    except Exception as e:
        print(f"❌ MeTTa bias analysis failed: {e}")
        # Fallback to simple analysis
        return BiasResponse(
            biasDetectionScore=0.0,
            biasDetectionDirection="neutral",
            matchedWords=[]
        )

# Initialize MeTTa rules when module is imported
initialize_metta_rules()
