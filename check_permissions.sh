#!/bin/bash

# GenX Trading System - Permission Diagnostic Script
# This script checks the current state of Cloud Build permissions

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 GenX Trading System - Permission Diagnostic${NC}"
echo "==============================================="

# Get project details
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)" 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: No project ID found${NC}"
    echo "Please set your project: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${BLUE}📋 Project Information:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Project Number: $PROJECT_NUMBER"
echo ""

# Check authentication
echo -e "${BLUE}🔐 Authentication Status:${NC}"
CURRENT_USER=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)
if [ ! -z "$CURRENT_USER" ]; then
    echo -e "${GREEN}  ✅ Authenticated as: $CURRENT_USER${NC}"
else
    echo -e "${RED}  ❌ Not authenticated${NC}"
    echo "  Run: gcloud auth login"
    exit 1
fi
echo ""

# Check API status
echo -e "${BLUE}🔧 API Status:${NC}"
APIS=("cloudbuild.googleapis.com" "run.googleapis.com" "containerregistry.googleapis.com" "iam.googleapis.com")

for api in "${APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>/dev/null | grep -q "$api"; then
        echo -e "${GREEN}  ✅ $api${NC}"
    else
        echo -e "${RED}  ❌ $api${NC}"
    fi
done
echo ""

# Check Cloud Build service account
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
echo -e "${BLUE}🔑 Cloud Build Service Account: $CLOUDBUILD_SA${NC}"

# Check if service account exists
if gcloud iam service-accounts describe $CLOUDBUILD_SA --project=$PROJECT_ID >/dev/null 2>&1; then
    echo -e "${GREEN}  ✅ Service account exists${NC}"
else
    echo -e "${RED}  ❌ Service account not found${NC}"
    echo "  This is unusual - Cloud Build service account should be created automatically"
fi
echo ""

# Check service account roles
echo -e "${BLUE}🛡️  Current IAM Roles for Cloud Build Service Account:${NC}"
ROLES=$(gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="value(bindings.role)" \
    --filter="bindings.members:$CLOUDBUILD_SA" 2>/dev/null)

REQUIRED_ROLES=(
    "roles/cloudbuild.builds.builder"
    "roles/run.admin"
    "roles/storage.admin"
    "roles/iam.serviceAccountUser"
    "roles/viewer"
)

if [ ! -z "$ROLES" ]; then
    echo "$ROLES" | while read role; do
        echo -e "${GREEN}  ✅ $role${NC}"
    done
    
    echo ""
    echo -e "${BLUE}🔍 Missing Required Roles:${NC}"
    for required_role in "${REQUIRED_ROLES[@]}"; do
        if ! echo "$ROLES" | grep -q "$required_role"; then
            echo -e "${RED}  ❌ $required_role${NC}"
        fi
    done
else
    echo -e "${RED}  ❌ No roles found for Cloud Build service account${NC}"
    echo "  Run: ./fix_cloudbuild_permissions.sh"
fi
echo ""

# Check your user permissions
echo -e "${BLUE}👤 Your User Permissions:${NC}"
USER_ROLES=$(gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="value(bindings.role)" \
    --filter="bindings.members:user:$CURRENT_USER" 2>/dev/null)

ADMIN_ROLES=("roles/owner" "roles/editor" "roles/iam.admin" "roles/resourcemanager.projectIamAdmin")
HAS_ADMIN=false

for admin_role in "${ADMIN_ROLES[@]}"; do
    if echo "$USER_ROLES" | grep -q "$admin_role"; then
        echo -e "${GREEN}  ✅ $admin_role${NC}"
        HAS_ADMIN=true
    fi
done

if [ "$HAS_ADMIN" = false ]; then
    echo -e "${RED}  ❌ No admin roles found${NC}"
    echo -e "${YELLOW}  ⚠️  You may not have permission to grant IAM roles${NC}"
fi
echo ""

# Final recommendations
echo -e "${BLUE}📝 Recommendations:${NC}"
if [ -z "$ROLES" ]; then
    echo -e "${YELLOW}1. Run: ./fix_cloudbuild_permissions.sh${NC}"
fi
echo -e "${YELLOW}2. If permissions are correct, try: ./deploy_cloud_build.sh${NC}"
echo -e "${YELLOW}3. Check Cloud Build history: gcloud builds list --limit=5${NC}"
echo ""
echo -e "${GREEN}✅ Diagnostic complete!${NC}"