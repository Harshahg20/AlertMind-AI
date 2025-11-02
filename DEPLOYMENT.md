# AlertMind-AI Google Cloud Deployment Guide

This guide will walk you through deploying the AlertMind-AI application to Google Cloud Platform using Cloud Run.

## Prerequisites

1. **Google Cloud Account**: Sign up at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud SDK (gcloud)**: Install from [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Install Docker Desktop or Docker Engine
4. **Google AI API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Project Structure

- **Backend**: FastAPI application (Python)
- **Frontend**: React application (Node.js)
- Both services will be deployed as separate Cloud Run services

## Step-by-Step Deployment

### 1. Initial Google Cloud Setup

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace PROJECT_ID with your actual project ID)
gcloud config set project PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Configure Google AI API Key

Store your Google AI API key in Secret Manager (recommended for production):

```bash
# Create a secret for the API key
echo -n "YOUR_GOOGLE_AI_API_KEY" | gcloud secrets create google-ai-api-key \
    --data-file=- \
    --replication-policy="automatic"

# Grant Cloud Run access to the secret
gcloud secrets add-iam-policy-binding google-ai-api-key \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

Alternatively, you can set it as an environment variable in Cloud Run directly.

### 3. Deploy Backend Service

#### Option A: Using Cloud Build (Recommended)

1. **Update the Cloud Build configuration**:

   Edit `cloudbuild-backend.yaml` and replace `YOUR_GOOGLE_AI_API_KEY_HERE` with your actual API key, or update it to use Secret Manager:

   ```yaml
   - '--set-secrets'
   - 'GOOGLE_AI_API_KEY=google-ai-api-key:latest'
   ```

2. **Submit the build**:

   ```bash
   gcloud builds submit --config=cloudbuild-backend.yaml
   ```

#### Option B: Manual Deployment

```bash
# Navigate to backend directory
cd backend

# Build and push Docker image
gcloud builds submit --tag gcr.io/PROJECT_ID/alertmind-backend

# Deploy to Cloud Run
gcloud run deploy alertmind-backend \
    --image gcr.io/PROJECT_ID/alertmind-backend \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --set-env-vars GOOGLE_AI_API_KEY=YOUR_GOOGLE_AI_API_KEY

# Note the service URL after deployment
# Example: https://alertmind-backend-xxxxx-uc.a.run.app
```

### 4. Deploy Frontend Service

After deploying the backend, note the backend service URL. You'll need it to configure the frontend.

#### Option A: Using Cloud Build

1. **Update the Cloud Build configuration**:

   Edit `cloudbuild-frontend.yaml` and replace `YOUR_BACKEND_API_URL_HERE` with your actual backend URL (e.g., `https://alertmind-backend-xxxxx-uc.a.run.app/api`)

2. **Submit the build**:

   ```bash
   gcloud builds submit --config=cloudbuild-frontend.yaml
   ```

#### Option B: Manual Deployment

```bash
# Navigate to frontend directory
cd frontend

# Build Docker image with API URL
docker build --build-arg REACT_APP_API_URL=https://YOUR_BACKEND_URL/api -t gcr.io/PROJECT_ID/alertmind-frontend .

# Push to Container Registry
docker push gcr.io/PROJECT_ID/alertmind-frontend

# Deploy to Cloud Run
gcloud run deploy alertmind-frontend \
    --image gcr.io/PROJECT_ID/alertmind-frontend \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 80 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10
```

### 5. Update CORS Settings (Important!)

After deploying the backend, update the CORS settings to allow requests from your frontend domain:

1. **Option A: Update code before deployment** - Modify `backend/app/main.py`:

   ```python
   # Replace the CORS configuration
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # For development/testing, restrict in production
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

   Or better, use an environment variable:

   ```python
   import os
   allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
   app.add_middleware(
       CORSMiddleware,
       allow_origins=allowed_origins,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Option B: Set environment variable during deployment**:

   ```bash
   gcloud run services update alertmind-backend \
       --set-env-vars CORS_ORIGINS=https://alertmind-frontend-xxxxx-uc.a.run.app \
       --region us-central1
   ```

### 6. Verify Deployment

1. **Check backend health**:
   ```bash
   curl https://YOUR_BACKEND_URL/health
   ```

2. **Check frontend**:
   Open your frontend URL in a browser:
   ```
   https://YOUR_FRONTEND_URL
   ```

3. **View logs**:
   ```bash
   # Backend logs
   gcloud run logs read alertmind-backend --region us-central1

   # Frontend logs
   gcloud run logs read alertmind-frontend --region us-central1
   ```

## Updating the Application

To update after making changes:

```bash
# Backend
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/alertmind-backend
gcloud run deploy alertmind-backend --image gcr.io/PROJECT_ID/alertmind-backend --region us-central1

# Frontend
cd frontend
docker build --build-arg REACT_APP_API_URL=https://YOUR_BACKEND_URL/api -t gcr.io/PROJECT_ID/alertmind-frontend .
docker push gcr.io/PROJECT_ID/alertmind-frontend
gcloud run deploy alertmind-frontend --image gcr.io/PROJECT_ID/alertmind-frontend --region us-central1
```

## Local Testing with Docker

Before deploying, you can test the Docker images locally:

### Backend

```bash
cd backend
docker build -t alertmind-backend .
docker run -p 8000:8000 -e GOOGLE_AI_API_KEY=YOUR_KEY alertmind-backend
```

### Frontend

```bash
cd frontend
docker build --build-arg REACT_APP_API_URL=http://localhost:8000/api -t alertmind-frontend .
docker run -p 3000:80 alertmind-frontend
```

## Cost Optimization

1. **Backend**: 
   - Set `min-instances=0` if you don't need constant uptime
   - Adjust `max-instances` based on expected traffic
   - Use `--cpu=1` if 2 CPUs are not needed

2. **Frontend**:
   - Frontend is mostly static, consider using Cloud Storage + Cloud CDN for even lower costs
   - Or deploy to Firebase Hosting for a simpler static hosting solution

## Security Best Practices

1. **API Keys**: Use Secret Manager instead of environment variables for sensitive data
2. **CORS**: Restrict CORS origins to specific domains in production
3. **Authentication**: Consider adding authentication to Cloud Run services
4. **HTTPS**: Cloud Run automatically provides HTTPS endpoints
5. **Environment Variables**: Avoid committing `.env` files to version control

## Troubleshooting

### Backend fails to start
- Check logs: `gcloud run logs read alertmind-backend --region us-central1`
- Verify `GOOGLE_AI_API_KEY` is set correctly
- Ensure all Python dependencies are in `requirements.txt`

### Frontend can't connect to backend
- Verify the backend URL in frontend build matches the actual backend URL
- Check CORS settings in backend
- Verify both services are in the same region

### Container build fails
- Check Dockerfile syntax
- Verify all dependencies are available
- Check Cloud Build logs: `gcloud builds list`

## Alternative: Using Cloud Run Jobs

If you have scheduled tasks or batch jobs, consider using Cloud Run Jobs instead of services.

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

