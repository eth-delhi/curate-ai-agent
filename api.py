"""
FastAPI application with single /analyze/post endpoint
"""
from fastapi import FastAPI, HTTPException, APIRouter
from datetime import datetime
import uuid
from models import PostAnalysisRequest, PostAnalysisResponse
from scoring_engine import calculate_readability, calculate_overall_score
from asi_one_client import get_comprehensive_analysis
from metta_engine import analyze_bias_metta

router = APIRouter()

@router.post("/analyze/post", response_model=PostAnalysisResponse)
async def analyze_post(request: PostAnalysisRequest):
    """Complete post analysis using Fetch.ai ASI-based scoring system"""
    try:
        # Generate UUID if not provided
        post_uuid = request.postUuid or str(uuid.uuid4())
        
        # Get comprehensive analysis from ASI
        asi_analysis = await get_comprehensive_analysis(request.text)
        
        # Get bias analysis from MeTTa engine
        bias_result = await analyze_bias_metta(request.text)
        
        # Get readability analysis
        read_result = calculate_readability(request.text)
        
        # Calculate overall score using ASI engine
        overall_score, score_breakdown, recommendations = await calculate_overall_score(
            sentiment_score=asi_analysis.get("sentiment", 0.0),
            bias_score=bias_result.biasDetectionScore,
            readability_fk=read_result.readabilityFleschKincaid,
            originality_score=1.0 - asi_analysis.get("plagiarism", 0.5),  # Convert plagiarism to originality
            plagiarism_score=asi_analysis.get("plagiarism", 0.5),
            text=request.text
        )
        
        # Extract scores
        sentiment_score = asi_analysis.get("sentiment", 0.0)
        bias_score = bias_result.biasDetectionScore
        originality = 1.0 - asi_analysis.get("plagiarism", 0.5)
        plagiarism = asi_analysis.get("plagiarism", 0.5)
        ai_detection_score = asi_analysis.get("ai_detection", 0.0)
        
        # Get topics from ASI analysis
        main_topic = asi_analysis.get("main_topic", "General")
        secondary_topics = asi_analysis.get("secondary_topics", ["General"])
        
        # Prepare response
        response = PostAnalysisResponse(
            rating=overall_score,
            sentimentAnalysisScore=sentiment_score,
            biasDetectionScore=bias_score,
            biasDetectionDirection=bias_result.biasDetectionDirection,
            originalityScore=originality,
            plagiarismScore=plagiarism,
            aiDetectionScore=ai_detection_score,
            readabilityFleschKincaid=read_result.readabilityFleschKincaid,
            readabilityGunningFog=read_result.readabilityGunningFog,
            readabilityScore=read_result.readabilityScore,
            mainTopic=main_topic,
            secondaryTopics=secondary_topics,
            explanation=score_breakdown,
            postUuid=post_uuid
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")