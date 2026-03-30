# ADK Text Classification Agent

A Google AI agent built with ADK and Gemini that classifies input text into predefined categories. The agent is hosted on Google Cloud Run and exposes HTTP endpoints for easy integration.

## Overview

This project demonstrates a complete AI agent implementation using:
- **Google ADK (Agent Development Kit)** - For agent structure and capabilities
- **Gemini Pro Model** - For inference and text understanding
- **Flask** - For HTTP server and endpoint exposure
- **Google Cloud Run** - For serverless deployment
- **Docker** - For containerization

## Agent Capability

**Text Classification**: Analyzes input text and classifies it into one of these categories:
- `NEWS` - News articles and press releases
- `OPINION` - Opinion pieces and editorials
- `TECHNICAL` - Technical documentation and specs
- `MARKETING` - Marketing and promotional content
- `EDUCATIONAL` - Educational and tutorials

Each classification includes:
- **Category**: The predicted category
- **Confidence**: Confidence score (0.0 - 1.0)
- **Reasoning**: Brief explanation for the classification

## Project Structure

```
.
├── agent.py              # ADK Agent implementation with Gemini
├── server.py             # Flask HTTP server
├── requirements.txt      # Python dependencies
├── Dockerfile            # Cloud Run container config
├── .gcloudignore         # Files to ignore in Cloud deployment
├── README.md             # This file
└── test_agent.py         # (Optional) Local testing script
```

## API Endpoints

### 1. Health Check
```
GET /
```
Returns service status and version.

**Response:**
```json
{
  "status": "healthy",
  "service": "ADK Text Classification Agent",
  "version": "1.0.0"
}
```

### 2. Classify Text
```
POST /classify
```
Classifies the provided text.

**Request Body:**
```json
{
  "text": "Your text to classify here"
}
```

**Response:**
```json
{
  "success": true,
  "text": "Your text to classify h...",
  "classification": {
    "category": "NEWS",
    "confidence": 0.87,
    "reasoning": "This appears to be a news article covering current events"
  }
}
```

### 3. Agent Information
```
GET /agent/info
```
Returns information about the agent and available endpoints.

**Response:**
```json
{
  "agent_type": "TextClassificationAgent",
  "capability": "Classify text into predefined categories",
  "categories": ["NEWS", "OPINION", "TECHNICAL", "MARKETING", "EDUCATIONAL"],
  "models_used": ["gemini-pro"],
  "endpoints": [...]
}
```

## Local Setup

### Prerequisites
- Python 3.9+
- Google Gemini API key
- pip package manager

### Installation

1. **Clone/Download the project**
```bash
cd "path\to\adk agent"
```

2. **Create virtual environment (optional but recommended)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variable**
```bash
# Windows (Command Prompt)
set GOOGLE_API_KEY=your_gemini_api_key_here

# Windows (PowerShell)
$env:GOOGLE_API_KEY="your_gemini_api_key_here"

# macOS/Linux
export GOOGLE_API_KEY=your_gemini_api_key_here
```

5. **Run locally**
```bash
python server.py
```

The server will start on `http://localhost:8080`

### Testing Locally

```bash
# Test health check
curl http://localhost:8080/

# Test classification
curl -X POST http://localhost:8080/classify \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Breaking news: New technology revolutionizes industry\"}"

# Get agent info
curl http://localhost:8080/agent/info
```

## Cloud Run Deployment

### Prerequisites
- Google Cloud Platform account
- `gcloud` CLI installed and authenticated
- Docker installed (optional, Cloud Run can build from source)

### Step 1: Create a GCP Project

```bash
# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Or create a new project
gcloud projects create adk-agent-project
gcloud config set project adk-agent-project
```

### Step 2: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable generativeai.googleapis.com
```

### Step 3: Create Gemini API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "APIs & Services" → "Credentials"
3. Click "Create Credentials" → "API Key"
4. Copy the API key

### Step 4: Deploy to Cloud Run

**Option A: Direct deployment from source**
```bash
gcloud run deploy adk-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

**Option B: Build Docker image first**
```bash
# Build the image
docker build -t gcr.io/YOUR_PROJECT_ID/adk-agent:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/adk-agent:latest

# Deploy to Cloud Run
gcloud run deploy adk-agent \
  --image gcr.io/YOUR_PROJECT_ID/adk-agent:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

### Step 5: Get the Service URL

```bash
gcloud run services describe adk-agent --region us-central1
```

The output will include the `Service URL`. This is your endpoint.

### Step 6: Test the Deployment

```bash
# Replace with your Cloud Run URL
CLOUD_RUN_URL=https://adk-agent-xxxxx.run.app

# Health check
curl $CLOUD_RUN_URL/

# Test classification
curl -X POST $CLOUD_RUN_URL/classify \
  -H "Content-Type: application/json" \
  -d '{"text":"This is a test article about classification"}'

# Get agent info
curl $CLOUD_RUN_URL/agent/info
```

## Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `PORT` | No | Server port (default: 8080) |
| `PYTHONUNBUFFERED` | No | Disable output buffering (default: 1) |

### Resource Limits (Cloud Run)
- **Memory**: 512 MB (default)
- **CPU**: 1 vCPU (default)
- **Timeout**: 300 seconds (default)
- **Concurrency**: 80 (default)

Adjust these in the deployment command if needed:
```bash
gcloud run deploy adk-agent \
  --memory 1Gi \
  --cpu 2 \
  --timeout 600 \
  --concurrency 100 \
  ...
```

## Cost Considerations

- **Cloud Run**: Pay per request + compute time (generous free tier: 2M requests/month)
- **Gemini API**: Pay per token (no free tier for gemini-pro)
- **Network**: Minimal egress costs

Estimate: ~$0.001 per 1000 tokens for Gemini (varies)

## Error Handling

The agent handles various error scenarios:

| Error | Response | HTTP Code |
|-------|----------|-----------|
| Empty input | `{"success": false, "error": "Input cannot be empty"}` | 400 |
| Invalid JSON | `{"success": false, "error": "Invalid JSON"}` | 400 |
| Missing API key | `{"success": false, "error": "Agent not initialized"}` | 503 |
| API timeout/error | Returns error in response | 500 |
| Unknown endpoint | Lists available endpoints | 404 |

## Troubleshooting

### "GOOGLE_API_KEY not set"
**Solution**: Make sure the environment variable is set before running:
```bash
# Verify it's set
echo $GOOGLE_API_KEY  # macOS/Linux
echo %GOOGLE_API_KEY%  # Windows CMD
```

### "Connection timeout on Cloud Run"
**Solution**: 
- Check API quota in Cloud Console
- Verify Gemini API is enabled in your project
- Increase timeout in Cloud Run configuration

### "Cold start latency"
**Solution**: Cloud Run has initial cold start (~2-5 seconds). Consider:
- Using a higher memory allocation (improves startup)
- Setting concurrency to keep instances warm
- Using Google Cloud Tasks for background classification

## Future Enhancements

- Add authentication/API keys to the service
- Implement batch classification endpoint
- Add request/response logging and monitoring
- Support custom category definitions
- Add rate limiting
- Implement caching for repeated classifications
- Add webhooks for async processing

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues with:
- **Google Cloud Run**: [Cloud Run Documentation](https://cloud.google.com/run/docs)
- **Gemini API**: [Gemini API Docs](https://ai.google.dev/)
- **Flask**: [Flask Documentation](https://flask.palletsprojects.com/)
