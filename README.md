Activate VENV
source venv/bin/activate

# 🏗️ ASI Alliance Content Analysis Agent - Refactored Architecture

## 📁 **Modular File Structure**

The codebase has been refactored into a clean, modular architecture following best practices:

```
asi-agent/
├── main.py                 # Application entry point
├── api.py                  # FastAPI routes and endpoints
├── agents.py               # uAgents multi-agent system
├── models.py               # Pydantic data models
├── database.py             # Database models and configuration
├── metta_engine.py         # MeTTa reasoning engine
├── asi_one_client.py       # ASI:One API client
├── scoring_engine.py       # Content scoring and recommendations
├── requirements.txt        # Python dependencies
├── agent.yaml             # Agentverse deployment manifest
└── README_REFACTORED.md   # This file
```

## 🎯 **Separation of Concerns**

### **1. `main.py` - Application Entry Point**

- **Purpose**: Application bootstrap and server startup
- **Responsibilities**:
  - Start uAgents Bureau
  - Launch FastAPI server
  - Handle graceful shutdown

### **2. `api.py` - FastAPI Application**

- **Purpose**: REST API endpoints and HTTP handling
- **Responsibilities**:
  - Define API routes (`/analyze/bias`, `/score/overall`, etc.)
  - Request/response validation
  - Error handling and HTTP status codes
  - Database integration for persistence

### **3. `agents.py` - Multi-Agent System**

- **Purpose**: uAgents coordination and communication
- **Responsibilities**:
  - Define individual agents (BiasAgent, ReadabilityAgent, etc.)
  - Implement agent protocols and message handlers
  - Coordinate agent-to-agent communication
  - Chat Protocol for conversational interface

### **4. `models.py` - Data Models**

- **Purpose**: Pydantic models for type safety and validation
- **Responsibilities**:
  - API request/response models
  - Agent message models
  - Data validation and serialization

### **5. `database.py` - Data Persistence**

- **Purpose**: Database models and connection management
- **Responsibilities**:
  - SQLAlchemy ORM models
  - Database connection configuration
  - Session management utilities

### **6. `metta_engine.py` - Reasoning Engine**

- **Purpose**: MeTTa-based bias detection and reasoning
- **Responsibilities**:
  - Initialize MeTTa knowledge base
  - Define bias detection rules
  - Analyze content for bias, manipulation, and profanity
  - Sophisticated reasoning logic

### **7. `asi_one_client.py` - External API Integration**

- **Purpose**: ASI:One API integration
- **Responsibilities**:
  - Sentiment analysis via ASI:One
  - Topic extraction and classification
  - Similarity analysis
  - Fallback mechanisms when API is unavailable

### **8. `scoring_engine.py` - Content Scoring**

- **Purpose**: Content quality assessment and recommendations
- **Responsibilities**:
  - Readability calculations (Flesch-Kincaid, Gunning Fog)
  - Overall score computation
  - Recommendation generation
  - Score normalization and weighting

## 🚀 **Benefits of This Architecture**

### **✅ Maintainability**

- **Single Responsibility**: Each file has one clear purpose
- **Easy to Modify**: Changes to one component don't affect others
- **Clear Dependencies**: Easy to see what depends on what

### **✅ Testability**

- **Unit Testing**: Each module can be tested independently
- **Mocking**: Easy to mock dependencies for testing
- **Isolation**: Components can be tested in isolation

### **✅ Scalability**

- **Modular Deployment**: Components can be deployed separately
- **Easy Extension**: New features can be added as new modules
- **Performance**: Can optimize individual components

### **✅ Code Quality**

- **Type Safety**: Pydantic models provide runtime type checking
- **Documentation**: Each module is self-documenting
- **Standards**: Follows Python and FastAPI best practices

## 🔧 **How to Run**

### **1. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **2. Set Environment Variables**

```bash
export ASI_API_KEY="your_asi_one_api_key"
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"
```

### **3. Start the Application**

```bash
python main.py
```

### **4. Alternative: Run Individual Components**

```bash
# Just the API server
python -c "from api import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8001)"

# Just the agents
python -c "from agents import bureau; bureau.run()"
```

## 🧪 **Testing Individual Components**

### **Test MeTTa Engine**

```python
from metta_engine import analyze_bias_metta
result = await analyze_bias_metta("This is fucking amazing!")
print(result)
```

### **Test ASI:One Client**

```python
from asi_one_client import get_sentiment_analysis
sentiment = await get_sentiment_analysis("I love this!")
print(sentiment)
```

### **Test Scoring Engine**

```python
from scoring_engine import calculate_overall_score
score, breakdown, recs = calculate_overall_score(0.8, 0.2, 65.0, 0.7, 0.3)
print(f"Score: {score}, Recommendations: {recs}")
```

## 📊 **API Endpoints**

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /analyze/bias` - Bias analysis only
- `POST /analyze/readability` - Readability analysis only
- `POST /analyze/post` - Complete post analysis
- `POST /score/overall` - Overall score with breakdown

## 🤖 **Agent Communication**

The multi-agent system uses real uAgents communication:

```python
# Agent-to-agent communication
bias_result = await agg_agent.send("BiasAgent", "BiasCheck", TextMessage(text=content))
read_result = await agg_agent.send("ReadabilityAgent", "ReadabilityCheck", TextMessage(text=content))
sentiment_result = await agg_agent.send("SentimentAgent", "SentimentCheck", TextMessage(text=content))
```

## 🎉 **Key Improvements**

1. **Modular Design**: Each component has a single responsibility
2. **Type Safety**: Pydantic models ensure data integrity
3. **Testability**: Components can be tested independently
4. **Maintainability**: Easy to modify and extend
5. **Documentation**: Self-documenting code structure
6. **Best Practices**: Follows Python and FastAPI conventions

This refactored architecture makes the codebase much more professional, maintainable, and ready for production deployment! 🚀
