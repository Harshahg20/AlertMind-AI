# AlertMind-AI - Complete Deployment Guide

## ✅ Deployment Status

### Backend Service
- **URL**: https://alertmind-backend-qspwfgfhda-uc.a.run.app
- **API Base**: https://alertmind-backend-qspwfgfhda-uc.a.run.app/api
- **Port**: 443 (internal container port)
- **Status**: ✅ Healthy and Running
- **CORS**: Configured for frontend access

### Frontend Service
- **URL**: https://alertmind-frontend-qspwfgfhda-uc.a.run.app
- **Port**: 8080 (internal container port)
- **Status**: ✅ Healthy and Running
- **Backend Connection**: ✅ Configured

---

## 🚀 Steps to Verify Deployment

### 1. Test Backend Health
```bash
curl https://alertmind-backend-qspwfgfhda-uc.a.run.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "cascadeguard-ai",
  "agentic_ai": "enabled",
  "version": "2.0.0"
}
```

### 2. Test Backend API
```bash
curl https://alertmind-backend-qspwfgfhda-uc.a.run.app/api/alerts
```

**Expected**: Returns a JSON array of alerts

### 3. Test Frontend
Open your browser and navigate to:
```
https://alertmind-frontend-qspwfgfhda-uc.a.run.app
```

**Expected**: The AlertMind-AI dashboard should load with data from the backend

---

## 🔧 How to Redeploy

### Redeploy Backend
```powershell
# From project root
cd backend
gcloud builds submit --tag gcr.io/alertmind-476814/alertmind-backend --timeout=30m

# Deploy to Cloud Run
gcloud run deploy alertmind-backend \
  --image gcr.io/alertmind-476814/alertmind-backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 443 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --env-vars-file=../backend-env-vars.yaml
```

### Redeploy Frontend
```powershell
# From project root
cd frontend
$backendUrl = "https://alertmind-backend-370935358441.us-central1.run.app"
gcloud builds submit --config=cloudbuild.yaml --substitutions=_API_URL="$backendUrl/api" .
```

---

## 📝 Configuration Files

### Backend Environment Variables (backend-env-vars.yaml)
```yaml
CORS_ORIGINS: "http://localhost:3000,https://alertmind-frontend-qspwfgfhda-uc.a.run.app"
GOOGLE_AI_API_KEY: "YOUR_GOOGLE_AI_API_KEY"
```

### Update CORS Origins
If you deploy the frontend to a new URL, update CORS:
```powershell
# Update backend-env-vars.yaml with new frontend URL
gcloud run services update alertmind-backend \
  --region us-central1 \
  --env-vars-file=backend-env-vars.yaml
```

---

## 🔍 Troubleshooting

### Issue: Frontend shows "Failed to connect to backend"

**Solution 1: Check CORS Configuration**
```powershell
gcloud run services describe alertmind-backend \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

Verify that `CORS_ORIGINS` includes your frontend URL.

**Solution 2: Update CORS**
```powershell
gcloud run services update alertmind-backend \
  --region us-central1 \
  --env-vars-file=backend-env-vars.yaml
```

### Issue: Backend returns 503 errors

**Check backend logs:**
```powershell
gcloud run services logs read alertmind-backend \
  --region us-central1 \
  --limit 50
```

**Common causes:**
- Google AI API Key not set or invalid
- Container startup timeout
- Memory/CPU limits exceeded

**Solution:**
```powershell
# Update env vars
gcloud run services update alertmind-backend \
  --region us-central1 \
  --env-vars-file=backend-env-vars.yaml

# Or increase resources
gcloud run services update alertmind-backend \
  --region us-central1 \
  --memory 4Gi \
  --cpu 4
```

### Issue: Frontend shows white screen

**Check frontend logs:**
```powershell
gcloud run services logs read alertmind-frontend \
  --region us-central1 \
  --limit 50
```

**Check if frontend is using correct backend URL:**
The frontend was built with:
```
REACT_APP_API_URL=https://alertmind-backend-370935358441.us-central1.run.app/api
```

---

## 🌐 Local Development

### Run Backend Locally
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Run Frontend Locally
```powershell
cd frontend
npm install
npm start
```

Frontend will connect to backend at `http://localhost:8000/api` by default.

---

## 📊 Service URLs Summary

| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | https://alertmind-backend-qspwfgfhda-uc.a.run.app/api | REST API endpoints |
| Backend Health | https://alertmind-backend-qspwfgfhda-uc.a.run.app/health | Health check |
| Frontend | https://alertmind-frontend-qspwfgfhda-uc.a.run.app | Web dashboard |

---

## ✨ Features Available

- ✅ Real-time alert monitoring
- ✅ Cascade prediction with AI
- ✅ Alert correlation
- ✅ Autonomous decision making
- ✅ Prevention execution
- ✅ Patch management
- ✅ IT administrative tasks
- ✅ Google Gemini AI integration
- ✅ Multi-client support

---

## 🔐 Security Notes

1. **API Keys**: Store Google AI API key in Secret Manager for production
2. **Authentication**: Current deployment allows unauthenticated access. Add authentication for production.
3. **CORS**: Currently configured for specific origins. Update as needed.

---

## 📈 Monitoring

### View Service Metrics
```powershell
# Backend metrics
gcloud run services describe alertmind-backend \
  --region us-central1 \
  --format="value(status.traffic)"

# Frontend metrics
gcloud run services describe alertmind-frontend \
  --region us-central1 \
  --format="value(status.traffic)"
```

### View Logs
```powershell
# Backend logs
gcloud run services logs read alertmind-backend --region us-central1 --limit 100

# Frontend logs
gcloud run services logs read alertmind-frontend --region us-central1 --limit 100
```

---

## 💰 Cost Optimization

- Backend has `min-instances: 1` to ensure availability
- Frontend has `min-instances: 0` to reduce costs when idle
- Adjust based on your usage patterns

---

## 🎉 Next Steps

1. ✅ Backend deployed and healthy
2. ✅ Frontend deployed and accessible
3. ✅ CORS configured for frontend-backend communication
4. 🔄 Access the frontend URL and verify all features work
5. 🔄 Monitor logs for any issues
6. 🔄 Set up custom domain (optional)
7. 🔄 Add authentication (recommended for production)

---

**Deployment completed successfully!** 🚀

