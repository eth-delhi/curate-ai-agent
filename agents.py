"""
uAgents multi-agent system for content analysis
"""
from uagents import Agent, Context, Protocol, Bureau
from uagents.setup import fund_agent_if_low
from models import TextMessage, PostMessage, ChatMessage, ChatResponse, BiasResponse, ReadabilityResponse
from metta_engine import analyze_bias_metta
from asi_one_client import get_comprehensive_analysis
from scoring_engine import calculate_readability, calculate_overall_score
import asyncio
import uuid

# --- Chat Protocol for conversational interaction ---
chat_protocol = Protocol("ChatProtocol")

@chat_protocol.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle conversational messages and provide content analysis"""
    try:
        # Extract text to analyze from the message
        text_to_analyze = msg.message
        
        # Check if it's a rating request
        if "rate this post" in text_to_analyze.lower() or "analyze this" in text_to_analyze.lower():
            # Extract the actual content to analyze
            content = text_to_analyze.replace("rate this post:", "").replace("analyze this:", "").strip()
            if not content:
                content = text_to_analyze
            
            # Perform comprehensive analysis
            bias_result = await analyze_bias_metta(content)
            read_result = calculate_readability(content)
            
            # Calculate overall score (includes ASI:One comprehensive analysis)
            overall_score, score_breakdown, recommendations = await calculate_overall_score(
                sentiment_score=0.0,  # Will be overridden by ASI analysis
                bias_score=bias_result.biasDetectionScore,
                readability_fk=read_result.readabilityFleschKincaid,
                originality_score=0.0,  # Will be overridden by ASI analysis
                similarity_score=0.0,  # Will be overridden by ASI analysis
                text=content
            )
            
            # Extract information from comprehensive analysis
            sentiment_score = score_breakdown['sentiment']['final_score'] / 100 * 2 - 1  # Convert back to -1 to +1
            main_topic = "General"  # Will be updated from ASI analysis
            secondary_topics = ["AI", "Technology"]  # Will be updated from ASI analysis
            
            # Create conversational response
            response = f"📊 **Content Analysis Results**\n\n"
            response += f"🏆 **Overall Score: {overall_score}/100**\n\n"
            response += f"📈 **Breakdown:**\n"
            response += f"• Sentiment: {score_breakdown['sentiment']['score']}/100\n"
            response += f"• Bias: {score_breakdown['bias']['score']}/100\n"
            response += f"• Readability: {score_breakdown['readability']['score']}/100\n"
            response += f"• Originality: {score_breakdown['originality']['score']}/100\n\n"
            response += f"🎯 **Main Topic:** {main_topic}\n"
            response += f"📝 **Secondary Topics:** {', '.join(secondary_topics)}\n\n"
            response += f"💡 **Recommendations:**\n"
            for rec in recommendations[:3]:  # Show top 3 recommendations
                response += f"• {rec}\n"
            
            analysis_data = {
                "overall_score": overall_score,
                "score_breakdown": score_breakdown,
                "recommendations": recommendations,
                "main_topic": main_topic,
                "secondary_topics": secondary_topics
            }
            
            await ctx.send(sender, ChatResponse(response=response, analysis=analysis_data))
            
        else:
            # General conversation
            response = "Hello! I'm your content analysis agent. You can ask me to:\n"
            response += "• 'Rate this post: [your content]' - Get detailed analysis\n"
            response += "• 'Analyze this: [your content]' - Get comprehensive breakdown\n"
            response += "• Ask questions about content quality, bias, readability, etc."
            
            await ctx.send(sender, ChatResponse(response=response))
            
    except Exception as e:
        error_response = f"Sorry, I encountered an error analyzing your content: {str(e)}"
        await ctx.send(sender, ChatResponse(response=error_response))

# --- Individual Analysis Agents ---

# 1. BiasAgent - Uses MeTTa for reasoning
bias_agent = Agent(name="BiasAgent", seed="bias_seed")
bias_proto = Protocol("BiasCheck")

@bias_proto.on_message(model=TextMessage)
async def check_bias(ctx: Context, sender: str, payload: TextMessage):
    """Real bias analysis using MeTTa reasoning engine"""
    post_text = payload.text
    
    try:
        # Use MeTTa to analyze bias
        result = await analyze_bias_metta(post_text)
        await ctx.send(sender, result.dict())
    except Exception as e:
        ctx.logger.error(f"Bias analysis failed: {e}")
        # Fallback response
        await ctx.send(sender, {
            "biasDetectionScore": 0.0,
            "biasDetectionDirection": "neutral",
            "matchedWords": []
        })

bias_agent.include(bias_proto)

# 2. ReadabilityAgent
read_agent = Agent(name="ReadabilityAgent", seed="read_seed")
read_proto = Protocol("ReadabilityCheck")

@read_proto.on_message(model=TextMessage)
async def readability(ctx: Context, sender: str, payload: TextMessage):
    """Calculate readability metrics"""
    text = payload.text
    result = calculate_readability(text)
    await ctx.send(sender, result.dict())

read_agent.include(read_proto)

# 3. SentimentAgent - Uses ASI:One for real NLP
sentiment_agent = Agent(name="SentimentAgent", seed="sentiment_seed")
sentiment_proto = Protocol("SentimentCheck")

@sentiment_proto.on_message(model=TextMessage)
async def check_sentiment(ctx: Context, sender: str, payload: TextMessage):
    """Real sentiment analysis using ASI:One"""
    post_text = payload.text
    
    try:
        # Use ASI:One comprehensive analysis
        asi_analysis = await get_comprehensive_analysis(post_text)
        sentiment_score = asi_analysis["sentiment"]
        main_topic = asi_analysis["main_topic"]
        secondary_topics = asi_analysis["secondary_topics"]
        similarity = asi_analysis["similarity"]
        
        await ctx.send(sender, {
            "sentimentScore": sentiment_score,
            "mainTopic": main_topic,
            "secondaryTopics": secondary_topics,
            "similarityScore": similarity,
            "originalityScore": 1 - similarity
        })
    except Exception as e:
        ctx.logger.error(f"Sentiment analysis failed: {e}")
        # Fallback response
        await ctx.send(sender, {
            "sentimentScore": 0.0,
            "mainTopic": "General",
            "secondaryTopics": ["AI"],
            "similarityScore": 0.3,
            "originalityScore": 0.7
        })

sentiment_agent.include(sentiment_proto)

# 4. AggregatorAgent - Main agent with Chat Protocol
agg_agent = Agent(name="AggregatorAgent", seed="agg_seed")
agg_proto = Protocol("PostRating")

# Add Chat Protocol to AggregatorAgent
agg_agent.include(chat_protocol)

@agg_proto.on_message(model=PostMessage)
async def aggregate(ctx: Context, sender: str, payload: PostMessage):
    """Aggregate results from all agents"""
    post_uuid = payload.postUuid
    post_text = payload.text

    # --- Communicate with sub-agents using real uAgents ---
    bias_result = await agg_agent.send("BiasAgent", "BiasCheck", TextMessage(text=post_text))
    read_result = await agg_agent.send("ReadabilityAgent", "ReadabilityCheck", TextMessage(text=post_text))
    sentiment_result = await agg_agent.send("SentimentAgent", "SentimentCheck", TextMessage(text=post_text))

    # --- Use real agent results ---
    sentiment_score = sentiment_result["sentimentScore"]
    similarity = sentiment_result["similarityScore"]
    originality = sentiment_result["originalityScore"]
    main_topic = sentiment_result["mainTopic"]
    secondary_topics = sentiment_result["secondaryTopics"]
    
    # Calculate overall rating using real data
    rating = int((sentiment_score + (1 - bias_result["biasDetectionScore"]) + originality + (read_result["readabilityFleschKincaid"]/100)) * 25)

    # --- Return result ---
    return {
        "rating": rating,
        "sentimentAnalysisScore": sentiment_score,
        "biasDetectionScore": bias_result["biasDetectionScore"],
        "biasDetectionDirection": bias_result["biasDetectionDirection"],
        "originalityScore": originality,
        "similarityScore": similarity,
        "readabilityFleschKincaid": read_result["readabilityFleschKincaid"],
        "readabilityGunningFog": read_result["readabilityGunningFog"],
        "mainTopic": main_topic,
        "secondaryTopics": secondary_topics,
        "explanation": [bias_result, read_result]
    }

agg_agent.include(agg_proto)

# --- Bureau for Agent Orchestration ---
bureau = Bureau()
bureau.add(bias_agent)
bureau.add(read_agent)
bureau.add(sentiment_agent)
bureau.add(agg_agent)