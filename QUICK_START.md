# Quick Start Guide

Get your ADK agent running in 5 minutes!

## Local Testing (2 min)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```bash
# Windows CMD
set GOOGLE_API_KEY=your_gemini_api_key_here

# Windows PowerShell
$env:GOOGLE_API_KEY="your_gemini_api_key_here"

# macOS/Linux
export GOOGLE_API_KEY=your_gemini_api_key_here
```

Get API key: https://makersuite.google.com/app/apikey

### 3. Run Server
```bash
python server.py
```

Server starts at: `http://localhost:8080`

### 4. Test (in new terminal)
```bash
# Health check
curl http://localhost:8080/

# Test classification
curl -X POST http://localhost:8080/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Breaking news about new technology"}'
```

### 5. Run Tests (optional)
```bash
python test_agent.py
```

## Deploy to Cloud Run (3 min)

### 1. Get Gemini API Key
https://makersuite.google.com/app/apikey

### 2. Choose Your Platform

**macOS/Linux:**
```bash
chmod +x deploy.sh
./deploy.sh YOUR_PROJECT_ID YOUR_GEMINI_API_KEY
```

**Windows (PowerShell):**
```powershell
.\deploy.ps1 -ProjectId YOUR_PROJECT_ID -GeminiApiKey YOUR_GEMINI_API_KEY
```

**Manual (any platform):**
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
gcloud run deploy adk-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

### 3. Get Your URL
```bash
gcloud run services describe adk-agent --region us-central1 --format 'value(status.url)'
```

Your endpoint is ready! Example:
```
https://adk-agent-abc123def456.run.app
```

### 4. Test Endpoint
```bash
# Test it
curl https://adk-agent-abc123def456.run.app/

curl -X POST https://adk-agent-abc123def456.run.app/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Test your text here"}'
```

## Project Files

| File | Purpose |
|------|---------|
| `agent.py` | ADK agent implementation with Gemini |
| `server.py` | Flask HTTP server |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container configuration for Cloud Run |
| `README.md` | Full documentation |
| `DEPLOYMENT_GUIDE.md` | Detailed deployment steps |
| `test_agent.py` | Test script for local testing |
| `deploy.sh` | Automated deployment (bash) |
| `deploy.ps1` | Automated deployment (PowerShell) |

## API Endpoints

### POST `/classify`
Classify text into categories

**Request:**
```json
{
  "text": "Your text to classify"
}
```

**Response:**
```json
{
  "success": true,
  "text": "Your text to classify",
  "classification": {
    "category": "NEWS",
    "confidence": 0.87,
    "reasoning": "This appears to be a news article"
  }
}
```

### GET `/`
Health check

### GET `/agent/info`
Get agent information and endpoint list

## Categories

Your agent classifies text into:
- `NEWS` - News articles
- `OPINION` - Opinion pieces  
- `TECHNICAL` - Technical documentation
- `MARKETING` - Marketing content
- `EDUCATIONAL` - Educational material

## Troubleshooting

**"GOOGLE_API_KEY not set"**
- Verify environment variable is set
- Restart terminal after setting env var

**"Connection refused" locally**
- Make sure `python server.py` is running
- Check port 8080 is available

**"Service not responding" on Cloud Run**
- Check API key is correct
- View logs: `gcloud run logs read adk-agent --region us-central1`

**"Deployment failed"**
- Ensure gcloud CLI is configured
- Check project ID is correct
- Verify APIs are enabled: `gcloud services list --enabled`

## Next Steps

1. **Customize the agent**: Modify `agent.py` to change categories or logic
2. **Add authentication**: See DEPLOYMENT_GUIDE.md for security setup
3. **Monitor usage**: Check Cloud Console for metrics and logs
4. **Scale up**: Update memory/CPU settings for higher load

## Documentation

- Full details: [README.md](README.md)
- Deployment steps: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Code examples: See `test_agent.py`

## Support

- **Cloud Run Issues**: https://cloud.google.com/run/docs
- **Gemini API**: https://ai.google.dev/
- **gcloud CLI**: `gcloud run --help`

---

**Deployed successfully?** Share your Cloud Run URL! 🚀
