# AlertMind-AI - Quick Deployment Commands for Windows PowerShell
# ==================================================================

# ============================================
# VERIFY DEPLOYMENT STATUS
# ============================================

function Test-AlertMindDeployment {
    Write-Host "`n=== Testing AlertMind-AI Deployment ===" -ForegroundColor Yellow
    
    # Test Backend Health
    Write-Host "`n1. Backend Health Check..." -ForegroundColor Cyan
    try {
        $health = Invoke-RestMethod -Uri "https://alertmind-backend-qspwfgfhda-uc.a.run.app/health" -Method Get
        Write-Host "   ✅ Backend is healthy" -ForegroundColor Green
        Write-Host "   Status: $($health.status)" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ Backend health check failed" -ForegroundColor Red
    }
    
    # Test Backend API
    Write-Host "`n2. Backend API Test..." -ForegroundColor Cyan
    try {
        $alerts = Invoke-RestMethod -Uri "https://alertmind-backend-qspwfgfhda-uc.a.run.app/api/alerts" -Method Get
        Write-Host "   ✅ Backend API is working ($($alerts.Count) alerts)" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Backend API failed" -ForegroundColor Red
    }
    
    # Test Frontend
    Write-Host "`n3. Frontend Test..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "https://alertmind-frontend-qspwfgfhda-uc.a.run.app" -UseBasicParsing
        Write-Host "   ✅ Frontend is accessible (Status: $($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Frontend test failed" -ForegroundColor Red
    }
    
    Write-Host "`n=== Deployment Test Complete ===" -ForegroundColor Yellow
}

# ============================================
# REDEPLOY BACKEND
# ============================================

function Deploy-Backend {
    param(
        [string]$ApiKey = $env:GOOGLE_AI_API_KEY
    )
    
    Write-Host "`n=== Deploying Backend to Cloud Run ===" -ForegroundColor Yellow
    
    if (-not $ApiKey) {
        Write-Host "❌ GOOGLE_AI_API_KEY not set. Please provide API key." -ForegroundColor Red
        return
    }
    
    Push-Location backend
    
    Write-Host "`n1. Building Docker image (this will take 5-10 minutes)..." -ForegroundColor Cyan
    gcloud builds submit --tag gcr.io/alertmind-476814/alertmind-backend --timeout=30m
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n2. Deploying to Cloud Run..." -ForegroundColor Cyan
        
        # Create temp env vars file
        @"
CORS_ORIGINS: "http://localhost:3000,https://alertmind-frontend-qspwfgfhda-uc.a.run.app"
GOOGLE_AI_API_KEY: "$ApiKey"
"@ | Out-File -FilePath "../temp-backend-env.yaml" -Encoding UTF8
        
        gcloud run deploy alertmind-backend `
            --image gcr.io/alertmind-476814/alertmind-backend `
            --region us-central1 `
            --platform managed `
            --allow-unauthenticated `
            --port 443 `
            --memory 2Gi `
            --cpu 2 `
            --min-instances 1 `
            --max-instances 10 `
            --env-vars-file=../temp-backend-env.yaml
        
        Remove-Item "../temp-backend-env.yaml" -ErrorAction SilentlyContinue
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Backend deployed successfully!" -ForegroundColor Green
        }
    }
    
    Pop-Location
}

# ============================================
# REDEPLOY FRONTEND
# ============================================

function Deploy-Frontend {
    Write-Host "`n=== Deploying Frontend to Cloud Run ===" -ForegroundColor Yellow
    
    Push-Location frontend
    
    $backendUrl = "https://alertmind-backend-370935358441.us-central1.run.app"
    
    Write-Host "`n1. Building and deploying frontend (this will take 3-5 minutes)..." -ForegroundColor Cyan
    gcloud builds submit --config=cloudbuild.yaml --substitutions=_API_URL="$backendUrl/api" .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Frontend deployed successfully!" -ForegroundColor Green
        Write-Host "`nFrontend URL: https://alertmind-frontend-qspwfgfhda-uc.a.run.app" -ForegroundColor Cyan
    }
    
    Pop-Location
}

# ============================================
# VIEW LOGS
# ============================================

function Get-BackendLogs {
    param([int]$Limit = 50)
    Write-Host "`n=== Backend Logs (last $Limit entries) ===" -ForegroundColor Yellow
    gcloud run services logs read alertmind-backend --region us-central1 --limit $Limit
}

function Get-FrontendLogs {
    param([int]$Limit = 50)
    Write-Host "`n=== Frontend Logs (last $Limit entries) ===" -ForegroundColor Yellow
    gcloud run services logs read alertmind-frontend --region us-central1 --limit $Limit
}

# ============================================
# UPDATE CORS
# ============================================

function Update-BackendCors {
    param(
        [string]$FrontendUrl = "https://alertmind-frontend-qspwfgfhda-uc.a.run.app",
        [string]$ApiKey = $env:GOOGLE_AI_API_KEY
    )
    
    Write-Host "`n=== Updating Backend CORS Configuration ===" -ForegroundColor Yellow
    
    if (-not $ApiKey) {
        Write-Host "❌ GOOGLE_AI_API_KEY not set" -ForegroundColor Red
        return
    }
    
    # Create temp env vars file
    @"
CORS_ORIGINS: "http://localhost:3000,$FrontendUrl"
GOOGLE_AI_API_KEY: "$ApiKey"
"@ | Out-File -FilePath "temp-cors-env.yaml" -Encoding UTF8
    
    gcloud run services update alertmind-backend `
        --region us-central1 `
        --env-vars-file=temp-cors-env.yaml
    
    Remove-Item "temp-cors-env.yaml" -ErrorAction SilentlyContinue
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ CORS configuration updated!" -ForegroundColor Green
    }
}

# ============================================
# SERVICE STATUS
# ============================================

function Get-ServiceStatus {
    Write-Host "`n=== AlertMind-AI Service Status ===" -ForegroundColor Yellow
    
    Write-Host "`nBackend:" -ForegroundColor Cyan
    gcloud run services describe alertmind-backend --region us-central1 --format="table(status.url,status.traffic[0].latestRevision,status.traffic[0].percent)"
    
    Write-Host "`nFrontend:" -ForegroundColor Cyan
    gcloud run services describe alertmind-frontend --region us-central1 --format="table(status.url,status.traffic[0].latestRevision,status.traffic[0].percent)"
}

# ============================================
# USAGE EXAMPLES
# ============================================

Write-Host @"

AlertMind-AI Deployment Commands Loaded!

Usage:
------
Test-AlertMindDeployment     # Test if everything is working
Deploy-Backend               # Redeploy backend
Deploy-Frontend              # Redeploy frontend
Get-BackendLogs              # View backend logs
Get-FrontendLogs             # View frontend logs
Update-BackendCors           # Update CORS configuration
Get-ServiceStatus            # Check service status

Example:
--------
# Test deployment
Test-AlertMindDeployment

# Redeploy backend
Deploy-Backend -ApiKey "YOUR_API_KEY"

# View logs
Get-BackendLogs -Limit 100

"@ -ForegroundColor Gray

