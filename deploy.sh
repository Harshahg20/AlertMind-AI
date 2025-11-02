#!/bin/bash

# Clean deployment script for Google Cloud Run
# Project: alert-mind

set -e

PROJECT_ID="alert-mind"
REGION="us-central1"

echo "🚀 Deploying to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo ""

# Check prerequisites
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo "📋 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com --quiet

# Get API key
echo ""
read -p "Enter GOOGLE_AI_API_KEY (or press Enter to skip): " GOOGLE_AI_API_KEY
if [ -z "$GOOGLE_AI_API_KEY" ]; then
    GOOGLE_AI_API_KEY=""
    echo "⚠️  No API key provided. Backend will use fallback mode."
fi

# Deploy Backend
echo ""
echo "🔨 Building and deploying backend..."
gcloud builds submit --config=cloudbuild-backend.yaml \
    --substitutions=_GOOGLE_AI_API_KEY="$GOOGLE_AI_API_KEY",_CORS_ORIGINS="" \
    --project=$PROJECT_ID

# Get backend URL
BACKEND_URL=$(gcloud run services describe alertmind-backend --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")
if [ -z "$BACKEND_URL" ]; then
    echo "❌ Failed to get backend URL"
    exit 1
fi

echo "✅ Backend deployed: $BACKEND_URL"

# Deploy Frontend
echo ""
echo "🔨 Building and deploying frontend..."
echo "   Backend URL: $BACKEND_URL/api"

gcloud builds submit --config=cloudbuild-frontend.yaml \
    --substitutions=_API_URL="$BACKEND_URL/api",_BACKEND_API_URL="$BACKEND_URL/api" \
    --project=$PROJECT_ID

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe alertmind-frontend --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")
if [ -z "$FRONTEND_URL" ]; then
    echo "❌ Failed to get frontend URL"
    exit 1
fi

echo "✅ Frontend deployed: $FRONTEND_URL"

# Update backend CORS
echo ""
echo "🔄 Updating backend CORS settings..."
gcloud run services update alertmind-backend \
    --update-env-vars="CORS_ORIGINS=$FRONTEND_URL" \
    --region=$REGION \
    --project=$PROJECT_ID \
    --quiet

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📊 Service URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""
echo "📝 View logs:"
echo "   Backend:  gcloud run logs tail alertmind-backend --region=$REGION"
echo "   Frontend: gcloud run logs tail alertmind-frontend --region=$REGION"

