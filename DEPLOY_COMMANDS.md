# Simple Deployment Commands (Local Docker Build)

This guide uses local Docker builds and direct gcloud commands - no YAML files needed!

## Prerequisites

1. **Docker Desktop running** ✅
2. **Google Cloud SDK installed**
   ```bash
   gcloud --version
   ```
3. **Authenticated with Google Cloud**
   ```bash
   gcloud auth login
   gcloud config set project alert-mind
   ```

## Step 1: Deploy Backend

```bash
./deploy-backend-direct.sh
```

**What it does:**

1. Builds Docker image locally from `backend/Dockerfile`
2. Tags image with timestamp
3. Pushes to Google Container Registry
4. Deploys to Cloud Run
5. Shows service URL

**During deployment:**

- You'll be prompted for Google AI API key (optional - press Enter to skip)

**Expected output:**

```
✅ Backend deployed successfully!
📊 Service URL: https://alertmind-backend-xxxxx-uc.a.run.app
```

## Step 2: Test Backend

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe alertmind-backend --region=us-central1 --format="value(status.url)")

# Test health endpoint
curl $BACKEND_URL/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "cascadeguard-ai",
  "agentic_ai": "enabled",
  "version": "2.0.0"
}
```

## Step 3: Deploy Frontend

**Wait until backend is working, then:**

```bash
./deploy-frontend-direct.sh
```

**What it does:**

1. Gets backend URL automatically
2. Builds Docker image locally with backend URL baked in
3. Pushes to Google Container Registry
4. Deploys to Cloud Run
5. Updates backend CORS automatically
6. Shows service URL

**Expected output:**

```
✅ Frontend deployed successfully!
📊 Service URL: https://alertmind-frontend-xxxxx-uc.a.run.app
```

## Step 4: Open Frontend

```bash
FRONTEND_URL=$(gcloud run services describe alertmind-frontend --region=us-central1 --format="value(status.url)")
open $FRONTEND_URL
# OR just open: https://alertmind-frontend-xxxxx-uc.a.run.app
```

## Manual Commands (Alternative)

If you prefer to run commands manually:

### Backend Deployment

```bash
# 1. Configure Docker auth
gcloud auth configure-docker

# 2. Build image locally
cd backend
docker build -t gcr.io/alert-mind/alertmind-backend:latest .

# 3. Tag with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker tag gcr.io/alert-mind/alertmind-backend:latest gcr.io/alert-mind/alertmind-backend:$TIMESTAMP

# 4. Push to GCR
docker push gcr.io/alert-mind/alertmind-backend:latest
docker push gcr.io/alert-mind/alertmind-backend:$TIMESTAMP

# 5. Deploy to Cloud Run
gcloud run deploy alertmind-backend \
    --image gcr.io/alert-mind/alertmind-backend:$TIMESTAMP \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars "GOOGLE_AI_API_KEY=your_key_here,CORS_ORIGINS="
```

### Frontend Deployment

```bash
# 1. Get backend URL
BACKEND_URL=$(gcloud run services describe alertmind-backend --region=us-central1 --format="value(status.url)")

# 2. Build image locally with backend URL
cd frontend
docker build --build-arg REACT_APP_API_URL=$BACKEND_URL/api -t gcr.io/alert-mind/alertmind-frontend:latest .

# 3. Tag with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker tag gcr.io/alert-mind/alertmind-frontend:latest gcr.io/alert-mind/alertmind-frontend:$TIMESTAMP

# 4. Push to GCR
docker push gcr.io/alert-mind/alertmind-frontend:latest
docker push gcr.io/alert-mind/alertmind-frontend:$TIMESTAMP

# 5. Deploy to Cloud Run
gcloud run deploy alertmind-frontend \
    --image gcr.io/alert-mind/alertmind-frontend:$TIMESTAMP \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1

# 6. Update backend CORS
FRONTEND_URL=$(gcloud run services describe alertmind-frontend --region=us-central1 --format="value(status.url)")
gcloud run services update alertmind-backend \
    --update-env-vars "CORS_ORIGINS=$FRONTEND_URL" \
    --region us-central1
```

## View Logs

```bash
# Backend logs
gcloud run logs tail alertmind-backend --region=us-central1

# Frontend logs
gcloud run logs tail alertmind-frontend --region=us-central1
```

## Update Services

Just run the deploy scripts again - they update existing services:

```bash
./deploy-backend-direct.sh  # Updates backend
./deploy-frontend-direct.sh # Updates frontend
```

## Troubleshooting

### Docker build fails

- Make sure Docker Desktop is running
- Check Dockerfile paths are correct
- Verify Docker has enough resources

### Push to GCR fails

```bash
# Re-authenticate Docker
gcloud auth configure-docker
```

### Deployment fails

- Check you're authenticated: `gcloud auth list`
- Verify project is set: `gcloud config get-value project`
- Check service logs for errors

### Frontend can't connect to backend

- Verify backend URL is correct in frontend build
- Check CORS is updated: `gcloud run services describe alertmind-backend --region=us-central1`
- Rebuild frontend with correct backend URL

## Quick Reference

```bash
# Deploy backend
./deploy-backend-direct.sh

# Deploy frontend (after backend works)
./deploy-frontend-direct.sh

# Get URLs
gcloud run services describe alertmind-backend --region=us-central1 --format="value(status.url)"
gcloud run services describe alertmind-frontend --region=us-central1 --format="value(status.url)"

# View logs
gcloud run logs tail alertmind-backend --region=us-central1
gcloud run logs tail alertmind-frontend --region=us-central1
```
