#!/bin/bash

# AlertMind-AI Google Cloud Deployment Script
# Usage: ./deploy.sh [backend|frontend|all]

set -e

# Configuration - Update these variables
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
GOOGLE_AI_API_KEY="${GOOGLE_AI_API_KEY:-}"

if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "Error: Please set GCP_PROJECT_ID environment variable or update the script"
    exit 1
fi

deploy_backend() {
    echo "🚀 Deploying backend..."
    
    cd backend
    
    # Build and push
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/alertmind-backend
    
    # Deploy
    if [ -z "$GOOGLE_AI_API_KEY" ]; then
        echo "Warning: GOOGLE_AI_API_KEY not set. Deploying without API key."
        gcloud run deploy alertmind-backend \
            --image gcr.io/${PROJECT_ID}/alertmind-backend \
            --region ${REGION} \
            --platform managed \
            --allow-unauthenticated \
            --port 8000 \
            --memory 2Gi \
            --cpu 2 \
            --min-instances 1 \
            --max-instances 10
    else
        gcloud run deploy alertmind-backend \
            --image gcr.io/${PROJECT_ID}/alertmind-backend \
            --region ${REGION} \
            --platform managed \
            --allow-unauthenticated \
            --port 8000 \
            --memory 2Gi \
            --cpu 2 \
            --min-instances 1 \
            --max-instances 10 \
            --set-env-vars GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
    fi
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe alertmind-backend --region ${REGION} --format 'value(status.url)')
    echo "✅ Backend deployed at: ${BACKEND_URL}"
    
    cd ..
    
    # Export backend URL for frontend deployment
    export BACKEND_URL
}

deploy_frontend() {
    if [ -z "$BACKEND_URL" ]; then
        echo "Error: Backend URL not set. Please deploy backend first or set BACKEND_URL environment variable."
        exit 1
    fi
    
    echo "🚀 Deploying frontend..."
    echo "   Using backend URL: ${BACKEND_URL}"
    
    cd frontend
    
    # Build Docker image
    docker build --build-arg REACT_APP_API_URL=${BACKEND_URL}/api -t gcr.io/${PROJECT_ID}/alertmind-frontend .
    
    # Push to Container Registry
    docker push gcr.io/${PROJECT_ID}/alertmind-frontend
    
    # Deploy
    gcloud run deploy alertmind-frontend \
        --image gcr.io/${PROJECT_ID}/alertmind-frontend \
        --region ${REGION} \
        --platform managed \
        --allow-unauthenticated \
        --port 80 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10
    
    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe alertmind-frontend --region ${REGION} --format 'value(status.url)')
    echo "✅ Frontend deployed at: ${FRONTEND_URL}"
    
    cd ..
    
    # Update backend CORS to allow frontend
    echo "🔄 Updating backend CORS settings..."
    gcloud run services update alertmind-backend \
        --set-env-vars CORS_ORIGINS=${FRONTEND_URL} \
        --region ${REGION}
    
    echo ""
    echo "🎉 Deployment complete!"
    echo "   Frontend: ${FRONTEND_URL}"
    echo "   Backend: ${BACKEND_URL}"
}

case "${1:-all}" in
    backend)
        deploy_backend
        ;;
    frontend)
        deploy_frontend
        ;;
    all)
        deploy_backend
        deploy_frontend
        ;;
    *)
        echo "Usage: $0 [backend|frontend|all]"
        exit 1
        ;;
esac

