#!/bin/bash
set -e

PROJECT_ID="alert-mind"
REGION="us-central1"

echo "🚀 Deploying to Google Cloud Run (Auto)"
echo "Project: $PROJECT_ID"

# Try to load API key from backend/.env
if [ -f backend/.env ]; then
    echo "📄 Loading API key from backend/.env"
    export $(grep -v '^#' backend/.env | xargs)
fi

if [ -z "$GOOGLE_AI_API_KEY" ]; then
    echo "⚠️  GOOGLE_AI_API_KEY not found. Using empty key."
    GOOGLE_AI_API_KEY=""
else
    echo "✅ GOOGLE_AI_API_KEY found."
fi

# Deploy Backend
echo "🔨 Building and deploying backend..."
gcloud builds submit --config=cloudbuild-backend.yaml \
    --substitutions=_GOOGLE_AI_API_KEY="$GOOGLE_AI_API_KEY",_CORS_ORIGINS="" \
    --project=$PROJECT_ID

# Get backend URL
BACKEND_URL=$(gcloud run services describe alertmind-backend --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
echo "✅ Backend deployed: $BACKEND_URL"

# Deploy Frontend
echo "🔨 Building and deploying frontend..."
gcloud builds submit --config=cloudbuild-frontend.yaml \
    --substitutions=_API_URL="$BACKEND_URL/api",_BACKEND_API_URL="$BACKEND_URL/api" \
    --project=$PROJECT_ID

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe alertmind-frontend --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
echo "✅ Frontend deployed: $FRONTEND_URL"

# Update backend CORS
echo "🔄 Updating backend CORS settings..."
gcloud run services update alertmind-backend \
    --update-env-vars="CORS_ORIGINS=$FRONTEND_URL" \
    --region=$REGION \
    --project=$PROJECT_ID \
    --quiet

echo "🎉 Deployment complete!"
echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
