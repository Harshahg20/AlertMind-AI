#!/bin/bash

# Deploy frontend only

set -e

PROJECT_ID="alert-mind"
REGION="us-central1"

echo "🚀 Deploying frontend to Cloud Run..."

gcloud config set project $PROJECT_ID

# Get backend URL
BACKEND_URL=$(gcloud run services describe alertmind-backend --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")
if [ -z "$BACKEND_URL" ]; then
    echo "❌ Backend not found. Deploy backend first: ./deploy-backend.sh"
    exit 1
fi

echo "Using backend URL: $BACKEND_URL/api"

gcloud builds submit --config=cloudbuild-frontend.yaml \
    --substitutions=_API_URL="$BACKEND_URL/api",_BACKEND_API_URL="$BACKEND_URL/api" \
    --project=$PROJECT_ID

FRONTEND_URL=$(gcloud run services describe alertmind-frontend --region=$REGION --format="value(status.url)")
echo "✅ Frontend deployed: $FRONTEND_URL"

# Update backend CORS
echo "🔄 Updating backend CORS..."
gcloud run services update alertmind-backend \
    --update-env-vars="CORS_ORIGINS=$FRONTEND_URL" \
    --region=$REGION \
    --project=$PROJECT_ID \
    --quiet

echo "✅ CORS updated!"

