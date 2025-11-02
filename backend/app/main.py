from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
from app.api import alerts, predictions, agentic, patch, alert_correlation_agent, autonomous_decision, prevention_execution, enhanced_agentic, enhanced_patch_management, it_administrative_tasks
import os
import google.generativeai as genai

# Load environment variables from files in priority order
# 1) backend/.env (standard)
# 2) backend/settings.env (fallback when dotfiles are restricted)
# 3) project root .env
backend_dir = Path(__file__).resolve().parents[1]
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir / "settings.env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(
    title="CascadeGuard AI API",
    description="Intelligent Multi-Tenant Alert Orchestration with Agentic AI for MSPs",
    version="2.0.0",
    redirect_slashes=False  # Disable automatic trailing slash redirects to avoid HTTP redirects
)

# Enable CORS for React frontend
# Allow CORS origins from environment variable (comma-separated) or default to localhost
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# Automatically allow all Cloud Run frontend origins (for production deployments)
# This handles cases where frontend URLs change or multiple frontend instances exist
# Use regex pattern to match any Cloud Run service (both .run.app and .a.run.app domains)
cloud_run_regex = r"https://.*\.run\.app|https://.*\.a\.run\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cloud_run_regex,  # Allow all Cloud Run services
    allow_credentials=False,  # Set to False since we're not using cookies/auth - this simplifies CORS
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verify Google AI configuration at startup (graceful - does not crash if unavailable)
@app.on_event("startup")
async def verify_gemini_configuration():
    import logging
    logger = logging.getLogger(__name__)
    
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key or api_key == "demo_key":
        logger.warning("⚠️ GOOGLE_AI_API_KEY not set or invalid. Server will run in fallback mode.")
        logger.info("ℹ️ Set a valid GOOGLE_AI_API_KEY environment variable for AI-powered features.")
        logger.info("ℹ️ All services will work with deterministic fallback algorithms.")
        return
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        # Lightweight readiness probe (skip if it fails)
        try:
            await model.generate_content_async("healthcheck")
            logger.info("✅ Gemini API key validated successfully")
        except Exception as probe_error:
            logger.warning(f"⚠️ Gemini API key validation failed (will use fallback mode): {probe_error}")
            logger.info("ℹ️ Server will continue with fallback algorithms")
    except Exception as e:
        logger.warning(f"⚠️ Gemini configuration check failed (will use fallback mode): {e}")
        logger.info("ℹ️ Server will continue running with deterministic fallback algorithms")
        # Do not raise - allow server to start in fallback mode

# Include API routes
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(agentic.router, prefix="/api/agent", tags=["agentic-ai"])
app.include_router(enhanced_agentic.router, prefix="/api/agent/enhanced", tags=["enhanced-agentic-ai"])
app.include_router(patch.router, prefix="/api/patch", tags=["patch-management"])
app.include_router(alert_correlation_agent.router, prefix="/api/alert-correlation", tags=["alert-correlation-agent"])
app.include_router(autonomous_decision.router, prefix="/api/autonomous-decision", tags=["autonomous-decision-agent"])
app.include_router(prevention_execution.router, prefix="/api/prevention-execution", tags=["prevention-execution-agent"])
app.include_router(enhanced_patch_management.router, prefix="/api/enhanced-patch", tags=["enhanced-patch-management"])
app.include_router(it_administrative_tasks.router, prefix="/api/it-admin", tags=["it-administrative-tasks"])

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