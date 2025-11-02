#!/bin/bash

# Quick script to view Cloud Run logs

PROJECT_ID="alert-mind"
REGION="us-central1"

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: ./view-logs.sh [backend|frontend]"
    echo ""
    echo "Examples:"
    echo "  ./view-logs.sh backend"
    echo "  ./view-logs.sh frontend"
    exit 1
fi

if [ "$SERVICE_NAME" = "backend" ]; then
    SERVICE_NAME="alertmind-backend"
elif [ "$SERVICE_NAME" = "frontend" ]; then
    SERVICE_NAME="alertmind-frontend"
fi

echo "📋 Viewing logs for: $SERVICE_NAME"
echo ""

# Use gcloud logging read command
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit 50 \
    --format="table(timestamp,severity,textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "💡 For more logs, visit:"
echo "   https://console.cloud.google.com/logs/query?project=$PROJECT_ID"

