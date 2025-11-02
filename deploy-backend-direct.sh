#!/bin/bash

# Deploy backend directly - Build locally, push to GCR, deploy to Cloud Run
set -e

PROJECT_ID="alert-mind"
REGION="us-central1"
IMAGE_NAME="gcr.io/alert-mind/alertmind-backend"
SERVICE_NAME="alertmind-backend"

echo "🚀 Deploying Backend to Cloud Run"
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

# Build image locally for linux/amd64 (required by Cloud Run)
echo ""
echo "🔨 Building Docker image locally for linux/amd64..."
echo "   (Cloud Run requires linux/amd64 architecture)"

# Set up buildx for multi-platform builds
docker buildx create --use --name multiplatform 2>/dev/null || docker buildx use multiplatform

cd backend

# Build for linux/amd64 platform
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker buildx build \
    --platform linux/amd64 \
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

# Get API key (optional)
echo ""
read -p "Enter GOOGLE_AI_API_KEY (or press Enter to skip): " GOOGLE_AI_API_KEY
if [ -z "$GOOGLE_AI_API_KEY" ]; then
    GOOGLE_AI_API_KEY=""
    echo "⚠️  No API key provided. Backend will use fallback mode."
fi

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
        --memory 2Gi \
        --cpu 2 \
        --min-instances 0 \
        --max-instances 10 \
        --timeout 300 \
        --set-env-vars "GOOGLE_AI_API_KEY=$GOOGLE_AI_API_KEY,CORS_ORIGINS="
else
    echo ""
    echo "🔄 Updating existing Cloud Run service..."
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME:$TIMESTAMP \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 2Gi \
        --cpu 2 \
        --min-instances 0 \
        --max-instances 10 \
        --timeout 300 \
        --update-env-vars "GOOGLE_AI_API_KEY=$GOOGLE_AI_API_KEY"
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "✅ Backend deployed successfully!"
echo ""
echo "📊 Service URL: $SERVICE_URL"
echo ""
echo "🧪 Test the backend:"
echo "   curl $SERVICE_URL/health"
echo ""
echo "📝 View logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit 50 --format json"
echo "   OR visit: https://console.cloud.google.com/logs/query?project=$PROJECT_ID"

