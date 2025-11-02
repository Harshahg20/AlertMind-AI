# Step-by-Step Deployment Guide to Google Cloud Run

Follow these steps to deploy AlertMind to Google Cloud Run.

## Prerequisites Setup

### Step 1: Install Google Cloud SDK

**macOS:**

```bash
# Option A: Using Homebrew
brew install google-cloud-sdk

# Option B: Manual installation
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Linux:**

```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download and install from: https://cloud.google.com/sdk/docs/install

**Verify installation:**

```bash
gcloud --version
```

### Step 2: Install Docker

**macOS:**

```bash
brew install --cask docker
# OR download from: https://docs.docker.com/desktop/install/mac-install/
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# Or follow: https://docs.docker.com/engine/install/ubuntu/
```

**Windows:**
Download from: https://docs.docker.com/desktop/install/windows-install/

**Verify installation:**

```bash
docker --version
```

### Step 3: Authenticate with Google Cloud

```bash
# Login to your Google account
gcloud auth login

# Set the project
gcloud config set project alert-mind

# Verify project is set
gcloud config get-value project
```

### Step 4: Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Deployment Steps

### Step 5: Navigate to Project Directory

```bash
cd /Users/harshahg/superhack2025
```

### Step 6: Deploy the Application

**Option A: Deploy Everything (Recommended)**

```bash
./deploy.sh
```

This will:

1. Ask for your Google AI API key (optional - press Enter to skip)
2. Build and deploy the backend
3. Build and deploy the frontend
4. Configure CORS automatically
5. Display service URLs

**Option B: Deploy Backend Only**

```bash
./deploy-backend.sh
```

**Option C: Deploy Frontend Only** (requires backend already deployed)

```bash
./deploy-frontend.sh
```

### Step 7: During Deployment

When you run `./deploy.sh`, you'll be prompted:

1. **Enter GOOGLE_AI_API_KEY**

   - Enter your API key if you have one
   - OR press Enter to skip (app will work in fallback mode)

2. **Wait for build to complete**
   - Backend build takes ~5-10 minutes
   - Frontend build takes ~3-5 minutes

### Step 8: Get Your Service URLs

After deployment completes, you'll see:

```
🎉 Deployment complete!

📊 Service URLs:
   Backend:  https://alertmind-backend-xxxxx-uc.a.run.app
   Frontend: https://alertmind-frontend-xxxxx-uc.a.run.app
```

**Save these URLs!** You'll need them to access your application.

## Verify Deployment

### Step 9: Test Backend

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe alertmind-backend --region=us-central1 --format="value(status.url)")

# Test health endpoint
curl $BACKEND_URL/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "cascadeguard-ai",
  "agentic_ai": "enabled",
  "version": "2.0.0"
}
```

### Step 10: Test Frontend

Open the frontend URL in your browser:

```
https://alertmind-frontend-xxxxx-uc.a.run.app
```

You should see the AlertMind dashboard.

## Post-Deployment

### Step 11: View Logs (Optional)

```bash
# Backend logs
gcloud run logs tail alertmind-backend --region=us-central1

# Frontend logs
gcloud run logs tail alertmind-frontend --region=us-central1
```

### Step 12: Update Frontend API URL (if needed)

If the frontend can't connect to backend, update the API URL in `frontend/src/utils/apiClient.js`:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || "YOUR_BACKEND_URL/api";
```

Then redeploy frontend:

```bash
./deploy-frontend.sh
```

### Step 13: Update Environment Variables (Optional)

Update backend environment variables:

```bash
gcloud run services update alertmind-backend \
    --update-env-vars="GOOGLE_AI_API_KEY=your_key_here,CORS_ORIGINS=https://your-frontend-url" \
    --region=us-central1 \
    --project=alert-mind
```

## Troubleshooting

### Build Fails

**Check build logs:**

```bash
gcloud builds list --limit=5
gcloud builds log [BUILD_ID]
```

**Common issues:**

- Docker not running: `docker ps` should work
- Not authenticated: `gcloud auth login`
- Wrong project: `gcloud config set project alert-mind`

### Service Not Starting

**Check service logs:**

```bash
gcloud run logs tail alertmind-backend --region=us-central1 --limit=50
```

**Common issues:**

- Port mismatch: Ensure Dockerfile uses PORT 8080
- Missing environment variables
- API key issues (check logs for errors)

### Frontend Can't Connect to Backend

**Check CORS:**

```bash
gcloud run services describe alertmind-backend --region=us-central1 --format="value(spec.template.spec.containers[0].env)"
```

**Update CORS:**

```bash
gcloud run services update alertmind-backend \
    --update-env-vars="CORS_ORIGINS=https://your-frontend-url" \
    --region=us-central1
```

## Quick Reference Commands

```bash
# Deploy everything
./deploy.sh

# Deploy backend only
./deploy-backend.sh

# Deploy frontend only
./deploy-frontend.sh

# View backend URL
gcloud run services describe alertmind-backend --region=us-central1 --format="value(status.url)"

# View frontend URL
gcloud run services describe alertmind-frontend --region=us-central1 --format="value(status.url)"

# View logs
gcloud run logs tail alertmind-backend --region=us-central1
gcloud run logs tail alertmind-frontend --region=us-central1

# List services
gcloud run services list --region=us-central1

# Delete services (if needed)
gcloud run services delete alertmind-backend --region=us-central1
gcloud run services delete alertmind-frontend --region=us-central1
```

## Next Steps

1. ✅ Test the deployed application
2. ✅ Monitor logs for any issues
3. ✅ Set up custom domain (optional)
4. ✅ Configure alerts and monitoring
5. ✅ Set up CI/CD pipeline (optional)

## Need Help?

- **Cloud Build Logs**: https://console.cloud.google.com/cloud-build/builds?project=alert-mind
- **Cloud Run Console**: https://console.cloud.google.com/run?project=alert-mind
- **Service Logs**: Use `gcloud run logs tail` command

---

**That's it!** Your application is now deployed to Google Cloud Run. 🎉
