# Fix: Architecture Mismatch for Cloud Run

## Problem
Cloud Run requires `linux/amd64` architecture, but Docker on Apple Silicon (M1/M2/M3) builds `linux/arm64` by default.

## Solution
The deployment scripts now use `docker buildx` to build for the correct platform.

## What Changed

Both `deploy-backend-direct.sh` and `deploy-frontend-direct.sh` now:
1. Use `docker buildx` instead of `docker build`
2. Specify `--platform linux/amd64` 
3. Use `--load` to load the image locally after building

## How It Works

```bash
docker buildx build \
    --platform linux/amd64 \
    --tag gcr.io/alert-mind/alertmind-backend:latest \
    --load \
    .
```

The `--platform linux/amd64` flag ensures the image is built for Cloud Run's required architecture, even on Apple Silicon.

## Deploy Again

Now you can deploy:

```bash
# Deploy backend
./deploy-backend-direct.sh

# Deploy frontend (after backend works)
./deploy-frontend-direct.sh
```

## Manual Build (If Needed)

If you want to build manually:

```bash
# Backend
cd backend
docker buildx build --platform linux/amd64 -t gcr.io/alert-mind/alertmind-backend:latest --load .

# Frontend
cd frontend
docker buildx build --platform linux/amd64 --build-arg REACT_APP_API_URL=https://backend-url/api -t gcr.io/alert-mind/alertmind-frontend:latest --load .
```

