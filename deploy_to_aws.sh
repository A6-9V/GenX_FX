#!/bin/bash

# GenX_FX Quick AWS Deployment Script
# This script provides a guided deployment to AWS

set -e

echo "🚀 Welcome to GenX_FX AWS Deployment!"
echo "Account: genxapitrading@gmail.com"
echo "User: keamouyleng"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is installed
check_aws_cli() {
    if command -v aws &> /dev/null; then
        print_success "AWS CLI is installed: $(aws --version)"
        return 0
    else
        print_error "AWS CLI is not installed."
        echo ""
        echo "Please install AWS CLI first:"
        echo ""
        echo "For Linux:"
        echo "  curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'"
        echo "  unzip awscliv2.zip"
        echo "  sudo ./aws/install"
        echo ""
        echo "For macOS:"
        echo "  curl 'https://awscli.amazonaws.com/AWSCLIV2.pkg' -o 'AWSCLIV2.pkg'"
        echo "  sudo installer -pkg AWSCLIV2.pkg -target /"
        echo ""
        exit 1
    fi
}

# Check AWS configuration
check_aws_config() {
    if aws sts get-caller-identity &> /dev/null; then
        print_success "AWS CLI is configured"
        print_status "Current identity:"
        aws sts get-caller-identity
        return 0
    else
        print_warning "AWS CLI is not configured."
        echo ""
        echo "Please configure AWS CLI with your credentials:"
        echo "1. Go to AWS Console: https://console.aws.amazon.com/"
        echo "2. Sign in with: genxapitrading@gmail.com"
        echo "3. Go to IAM > Users > keamouyleng > Security credentials"
        echo "4. Create Access Keys"
        echo "5. Run: aws configure"
        echo ""
        read -p "Press Enter after configuring AWS CLI, or 'q' to quit: " choice
        if [ "$choice" = "q" ]; then
            exit 1
        fi
        
        # Verify configuration
        if aws sts get-caller-identity &> /dev/null; then
            print_success "AWS CLI configured successfully!"
            aws sts get-caller-identity
        else
            print_error "AWS CLI configuration failed. Please try again."
            exit 1
        fi
    fi
}

# Main deployment function
main() {
    print_status "Starting GenX_FX AWS deployment..."
    
    # Check prerequisites
    check_aws_cli
    check_aws_config
    
    echo ""
    print_status "Ready to deploy! Choose your deployment method:"
    echo ""
    echo "1. Automated Secure Deployment (Recommended)"
    echo "   - Full automated deployment with security best practices"
    echo "   - Creates all necessary AWS resources"
    echo "   - Deploys to EC2 instance"
    echo ""
    echo "2. Manual Step-by-Step Deployment"
    echo "   - More control over each step"
    echo "   - Separate setup and deployment phases"
    echo ""
    echo "3. View Deployment Guide"
    echo "   - Detailed documentation and troubleshooting"
    echo ""
    
    read -p "Enter your choice (1, 2, or 3): " choice
    
    case $choice in
        1)
            print_status "Starting automated secure deployment..."
            ./aws/secure_deploy.sh
            ;;
        2)
            print_status "Starting manual deployment..."
            echo ""
            echo "Step 1: Setting up AWS resources..."
            ./aws/setup.sh
            echo ""
            echo "Step 2: Deploying application..."
            ./aws/deploy.sh
            ;;
        3)
            print_status "Opening deployment guide..."
            if command -v cat &> /dev/null; then
                cat AWS_DEPLOYMENT_GUIDE.md
            else
                print_error "Cannot display guide. Please open AWS_DEPLOYMENT_GUIDE.md manually."
            fi
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Deployment process completed!"
    echo ""
    print_status "Next steps:"
    echo "1. Check the generated configuration files:"
    echo "   - aws_config.json (AWS resources)"
    echo "   - instance_info.json (EC2 instance details)"
    echo ""
    echo "2. Access your deployed application:"
    echo "   - SSH into your EC2 instance"
    echo "   - Monitor logs in CloudWatch"
    echo "   - Check S3 bucket for data"
    echo ""
    echo "3. For detailed information, see: AWS_DEPLOYMENT_GUIDE.md"
}

# Run main function
main "$@"