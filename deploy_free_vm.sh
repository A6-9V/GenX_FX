#!/bin/bash

# GenX FX Free Tier VM Deployment Script
# Deploys the signal generation service to a free e2-micro VM on Google Cloud

set -e

# --- Configuration ---
# IMPORTANT: Replace with your Google Cloud Project ID
PROJECT_ID="genx-fx-392819"
INSTANCE_NAME="genx-fx-signals-free"
REGION="us-central1"
ZONE="us-central1-a"
MACHINE_TYPE="e2-micro" # Free tier eligible
IMAGE_FAMILY="ubuntu-2004-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
FIREWALL_RULE_NAME="allow-http-8080"
REPO_URL="https://github.com/your-username/your-repo.git" # Replace with your repo URL

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting GenX FX Free Tier Deployment...${NC}"

# --- Validation ---
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed.${NC}"
    echo "Please install the Google Cloud SDK and authenticate."
    exit 1
fi

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" == "your-gcp-project-id" ]; then
    echo -e "${RED}❌ Error: Please set your PROJECT_ID in the script.${NC}"
    exit 1
fi

gcloud config set project $PROJECT_ID

echo -e "${YELLOW}🔧 Creating firewall rule '${FIREWALL_RULE_NAME}'...${NC}"
gcloud compute firewall-rules create $FIREWALL_RULE_NAME \
    --allow tcp:8080 \
    --description="Allow HTTP traffic for signal server" \
    --target-tags=http-server \
    --quiet || echo -e "${YELLOW}Firewall rule '${FIREWALL_RULE_NAME}' may already exist. Skipping.${NC}"

echo -e "${YELLOW}🔧 Creating VM instance '${INSTANCE_NAME}'...${NC}"
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --tags=http-server \
    --metadata=startup-script="#!/bin/bash
        sudo apt-get update
        sudo apt-get install -y git
        git clone ${REPO_URL}
        cd \$(basename ${REPO_URL} .git)
        chmod +x deploy_vm.sh
        ./deploy_vm.sh
    "

echo -e "${GREEN}✅ VM instance '${INSTANCE_NAME}' created successfully.${NC}"

# --- Getting External IP ---
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo -e "${BLUE}🎉 Deployment Summary:${NC}"
echo "----------------------------------------"
echo -e "VM Name:       ${GREEN}$INSTANCE_NAME${NC}"
echo -e "Region:        ${GREEN}$REGION${NC}"
echo -e "Machine Type:  ${GREEN}$MACHINE_TYPE${NC}"
echo -e "External IP:   ${GREEN}$EXTERNAL_IP${NC}"
echo ""
echo -e "${YELLOW}Your signal file will be available at:${NC}"
echo -e "🔗 ${GREEN}http://${EXTERNAL_IP}:8080/MT4_Signals.csv${NC}"
echo ""
echo -e "It may take a few minutes for the setup to complete and the server to start."
echo "You can SSH into the VM to check progress: gcloud compute ssh ${INSTANCE_NAME} --zone ${ZONE}"
echo "----------------------------------------"