from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import alerts, predictions, agentic, patch, alert_correlation_agent, autonomous_decision, prevention_execution

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
app.include_router(alert_correlation_agent.router, prefix="/api/alert-correlation", tags=["alert-correlation-agent"])
app.include_router(autonomous_decision.router, prefix="/api/autonomous-decision", tags=["autonomous-decision-agent"])
app.include_router(prevention_execution.router, prefix="/api/prevention-execution", tags=["prevention-execution-agent"])

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
            "Google Gemini AI Integration",
            "Alert Correlation Agent with Sentence Transformers",
            "Autonomous Decision Agent with Gemini 1.5 Pro",
            "Prevention Execution Agent with Deterministic Orchestration"
        ],
        "agentic_capabilities": {
            "autonomous_agent": "Active cascade prevention agent",
            "ai_analysis": "Google Gemini Flash integration",
            "prevention_executor": "Automated action execution",
            "pattern_learning": "Cross-client intelligence",
            "alert_correlation_agent": "Sentence transformer-based alert clustering",
            "autonomous_decision_agent": "Gemini 1.5 Pro + deterministic business logic",
            "prevention_execution_agent": "Deterministic orchestration + tiny LLM summaries"
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