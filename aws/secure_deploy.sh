#!/bin/bash

# GenX_FX Secure AWS Deployment Script
# This script deploys the GenX_FX trading system to AWS using secure authentication

set -e

echo "🚀 Secure AWS Deployment for GenX_FX Trading System"
echo "Account: genxapitrading@gmail.com"
echo "User: keamouyleng"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check AWS CLI installation
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first:"
        echo "  Linux: curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip' && unzip awscliv2.zip && sudo ./aws/install"
        echo "  macOS: curl 'https://awscli.amazonaws.com/AWSCLIV2.pkg' -o 'AWSCLIV2.pkg' && sudo installer -pkg AWSCLIV2.pkg -target /"
        exit 1
    fi
    print_success "AWS CLI is installed: $(aws --version)"
}

# Configure AWS credentials securely
configure_aws_credentials() {
    print_status "Setting up AWS credentials for genxapitrading@gmail.com..."
    
    # Check if already configured
    if aws sts get-caller-identity &> /dev/null; then
        print_success "AWS CLI is already configured"
        print_status "Current identity:"
        aws sts get-caller-identity
        return 0
    fi
    
    print_warning "AWS CLI not configured. Please configure it manually:"
    echo ""
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
}

# Create AWS resources
create_aws_resources() {
    print_status "Creating AWS resources for GenX_FX trading system..."
    
    # Get AWS account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REGION=$(aws configure get default.region)
    
    print_status "Account ID: $ACCOUNT_ID"
    print_status "Region: $REGION"
    
    # Create S3 bucket for deployment
    BUCKET_NAME="genx-fx-trading-${ACCOUNT_ID}-$(date +%Y%m%d)"
    print_status "Creating S3 bucket: $BUCKET_NAME"
    
    if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
        aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"
        print_success "S3 bucket created: $BUCKET_NAME"
    else
        print_warning "S3 bucket already exists: $BUCKET_NAME"
    fi
    
    # Create DynamoDB table for trading data
    TABLE_NAME="genx-fx-trading-signals"
    print_status "Creating DynamoDB table: $TABLE_NAME"
    
    if ! aws dynamodb describe-table --table-name "$TABLE_NAME" &> /dev/null; then
        aws dynamodb create-table \
            --table-name "$TABLE_NAME" \
            --attribute-definitions \
                AttributeName=signal_id,AttributeType=S \
                AttributeName=timestamp,AttributeType=S \
            --key-schema \
                AttributeName=signal_id,KeyType=HASH \
                AttributeName=timestamp,KeyType=RANGE \
            --billing-mode PAY_PER_REQUEST \
            --region "$REGION"
        
        print_status "Waiting for DynamoDB table to be active..."
        aws dynamodb wait table-exists --table-name "$TABLE_NAME"
        print_success "DynamoDB table created: $TABLE_NAME"
    else
        print_warning "DynamoDB table already exists: $TABLE_NAME"
    fi
    
    # Create CloudWatch log group
    LOG_GROUP="/aws/genx-fx/trading-logs"
    print_status "Creating CloudWatch log group: $LOG_GROUP"
    
    if ! aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP" --query "logGroups[?logGroupName=='$LOG_GROUP']" --output text | grep -q "$LOG_GROUP"; then
        aws logs create-log-group --log-group-name "$LOG_GROUP" --region "$REGION"
        print_success "CloudWatch log group created: $LOG_GROUP"
    else
        print_warning "CloudWatch log group already exists: $LOG_GROUP"
    fi
    
    # Save configuration
    cat > aws_config.json << EOF
{
    "account_id": "$ACCOUNT_ID",
    "region": "$REGION",
    "s3_bucket": "$BUCKET_NAME",
    "dynamodb_table": "$TABLE_NAME",
    "cloudwatch_log_group": "$LOG_GROUP",
    "deployment_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    print_success "AWS resources created successfully!"
    print_status "Configuration saved to aws_config.json"
}

# Create deployment package
create_deployment_package() {
    print_status "Creating deployment package..."
    
    # Load configuration
    if [ ! -f "aws_config.json" ]; then
        print_error "aws_config.json not found. Please run setup first."
        exit 1
    fi
    
    S3_BUCKET=$(jq -r '.s3_bucket' aws_config.json)
    
    # Create temporary directory
    mkdir -p temp_deploy
    
    # Copy necessary files
    cp -r core/ temp_deploy/ 2>/dev/null || true
    cp -r api/ temp_deploy/ 2>/dev/null || true
    cp -r utils/ temp_deploy/ 2>/dev/null || true
    cp -r config/ temp_deploy/ 2>/dev/null || true
    cp -r services/ temp_deploy/ 2>/dev/null || true
    cp requirements.txt temp_deploy/ 2>/dev/null || true
    cp main.py temp_deploy/ 2>/dev/null || true
    
    # Create deployment script
    cat > temp_deploy/deploy_script.sh << 'EOF'
#!/bin/bash
set -e

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Starting GenX_FX trading system..."
python3 main.py
EOF
    
    chmod +x temp_deploy/deploy_script.sh
    
    # Create zip file
    cd temp_deploy
    zip -r ../genx-fx-deployment.zip .
    cd ..
    
    # Upload to S3
    print_status "Uploading deployment package to S3..."
    aws s3 cp genx-fx-deployment.zip "s3://$S3_BUCKET/"
    
    # Cleanup
    rm -rf temp_deploy genx-fx-deployment.zip
    
    print_success "Deployment package created and uploaded to S3"
}

# Deploy to EC2
deploy_to_ec2() {
    print_status "Deploying to EC2 instance..."
    
    # Load configuration
    S3_BUCKET=$(jq -r '.s3_bucket' aws_config.json)
    REGION=$(jq -r '.region' aws_config.json)
    
    # Get latest Amazon Linux 2 AMI
    AMI_ID=$(aws ec2 describe-images \
        --owners amazon \
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" \
        --query "reverse(sort_by(Images, &CreationDate))[:1].ImageId" \
        --output text \
        --region "$REGION")
    
    print_status "Using AMI: $AMI_ID"
    
    # Create key pair
    KEY_NAME="genx-fx-key-$(date +%Y%m%d)"
    print_status "Creating key pair: $KEY_NAME"
    
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --query 'KeyMaterial' \
        --output text \
        --region "$REGION" > "${KEY_NAME}.pem"
    
    chmod 400 "${KEY_NAME}.pem"
    print_success "Key pair created: ${KEY_NAME}.pem"
    
    # Create security group
    SG_NAME="genx-fx-trading-sg"
    print_status "Creating security group: $SG_NAME"
    
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$SG_NAME" \
        --description "Security group for GenX_FX trading system" \
        --query 'GroupId' \
        --output text \
        --region "$REGION")
    
    # Add security group rules
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"
    
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"
    
    # Create user data script
    cat > user_data.sh << EOF
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Download deployment package
aws s3 cp s3://$S3_BUCKET/genx-fx-deployment.zip /tmp/
cd /tmp
unzip genx-fx-deployment.zip

# Install dependencies and start application
chmod +x deploy_script.sh
./deploy_script.sh
EOF
    
    # Create EC2 instance
    print_status "Creating EC2 instance..."
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id "$AMI_ID" \
        --count 1 \
        --instance-type t3.medium \
        --key-name "$KEY_NAME" \
        --security-group-ids "$SG_ID" \
        --user-data file://user_data.sh \
        --query 'Instances[0].InstanceId' \
        --output text \
        --region "$REGION")
    
    print_success "EC2 instance created: $INSTANCE_ID"
    
    # Wait for instance to be running
    print_status "Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids "$INSTANCE_ID" \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text \
        --region "$REGION")
    
    print_success "Instance is running at: $PUBLIC_IP"
    
    # Save instance info
    cat > instance_info.json << EOF
{
    "instance_id": "$INSTANCE_ID",
    "public_ip": "$PUBLIC_IP",
    "security_group_id": "$SG_ID",
    "key_name": "$KEY_NAME",
    "key_file": "${KEY_NAME}.pem",
    "deployment_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    print_success "EC2 deployment completed!"
    print_status "SSH command: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
}

# Main deployment function
main() {
    print_status "Starting secure AWS deployment for GenX_FX..."
    
    # Check AWS CLI
    check_aws_cli
    
    # Configure credentials
    configure_aws_credentials
    
    # Create AWS resources
    create_aws_resources
    
    # Create deployment package
    create_deployment_package
    
    # Deploy to EC2
    deploy_to_ec2
    
    print_success "🎉 GenX_FX trading system deployed successfully to AWS!"
    print_status "Next steps:"
    echo "1. SSH into your instance: ssh -i \$(jq -r '.key_file' instance_info.json) ec2-user@\$(jq -r '.public_ip' instance_info.json)"
    echo "2. Monitor logs in CloudWatch: \$(jq -r '.cloudwatch_log_group' aws_config.json)"
    echo "3. Check S3 bucket for data: \$(jq -r '.s3_bucket' aws_config.json)"
    echo "4. View instance details: cat instance_info.json"
}

# Run main function
main "$@"