# ADK Agent Cloud Run Deployment Script (PowerShell - Windows)
# Usage: .\deploy.ps1 -ProjectId YOUR_PROJECT_ID -GeminiApiKey YOUR_API_KEY -Region us-central1

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$true)]
    [string]$GeminiApiKey,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "adk-agent",
    
    [Parameter(Mandatory=$false)]
    [string]$Memory = "512Mi",
    
    [Parameter(Mandatory=$false)]
    [string]$Cpu = "1"
)

# Color formatting
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor Yellow
}

# Print header
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ADK Agent Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Info "Checking prerequisites..."

# Check gcloud
try {
    $gcloud = gcloud --version 2>$null
    Write-Success "gcloud CLI found"
}
catch {
    Write-Error-Custom "gcloud CLI not found. Please install Google Cloud SDK"
    Write-Host "Download: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Set project
Write-Info "Setting GCP project: $ProjectId"
gcloud config set project $ProjectId 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to set project. Check PROJECT_ID: $ProjectId"
    exit 1
}
Write-Success "Project set"

# Enable APIs
Write-Info "Enabling required APIs..."
gcloud services enable run.googleapis.com --quiet 2>$null
gcloud services enable artifactregistry.googleapis.com --quiet 2>$null
gcloud services enable generativeai.googleapis.com --quiet 2>$null
Write-Success "APIs enabled"

# Deploy
Write-Info "Deploying to Cloud Run..."
Write-Info "Service: $ServiceName"
Write-Info "Region: $Region"
Write-Info "Memory: $Memory"
Write-Info "CPU: $Cpu"

gcloud run deploy $ServiceName `
    --source . `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --set-env-vars "GOOGLE_API_KEY=$GeminiApiKey" `
    --memory $Memory `
    --cpu $Cpu `
    --timeout 300 `
    --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Success "Deployment completed!"
}
else {
    Write-Error-Custom "Deployment failed!"
    exit 1
}

# Get service URL
Write-Info "Retrieving service URL..."
$serviceUrl = gcloud run services describe $ServiceName `
    --region $Region `
    --format "value(status.url)" 2>$null

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Service deployed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cloud Run URL:" -ForegroundColor Yellow
Write-Host "  $serviceUrl" -ForegroundColor Cyan
Write-Host ""

# Print useful commands
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Test health check:" -ForegroundColor White
Write-Host "   curl $serviceUrl/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test classification:" -ForegroundColor White
Write-Host "   curl -X POST $serviceUrl/classify ``" -ForegroundColor Gray
Write-Host "     -H 'Content-Type: application/json' ``" -ForegroundColor Gray
Write-Host "     -d '{""text"": ""Your test text here""}'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Get agent info:" -ForegroundColor White
Write-Host "   curl $serviceUrl/agent/info" -ForegroundColor Gray
Write-Host ""
Write-Host "4. View logs:" -ForegroundColor White
Write-Host "   gcloud run logs read $ServiceName --region $Region" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Update service (after code changes):" -ForegroundColor White
Write-Host "   gcloud run deploy $ServiceName --source . --region $Region" -ForegroundColor Gray
Write-Host ""

# Verify deployment
Write-Info "Verifying deployment..."
$response = Invoke-WebRequest -Uri "$serviceUrl/" -ErrorAction SilentlyContinue
if ($response.StatusCode -eq 200) {
    Write-Success "Service is responding correctly!"
    Write-Host "Response:" -ForegroundColor White
    Write-Host ($response.Content | ConvertFrom-Json | ConvertTo-Json -Indent 2) -ForegroundColor Gray
}
else {
    Write-Error-Custom "Service did not respond correctly (HTTP $($response.StatusCode))"
}

Write-Host ""
Write-Host "Deployment summary saved. Share this URL:" -ForegroundColor Yellow
Write-Host "$serviceUrl" -ForegroundColor Cyan
