# AlertMind-AI Google Cloud Deployment Script (PowerShell)
# Usage: .\deploy.ps1 [backend|frontend|all]

param(
    [Parameter(Position=0)]
    [ValidateSet("backend", "frontend", "all")]
    [string]$Service = "all"
)

$ErrorActionPreference = "Stop"

# Configuration - Update these variables
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "your-project-id" }
$REGION = if ($env:GCP_REGION) { $env:GCP_REGION } else { "us-central1" }
$GOOGLE_AI_API_KEY = $env:GOOGLE_AI_API_KEY

if ($PROJECT_ID -eq "your-project-id") {
    Write-Host "Error: Please set GCP_PROJECT_ID environment variable or update the script" -ForegroundColor Red
    exit 1
}

function Deploy-Backend {
    Write-Host "🚀 Deploying backend..." -ForegroundColor Cyan
    
    Push-Location backend
    
    # Build and push
    gcloud builds submit --tag "gcr.io/${PROJECT_ID}/alertmind-backend"
    
    # Deploy
    $deployArgs = @(
        "run", "deploy", "alertmind-backend",
        "--image", "gcr.io/${PROJECT_ID}/alertmind-backend",
        "--region", $REGION,
        "--platform", "managed",
        "--allow-unauthenticated",
        "--port", "8000",
        "--memory", "2Gi",
        "--cpu", "2",
        "--min-instances", "1",
        "--max-instances", "10"
    )
    
    if ($GOOGLE_AI_API_KEY) {
        $deployArgs += "--set-env-vars", "GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}"
    } else {
        Write-Host "Warning: GOOGLE_AI_API_KEY not set. Deploying without API key." -ForegroundColor Yellow
    }
    
    & gcloud @deployArgs
    
    # Get backend URL
    $script:BACKEND_URL = (gcloud run services describe alertmind-backend --region $REGION --format 'value(status.url)')
    Write-Host "✅ Backend deployed at: ${script:BACKEND_URL}" -ForegroundColor Green
    
    Pop-Location
}

function Deploy-Frontend {
    if (-not $script:BACKEND_URL) {
        Write-Host "Error: Backend URL not set. Please deploy backend first or set BACKEND_URL environment variable." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🚀 Deploying frontend..." -ForegroundColor Cyan
    Write-Host "   Using backend URL: ${script:BACKEND_URL}" -ForegroundColor Gray
    
    Push-Location frontend
    
    # Build Docker image
    docker build --build-arg "REACT_APP_API_URL=${script:BACKEND_URL}/api" -t "gcr.io/${PROJECT_ID}/alertmind-frontend" .
    
    # Push to Container Registry
    docker push "gcr.io/${PROJECT_ID}/alertmind-frontend"
    
    # Deploy
    gcloud run deploy alertmind-frontend `
        --image "gcr.io/${PROJECT_ID}/alertmind-frontend" `
        --region $REGION `
        --platform managed `
        --allow-unauthenticated `
        --port 80 `
        --memory 512Mi `
        --cpu 1 `
        --min-instances 0 `
        --max-instances 10
    
    # Get frontend URL
    $FRONTEND_URL = (gcloud run services describe alertmind-frontend --region $REGION --format 'value(status.url)')
    Write-Host "✅ Frontend deployed at: ${FRONTEND_URL}" -ForegroundColor Green
    
    Pop-Location
    
    # Update backend CORS to allow frontend
    Write-Host "🔄 Updating backend CORS settings..." -ForegroundColor Cyan
    gcloud run services update alertmind-backend `
        --set-env-vars "CORS_ORIGINS=${FRONTEND_URL}" `
        --region $REGION
    
    Write-Host ""
    Write-Host "🎉 Deployment complete!" -ForegroundColor Green
    Write-Host "   Frontend: ${FRONTEND_URL}" -ForegroundColor Green
    Write-Host "   Backend: ${script:BACKEND_URL}" -ForegroundColor Green
}

switch ($Service) {
    "backend" {
        Deploy-Backend
    }
    "frontend" {
        Deploy-Frontend
    }
    "all" {
        Deploy-Backend
        Deploy-Frontend
    }
}

