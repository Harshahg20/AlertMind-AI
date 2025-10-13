from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import alerts, predictions

app = FastAPI(
    title="CascadeGuard AI API",
    description="Intelligent Multi-Tenant Alert Orchestration for MSPs",
    version="1.0.0"
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

@app.get("/")
def read_root():
    return {
        "message": "CascadeGuard AI API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cascadeguard-ai"}

# To run: uvicorn main:app --reload --port 8000