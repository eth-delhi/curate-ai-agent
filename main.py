"""
Main application entry point
"""
import uvicorn
import threading
from agents import bureau
from api import router
from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI(
    title="ASI Alliance Content Analysis Agent",
    description="AI-powered content analysis using ASI:One, MeTTa, and uAgents",
    version="1.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    print("🚀 Starting ASI Agent API with Real uAgents + MeTTa + ASI:One...")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔍 Single endpoint: POST http://localhost:8001/analyze/post")
    print("🤖 Agents running on Agentverse...")
    
    # Start the Bureau in the background
    bureau_thread = threading.Thread(target=bureau.run, daemon=True)
    bureau_thread.start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8001)
