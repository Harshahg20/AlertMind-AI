# Quick Start Deployment Guide

## Prerequisites Checklist

- [ ] Google Cloud account created
- [ ] Google Cloud SDK (gcloud) installed and authenticated
- [ ] Docker installed and running
- [ ] Google AI API key obtained

## Fast Deployment (5 Steps)

### 1. Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:GCP_PROJECT_ID = "your-project-id"
$env:GOOGLE_AI_API_KEY = "your-api-key"
```

**Linux/Mac:**
```bash
export GCP_PROJECT_ID="your-project-id"
export GOOGLE_AI_API_KEY="your-api-key"
```

### 2. Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Deploy Backend

**Windows:**
```powershell
.\deploy.ps1 backend
```

**Linux/Mac:**
```bash
./deploy.sh backend
```

### 4. Deploy Frontend

**Windows:**
```powershell
.\deploy.ps1 frontend
```

**Linux/Mac:**
```bash
./deploy.sh frontend
```

### 5. Access Your Application

After deployment, you'll see URLs for both services. Open the frontend URL in your browser!

## Manual Deployment (Alternative)

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed manual steps.

## Local Testing

Test locally before deploying:

```bash
docker-compose up
```

Then visit `http://localhost:3000`

## Troubleshooting

- **Backend fails**: Check logs with `gcloud run logs read alertmind-backend --region us-central1`
- **Frontend can't connect**: Verify backend URL is correct in frontend build
- **CORS errors**: Update backend CORS settings with frontend URL

For more details, see [DEPLOYMENT.md](./DEPLOYMENT.md)

