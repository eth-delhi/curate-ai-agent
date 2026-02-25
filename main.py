"""
Main application entry point
"""
import uvicorn
from api import router
from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI(
    title="Fetch.ai ASI Content Analysis Agent",
    description="AI-powered content analysis using Fetch.ai ASI",
    version="2.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    print("🚀 Starting Fetch.ai ASI Content Analysis API...")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔍 Single endpoint: POST http://localhost:8001/analyze/post")
    print("🤖 Powered by Fetch.ai ASI...")
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8001)
