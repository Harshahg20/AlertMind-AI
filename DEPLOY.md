# Google Cloud Run Deployment Guide

Simple deployment guide for AlertMind to Google Cloud Run.

## Prerequisites

1. **Google Cloud SDK**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Docker** - Install from https://docs.docker.com/get-docker/

3. **Authentication**
   ```bash
   gcloud auth login
   gcloud config set project alert-mind
   ```

## Quick Deploy

Deploy everything (backend + frontend):
```bash
./deploy.sh
```

Deploy backend only:
```bash
./deploy-backend.sh
```

Deploy frontend only (requires backend deployed first):
```bash
./deploy-frontend.sh
```

## What Gets Deployed

### Backend Service
- **Name**: `alertmind-backend`
- **Port**: 8080
- **Memory**: 2Gi
- **CPU**: 2
- **Region**: us-central1

### Frontend Service
- **Name**: `alertmind-frontend`
- **Port**: 8080
- **Memory**: 512Mi
- **CPU**: 1
- **Region**: us-central1

## Manual Deployment

### Backend
```bash
gcloud builds submit --config=cloudbuild-backend.yaml \
    --substitutions=_GOOGLE_AI_API_KEY="YOUR_KEY",_CORS_ORIGINS="" \
    --project=alert-mind
```

### Frontend
```bash
# Get backend URL first
BACKEND_URL=$(gcloud run services describe alertmind-backend --region=us-central1 --format="value(status.url)")

# Deploy frontend
gcloud builds submit --config=cloudbuild-frontend.yaml \
    --substitutions=_API_URL="$BACKEND_URL/api" \
    --project=alert-mind
```

## View Logs

```bash
# Backend logs
gcloud run logs tail alertmind-backend --region=us-central1

# Frontend logs
gcloud run logs tail alertmind-frontend --region=us-central1
```

## Update Services

Just run the deploy scripts again - they update existing services.

## Environment Variables

Update backend environment variables:
```bash
gcloud run services update alertmind-backend \
    --update-env-vars="GOOGLE_AI_API_KEY=your_key,CORS_ORIGINS=https://frontend-url" \
    --region=us-central1 \
    --project=alert-mind
```

## Troubleshooting

**Build fails?**
- Check logs: `gcloud builds list --limit=5`
- Verify Dockerfiles are correct
- Check API keys are valid

**Service not starting?**
- Check logs: `gcloud run logs tail [service-name] --region=us-central1`
- Verify PORT is set to 8080
- Check environment variables

**Frontend can't connect to backend?**
- Verify backend URL in frontend build
- Check CORS settings on backend
- Ensure frontend URL is in backend's CORS_ORIGINS

## Cloud Console

View services: https://console.cloud.google.com/run?project=alert-mind

