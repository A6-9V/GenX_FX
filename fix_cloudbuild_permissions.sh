#!/bin/bash

# GenX Trading System - Cloud Build Permissions Fix Script
# This script fixes the service account permissions for Cloud Build

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 GenX Trading System - Cloud Build Permissions Fix${NC}"
echo "======================================================="

# Get project details
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: No project ID found${NC}"
    echo "Please set your project: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${BLUE}📋 Project Information:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Project Number: $PROJECT_NUMBER"
echo ""

# Cloud Build service account
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
echo -e "${BLUE}🔑 Cloud Build Service Account: $CLOUDBUILD_SA${NC}"
echo ""

echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID
gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID
gcloud services enable iam.googleapis.com --project=$PROJECT_ID

echo -e "${YELLOW}🛡️  Granting IAM roles to Cloud Build service account...${NC}"

# Essential Cloud Build roles
echo "  ➤ Cloud Build Service Account role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUDBUILD_SA" \
    --role="roles/cloudbuild.builds.builder" \
    --quiet

# Cloud Run deployment permissions
echo "  ➤ Cloud Run Admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUDBUILD_SA" \
    --role="roles/run.admin" \
    --quiet

# Container Registry permissions
echo "  ➤ Storage Admin role (for Container Registry)..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUDBUILD_SA" \
    --role="roles/storage.admin" \
    --quiet

# IAM Service Account User (needed for Cloud Run deployment)
echo "  ➤ Service Account User role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUDBUILD_SA" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

# Viewer role for accessing project resources
echo "  ➤ Viewer role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUDBUILD_SA" \
    --role="roles/viewer" \
    --quiet

# Artifact Registry permissions (for newer projects)
echo "  ➤ Artifact Registry Writer role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUDBUILD_SA" \
    --role="roles/artifactregistry.writer" \
    --quiet

echo ""
echo -e "${GREEN}✅ Permissions granted successfully!${NC}"
echo ""

echo -e "${YELLOW}🔍 Verifying Cloud Build service account permissions...${NC}"
echo "Current roles for $CLOUDBUILD_SA:"
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$CLOUDBUILD_SA"

echo ""
echo -e "${GREEN}🎉 Cloud Build permissions have been configured!${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Try running the deployment again: ./deploy_cloud_build.sh"
echo "2. If you still get permission errors, wait 1-2 minutes for IAM propagation"
echo "3. Check Cloud Build logs for any remaining issues"
echo ""
echo -e "${YELLOW}💡 Common Issues:${NC}"
echo "• IAM changes can take up to 2 minutes to propagate"
echo "• Make sure you have sufficient permissions to grant these roles"
echo "• Your user account needs Project IAM Admin or Owner role"