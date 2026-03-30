#!/bin/bash

# ADK Agent Cloud Run Deployment Script
# This script automates the deployment to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${1:-}"
GEMINI_API_KEY="${2:-}"
REGION="${3:-us-central1}"
SERVICE_NAME="adk-agent"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

show_usage() {
    echo "Usage: ./deploy.sh <PROJECT_ID> <GEMINI_API_KEY> [REGION]"
    echo ""
    echo "Example:"
    echo "  ./deploy.sh my-project sk-xxxxxxxxxxxx us-central1"
    echo ""
    echo "Arguments:"
    echo "  PROJECT_ID       - Your Google Cloud Project ID"
    echo "  GEMINI_API_KEY   - Your Google Gemini API Key"
    echo "  REGION           - Cloud Run region (default: us-central1)"
    exit 1
}

# Validation
if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID is required"
    show_usage
fi

if [ -z "$GEMINI_API_KEY" ]; then
    print_error "GEMINI_API_KEY is required"
    show_usage
fi

print_info "ADK Agent Cloud Run Deployment"
print_info "Project: $PROJECT_ID"
print_info "Region: $REGION"
print_info "Service: $SERVICE_NAME"

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI not found. Please install Google Cloud SDK"
    exit 1
fi
print_success "gcloud CLI found"

# Set project
print_info "Setting GCP project..."
gcloud config set project "$PROJECT_ID" || {
    print_error "Failed to set project. Check PROJECT_ID"
    exit 1
}
print_success "Project set"

# Enable APIs
print_info "Enabling required APIs..."
gcloud services enable run.googleapis.com --quiet
gcloud services enable artifactregistry.googleapis.com --quiet
gcloud services enable generativeai.googleapis.com --quiet
print_success "APIs enabled"

# Deploy
print_info "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_API_KEY=$GEMINI_API_KEY" \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --quiet

print_success "Deployment completed!"

# Get service URL
print_info "Retrieving service URL..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --format 'value(status.url)')

print_success "Service deployed successfully!"
echo ""
echo "=========================================="
echo "Cloud Run Service URL:"
echo ""
echo "  $SERVICE_URL"
echo ""
echo "=========================================="
echo ""
echo "Test your service:"
echo "  curl $SERVICE_URL/"
echo "  curl -X POST $SERVICE_URL/classify \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"text\": \"Your test text here\"}'"
echo ""
echo "View logs:"
echo "  gcloud run logs read $SERVICE_NAME --region $REGION"
echo ""
echo "Update service:"
echo "  gcloud run deploy $SERVICE_NAME --source . --region $REGION"
echo ""
