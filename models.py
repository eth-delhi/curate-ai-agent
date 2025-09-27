"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- Core Message Models for uAgents ---
class TextMessage(BaseModel):
    text: str

class PostMessage(BaseModel):
    text: str
    postUuid: str

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    analysis: Optional[Dict[str, Any]] = None

# --- Analysis Response Models ---
class BiasResponse(BaseModel):
    biasDetectionScore: float
    biasDetectionDirection: str
    matchedWords: List[str] = []

class ReadabilityResponse(BaseModel):
    readabilityFleschKincaid: float
    readabilityGunningFog: float
    readabilityScore: float  # Comprehensive 0-100 score

# --- Main API Request/Response Models ---
class PostAnalysisRequest(BaseModel):
    text: str
    postUuid: Optional[str] = None

class PostAnalysisResponse(BaseModel):
    rating: int
    sentimentAnalysisScore: float
    biasDetectionScore: float
    biasDetectionDirection: str
    originalityScore: float
    plagiarismScore: float
    aiDetectionScore: float
    readabilityFleschKincaid: float
    readabilityGunningFog: float
    readabilityScore: float
    mainTopic: str
    secondaryTopics: List[str]
    explanation: Dict[str, Any]
    postUuid: str