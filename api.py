"""
FastAPI application with single /analyze/post endpoint
"""
from fastapi import FastAPI, HTTPException, APIRouter
from datetime import datetime
import uuid
from models import PostAnalysisRequest, PostAnalysisResponse
from metta_engine import analyze_bias_metta
from scoring_engine import calculate_readability, calculate_overall_score

router = APIRouter()

@router.post("/analyze/post", response_model=PostAnalysisResponse)
async def analyze_post(request: PostAnalysisRequest):
    """Complete post analysis including bias, readability, and overall rating"""
    try:
        # Generate UUID if not provided
        post_uuid = request.postUuid or str(uuid.uuid4())
        
        # Get bias analysis using MeTTa
        bias_result = await analyze_bias_metta(request.text)
        
        # Get readability analysis
        read_result = calculate_readability(request.text)
        
        # Calculate overall score (includes ASI:One comprehensive analysis)
        overall_score, score_breakdown = await calculate_overall_score(
            sentiment_score=0.0,  # Will be overridden by ASI analysis
            bias_score=bias_result.biasDetectionScore,
            readability_fk=read_result.readabilityFleschKincaid,
            originality_score=0.0,  # Will be overridden by ASI analysis
            plagiarism_score=0.0,  # Will be overridden by ASI analysis
            text=request.text
        )
        
        # Extract sentiment and topic information from ASI analysis
        sentiment_score = score_breakdown['sentiment']['final_score'] / 100 * 2 - 1  # Convert back to -1 to +1
        main_topic = "General"  # Will be updated from ASI analysis
        secondary_topics = ["AI", "Technology"]  # Will be updated from ASI analysis
        
        # Calculate originality and plagiarism from score breakdown
        originality = score_breakdown['originality']['final_score'] / 100
        plagiarism = score_breakdown['plagiarism']['final_score'] / 100
        
        # Extract AI detection score
        ai_detection_score = score_breakdown['authenticity']['ai_detection_score'] / 100
        
        # Prepare response
        response = PostAnalysisResponse(
            rating=overall_score,
            sentimentAnalysisScore=sentiment_score,
            biasDetectionScore=bias_result.biasDetectionScore,
            biasDetectionDirection=bias_result.biasDetectionDirection,
            originalityScore=originality,
            plagiarismScore=plagiarism,
            aiDetectionScore=ai_detection_score,
            readabilityFleschKincaid=read_result.readabilityFleschKincaid,
            readabilityGunningFog=read_result.readabilityGunningFog,
            readabilityScore=read_result.readabilityScore,
            mainTopic=main_topic,
            secondaryTopics=secondary_topics,
            explanation={
                "bias_analysis": bias_result.dict(),
                "readability_analysis": read_result.dict(),
                "score_breakdown": score_breakdown
            },
            postUuid=post_uuid
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post analysis failed: {str(e)}")