from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import alerts, predictions, agentic, patch

app = FastAPI(
    title="CascadeGuard AI API",
    description="Intelligent Multi-Tenant Alert Orchestration with Agentic AI for MSPs",
    version="2.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(agentic.router, prefix="/api/agent", tags=["agentic-ai"])
app.include_router(patch.router, prefix="/api/patch", tags=["patch-management"])

@app.get("/")
def read_root():
    return {
        "message": "CascadeGuard AI API with Agentic Intelligence is running!",
        "status": "healthy",
        "version": "2.0.0",
        "features": [
            "Autonomous Cascade Prevention",
            "Cross-Client Pattern Learning", 
            "Intelligent Alert Correlation",
            "Proactive Failure Prevention",
            "Google Gemini AI Integration"
        ],
        "agentic_capabilities": {
            "autonomous_agent": "Active cascade prevention agent",
            "ai_analysis": "Google Gemini Flash integration",
            "prevention_executor": "Automated action execution",
            "pattern_learning": "Cross-client intelligence"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "cascadeguard-ai",
        "agentic_ai": "enabled",
        "version": "2.0.0"
    }

# To run: uvicorn main:app --reload --port 8000