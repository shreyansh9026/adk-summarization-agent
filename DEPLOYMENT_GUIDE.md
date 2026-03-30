# ADK Agent Cloud Run Deployment Guide

## Quick Start (5 minutes)

### Prerequisites
- Google Cloud Platform account
- `gcloud` CLI installed ([Install](https://cloud.google.com/sdk/docs/install))
- Google Gemini API key ([Get API Key](https://makersuite.google.com/app/apikey))

### Deployment

#### Option 1: Using Bash Script (macOS/Linux)
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh YOUR_PROJECT_ID YOUR_GEMINI_API_KEY us-central1
```

#### Option 2: Using PowerShell Script (Windows)
```powershell
# Run deployment
.\deploy.ps1 -ProjectId YOUR_PROJECT_ID -GeminiApiKey YOUR_GEMINI_API_KEY -Region us-central1
```

#### Option 3: Manual Deployment
```bash
# 1. Set project
gcloud config set project YOUR_PROJECT_ID

# 2. Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# 3. Deploy
gcloud run deploy adk-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_GEMINI_API_KEY \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300

# 4. Get URL
gcloud run services describe adk-agent --region us-central1
```

## Step-by-Step Deployment

### Step 1: Create/Select GCP Project

```bash
# Create new project
gcloud projects create adk-agent-project --name="ADK Agent"
gcloud config set project adk-agent-project

# Or use existing project
gcloud config set project YOUR_EXISTING_PROJECT_ID
```

### Step 2: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable generativeai.googleapis.com
```

### Step 3: Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key (looks like: `AIzaSy...`)
4. Keep it safe - don't commit to git!

### Step 4: Deploy with gcloud CLI

**Basic deployment:**
```bash
gcloud run deploy adk-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=AIzaSy... \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

**With custom settings:**
```bash
gcloud run deploy adk-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=AIzaSy... \
  --memory 1Gi \
  --cpu 2 \
  --timeout 600 \
  --concurrency 100 \
  --min-instances 1 \
  --max-instances 10
```

### Step 5: Get Your Service URL

```bash
gcloud run services describe adk-agent --region us-central1 --format 'value(status.url)'
```

Output example:
```
https://adk-agent-abc123def456.run.app
```

### Step 6: Test Your Deployment

```bash
# Replace with your actual URL
CLOUD_RUN_URL=https://adk-agent-abc123def456.run.app

# Test health check
curl $CLOUD_RUN_URL/

# Test classification
curl -X POST $CLOUD_RUN_URL/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Breaking news about a new discovery"}'

# Get agent info
curl $CLOUD_RUN_URL/agent/info
```

## Monitoring & Management

### View Logs
```bash
# Real-time logs
gcloud run logs read adk-agent --region us-central1 --limit 50 --follow

# Logs from specific time
gcloud run logs read adk-agent --region us-central1 --limit 100 --since 1h
```

### Update Service
```bash
# Update code
git add .
git commit -m "Update agent logic"

# Redeploy
gcloud run deploy adk-agent \
  --source . \
  --region us-central1
```

### Update Environment Variables
```bash
# Update API key (if changed)
gcloud run deploy adk-agent \
  --region us-central1 \
  --update-env-vars GOOGLE_API_KEY=NEW_API_KEY
```

### View Service Details
```bash
gcloud run services describe adk-agent --region us-central1
```

### Check Metrics
```bash
# View in Cloud Console
# https://console.cloud.google.com/run?region=us-central1

# Or list all services
gcloud run services list --region us-central1
```

## Performance Tuning

### Memory & CPU Settings
| Use Case | Memory | CPU | Notes |
|----------|--------|-----|-------|
| Light testing | 256 MB | 0.5 | Minimal costs, may be slow |
| Standard | 512 MB | 1 | Default, good balance |
| High performance | 1 GB | 2 | Faster response, higher cost |
| Scale heavy | 2 GB | 4 | For high-traffic scenarios |

### Concurrency Settings
```bash
gcloud run deploy adk-agent \
  --region us-central1 \
  --concurrency 80 \
  --max-instances 10 \
  --min-instances 1
```

- `concurrency`: Requests per instance (default: 80)
- `max-instances`: Maximum concurrent instances (default: 1000)
- `min-instances`: Minimum warm instances (avoid cold starts)

### Cold Start Optimization
```bash
# Keep minimum 1 instance always warm
gcloud run deploy adk-agent \
  --region us-central1 \
  --min-instances 1
```

**Note:** Minimum instances are billed constantly, even with 0 requests.

## Troubleshooting

### Deployment Fails
```bash
# Check if APIs are enabled
gcloud services list --enabled | grep run
gcloud services list --enabled | grep artifactregistry

# Check authentication
gcloud auth list
gcloud auth login
```

### Service Returns 503
**Cause:** API key not set or invalid
```bash
# Verify environment variable
gcloud run services describe adk-agent --region us-central1 | grep GOOGLE_API_KEY

# Update if needed
gcloud run deploy adk-agent \
  --region us-central1 \
  --update-env-vars GOOGLE_API_KEY=YOUR_NEW_KEY
```

### High Latency / Timeouts
```bash
# Check timeout setting
gcloud run services describe adk-agent --region us-central1 | grep timeout

# Increase timeout (max 3600 seconds)
gcloud run deploy adk-agent \
  --region us-central1 \
  --timeout 600
```

### Authentication Errors
```bash
# Re-authenticate
gcloud auth login

# or with specific account
gcloud auth login your-email@gmail.com

# Set default project
gcloud config set project YOUR_PROJECT_ID
```

### Check Deployment Status
```bash
# Get current status
gcloud run services describe adk-agent --region us-central1 --format yaml

# Watch deployment progress
gcloud run deploy adk-agent \
  --source . \
  --region us-central1 \
  --format="table(metadata.name, status.updateTime)"
```

## Cost Estimation

### Cloud Run Pricing (US-central1)
- **Requests:** $0.40 per million requests
- **Compute:** $0.00002400 per vCPU-second
- **Memory:** $0.00000250 per GB-second

### Example Calculations

**Heavy Usage (1M monthly requests):**
- Requests: 1M × $0.40/1M = $0.40
- Compute: 1M × 1.5s × 1 vCPU × $0.00002400 = $36
- Memory: 1M × 1.5s × 0.5GB × $0.00000250 = $1.88
- **Total: ~$38/month**

**Light Usage (100K monthly requests):**
- Requests: 100K × $0.40/1M = $0.04
- Compute: 100K × 1s × 1 vCPU × $0.00002400 = $2.40
- Memory: 100K × 1s × 0.5GB × $0.00000250 = $0.13
- **Total: ~$2.57/month**

**Free Tier:**
- 2M requests/month
- 360K vCPU-seconds/month
- 180K GB-seconds/month

Most hobby projects fit within the free tier!

## Security Best Practices

### API Key Security
```bash
# NEVER commit API key to git
echo ".env" >> .gitignore
echo "*.key" >> .gitignore

# Use Cloud Secret Manager for production
gcloud secrets create gemini-api-key --data-file=-
```

### Use Secret Manager
```bash
# Store API key
gcloud secrets create gemini-api-key --replication-policy="automatic"
echo "YOUR_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-

# Grant service account access
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secret manager
gcloud run deploy adk-agent \
  --source . \
  --region us-central1 \
  --set-env-vars "GOOGLE_API_KEY=projects/PROJECT_ID/secrets/gemini-api-key/versions/latest"
```

### Authentication
```bash
# Remove --allow-unauthenticated for production
gcloud run deploy adk-agent \
  --region us-central1

# Require authentication
gcloud run services add-iam-policy-binding adk-agent \
  --member=serviceAccount:SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.invoker \
  --region us-central1
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy adk-agent \
            --source . \
            --region us-central1 \
            --platform managed \
            --allow-unauthenticated \
            --set-env-vars GOOGLE_API_KEY=${{ secrets.GEMINI_API_KEY }}
```

## Cleanup

### Delete Service
```bash
gcloud run services delete adk-agent --region us-central1
```

### Delete Project (if created for testing)
```bash
gcloud projects delete adk-agent-project
```

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Gemini API Docs](https://ai.google.dev/)
- [gcloud cli reference](https://cloud.google.com/sdk/gcloud/reference/run)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-docker-image)

## Getting Help

```bash
# Help for gcloud run
gcloud run --help
gcloud run deploy --help

# Check quotas and limits
gcloud compute project-info describe --project=PROJECT_ID

# Contact support
# https://cloud.google.com/support
```
