#!/bin/bash

# Deploy backend only

set -e

PROJECT_ID="alert-mind"
REGION="us-central1"

echo "🚀 Deploying backend to Cloud Run..."

gcloud config set project $PROJECT_ID

read -p "Enter GOOGLE_AI_API_KEY (or press Enter to skip): " GOOGLE_AI_API_KEY
if [ -z "$GOOGLE_AI_API_KEY" ]; then
    GOOGLE_AI_API_KEY=""
fi

# Get frontend URL for CORS if it exists
FRONTEND_URL=""
if gcloud run services describe alertmind-frontend --region=$REGION --format="value(status.url)" 2>/dev/null; then
    FRONTEND_URL=$(gcloud run services describe alertmind-frontend --region=$REGION --format="value(status.url)")
fi

gcloud builds submit --config=cloudbuild-backend.yaml \
    --substitutions=_GOOGLE_AI_API_KEY="$GOOGLE_AI_API_KEY",_CORS_ORIGINS="$FRONTEND_URL" \
    --project=$PROJECT_ID

BACKEND_URL=$(gcloud run services describe alertmind-backend --region=$REGION --format="value(status.url)")
echo "✅ Backend deployed: $BACKEND_URL"

