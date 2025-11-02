#!/bin/bash

# Deploy frontend directly - Build locally, push to GCR, deploy to Cloud Run
set -e

PROJECT_ID="alert-mind"
REGION="us-central1"
IMAGE_NAME="gcr.io/alert-mind/alertmind-frontend"
SERVICE_NAME="alertmind-frontend"

echo "🚀 Deploying Frontend to Cloud Run"
echo "Project: $PROJECT_ID"
echo ""

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs (idempotent)
echo "📋 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com --quiet

# Configure Docker to use gcloud as credential helper
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker --quiet

# Get backend URL
echo ""
echo "🔍 Getting backend URL..."
BACKEND_URL=$(gcloud run services describe alertmind-backend --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")
if [ -z "$BACKEND_URL" ]; then
    echo "❌ Backend service not found. Please deploy backend first:"
    echo "   ./deploy-backend-direct.sh"
    exit 1
fi

echo "✅ Found backend: $BACKEND_URL"

# Build image locally with backend URL for linux/amd64 (required by Cloud Run)
echo ""
echo "🔨 Building Docker image locally for linux/amd64..."
echo "   Using backend URL: $BACKEND_URL/api"
echo "   (Cloud Run requires linux/amd64 architecture)"

# Set up buildx for multi-platform builds
docker buildx create --use --name multiplatform 2>/dev/null || docker buildx use multiplatform

cd frontend

# Build for linux/amd64 platform
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker buildx build \
    --platform linux/amd64 \
    --build-arg REACT_APP_API_URL=$BACKEND_URL/api \
    --tag $IMAGE_NAME:latest \
    --tag $IMAGE_NAME:$TIMESTAMP \
    --load \
    .

cd ..

# Push to Google Container Registry
echo ""
echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME:latest
docker push $IMAGE_NAME:$TIMESTAMP

# Check if service exists
SERVICE_EXISTS=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(metadata.name)" 2>/dev/null || echo "")

if [ -z "$SERVICE_EXISTS" ]; then
    echo ""
    echo "🆕 Creating new Cloud Run service..."
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME:$TIMESTAMP \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --timeout 60 \
        --set-env-vars "BACKEND_API_URL=$BACKEND_URL/api"
else
    echo ""
    echo "🔄 Updating existing Cloud Run service..."
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME:$TIMESTAMP \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --timeout 60 \
        --update-env-vars "BACKEND_API_URL=$BACKEND_URL/api"
fi

# Get service URL
FRONTEND_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

# Update backend CORS
echo ""
echo "🔄 Updating backend CORS settings..."
gcloud run services update alertmind-backend \
    --update-env-vars "CORS_ORIGINS=$FRONTEND_URL" \
    --region $REGION \
    --quiet

echo ""
echo "✅ Frontend deployed successfully!"
echo ""
echo "📊 Service URL: $FRONTEND_URL"
echo ""
echo "🌐 Open in browser:"
echo "   $FRONTEND_URL"
echo ""
echo "📝 View logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit 50 --format json"
echo "   OR visit: https://console.cloud.google.com/logs/query?project=$PROJECT_ID"

