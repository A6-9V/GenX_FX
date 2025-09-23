#!/bin/bash

# AWS Deployment Script for GenX Trading Platform
# This script handles the complete deployment process to AWS

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="genx-trading"
AWS_REGION="${AWS_REGION:-us-east-1}"
ENVIRONMENT="${ENVIRONMENT:-production}"
TERRAFORM_DIR="$(dirname "$0")"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed. Please install it first."
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        error "Terraform is not installed. Please install it first."
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install it first."
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured. Run 'aws configure' first."
    fi
    
    success "All prerequisites met"
}

# Deploy infrastructure
deploy_infrastructure() {
    log "Deploying AWS infrastructure with Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan \
        -var="aws_region=$AWS_REGION" \
        -var="environment=$ENVIRONMENT" \
        -var="project_name=$PROJECT_NAME" \
        -out=tfplan
    
    # Apply deployment
    terraform apply -auto-approve tfplan
    
    success "Infrastructure deployment completed"
}

# Build and push Docker image
build_and_push_image() {
    log "Building and pushing Docker image to ECR..."
    
    # Get ECR repository URL
    REPOSITORY_URL=$(aws ecr describe-repositories \
        --repository-names "$PROJECT_NAME" \
        --region "$AWS_REGION" \
        --query 'repositories[0].repositoryUri' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$REPOSITORY_URL" ]; then
        error "ECR repository not found. Make sure infrastructure is deployed first."
    fi
    
    # Login to ECR
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$REPOSITORY_URL"
    
    # Build image
    cd "$(dirname "$TERRAFORM_DIR")"
    docker build -f Dockerfile.production -t "$REPOSITORY_URL:latest" .
    docker tag "$REPOSITORY_URL:latest" "$REPOSITORY_URL:$(git rev-parse --short HEAD)"
    
    # Push image
    docker push "$REPOSITORY_URL:latest"
    docker push "$REPOSITORY_URL:$(git rev-parse --short HEAD)"
    
    success "Docker image built and pushed"
}

# Update ECS services
update_services() {
    log "Updating ECS services..."
    
    local services=("api" "discord-bot" "telegram-bot" "websocket-feed" "scheduler" "ai-trainer")
    
    for service in "${services[@]}"; do
        log "Updating service: $service"
        
        aws ecs update-service \
            --cluster "$PROJECT_NAME-cluster" \
            --service "$PROJECT_NAME-$service" \
            --force-new-deployment \
            --region "$AWS_REGION" > /dev/null
        
        log "Waiting for $service to stabilize..."
        aws ecs wait services-stable \
            --cluster "$PROJECT_NAME-cluster" \
            --services "$PROJECT_NAME-$service" \
            --region "$AWS_REGION"
        
        success "Service $service updated successfully"
    done
}

# Update secrets
update_secrets() {
    log "Updating application secrets..."
    
    if [ -f ".env" ]; then
        # Parse .env file and update secrets
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ $key =~ ^#.*$ ]] && continue
            [[ -z $key ]] && continue
            
            # Remove quotes from value
            value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/')
            
            log "Updating secret: $key"
        done < .env
        
        warning "Secrets update requires manual intervention. Please update AWS Secrets Manager manually."
    else
        warning ".env file not found. Skipping secrets update."
    fi
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Get ALB DNS name
    ALB_DNS=$(aws elbv2 describe-load-balancers \
        --names "$PROJECT_NAME-alb" \
        --region "$AWS_REGION" \
        --query 'LoadBalancers[0].DNSName' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$ALB_DNS" ]; then
        error "Load balancer not found"
    fi
    
    log "Testing API health endpoint..."
    
    # Wait for health check to pass
    local retries=30
    local count=0
    
    while [ $count -lt $retries ]; do
        if curl -sf "http://$ALB_DNS/health" > /dev/null 2>&1; then
            success "Health check passed"
            success "Application is accessible at: http://$ALB_DNS"
            return 0
        fi
        
        ((count++))
        log "Health check attempt $count/$retries failed, retrying in 10 seconds..."
        sleep 10
    done
    
    error "Health check failed after $retries attempts"
}

# Backup current deployment
backup_deployment() {
    log "Creating deployment backup..."
    
    local backup_dir="backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup Terraform state
    cp "$TERRAFORM_DIR/terraform.tfstate" "$backup_dir/" 2>/dev/null || true
    
    # Backup task definitions
    local services=("api" "discord-bot" "telegram-bot" "websocket-feed" "scheduler" "ai-trainer")
    
    for service in "${services[@]}"; do
        aws ecs describe-task-definition \
            --task-definition "$PROJECT_NAME-$service" \
            --region "$AWS_REGION" > "$backup_dir/$service-task-definition.json" 2>/dev/null || true
    done
    
    success "Backup created in $backup_dir"
}

# Rollback deployment
rollback_deployment() {
    local backup_dir="$1"
    
    if [ ! -d "$backup_dir" ]; then
        error "Backup directory not found: $backup_dir"
    fi
    
    warning "Rolling back deployment from $backup_dir"
    
    # Restore Terraform state
    if [ -f "$backup_dir/terraform.tfstate" ]; then
        cp "$backup_dir/terraform.tfstate" "$TERRAFORM_DIR/"
    fi
    
    # Restore task definitions
    local services=("api" "discord-bot" "telegram-bot" "websocket-feed" "scheduler" "ai-trainer")
    
    for service in "${services[@]}"; do
        if [ -f "$backup_dir/$service-task-definition.json" ]; then
            log "Rolling back service: $service"
            
            aws ecs register-task-definition \
                --cli-input-json "file://$backup_dir/$service-task-definition.json" \
                --region "$AWS_REGION" > /dev/null
            
            aws ecs update-service \
                --cluster "$PROJECT_NAME-cluster" \
                --service "$PROJECT_NAME-$service" \
                --task-definition "$PROJECT_NAME-$service" \
                --region "$AWS_REGION" > /dev/null
        fi
    done
    
    success "Rollback completed"
}

# Show deployment status
show_status() {
    log "Deployment Status"
    echo "=================="
    
    # ECS Cluster status
    echo "ECS Cluster: $PROJECT_NAME-cluster"
    aws ecs describe-clusters \
        --clusters "$PROJECT_NAME-cluster" \
        --region "$AWS_REGION" \
        --query 'clusters[0].{Status:status,RunningTasks:runningTasksCount,PendingTasks:pendingTasksCount}' \
        --output table
    
    echo ""
    
    # Services status
    echo "ECS Services:"
    local services=("api" "discord-bot" "telegram-bot" "websocket-feed" "scheduler" "ai-trainer")
    
    for service in "${services[@]}"; do
        aws ecs describe-services \
            --cluster "$PROJECT_NAME-cluster" \
            --services "$PROJECT_NAME-$service" \
            --region "$AWS_REGION" \
            --query "services[0].{Service:serviceName,Status:status,Running:runningCount,Desired:desiredCount}" \
            --output table 2>/dev/null || echo "Service $service not found"
    done
    
    echo ""
    
    # Load balancer status
    echo "Load Balancer:"
    ALB_DNS=$(aws elbv2 describe-load-balancers \
        --names "$PROJECT_NAME-alb" \
        --region "$AWS_REGION" \
        --query 'LoadBalancers[0].DNSName' \
        --output text 2>/dev/null || echo "Not found")
    
    echo "DNS: $ALB_DNS"
    
    if [ "$ALB_DNS" != "Not found" ]; then
        echo "Health: $(curl -sf "http://$ALB_DNS/health" && echo "✓ Healthy" || echo "✗ Unhealthy")"
    fi
}

# Main deployment function
deploy() {
    log "Starting AWS deployment for $PROJECT_NAME"
    
    check_prerequisites
    backup_deployment
    deploy_infrastructure
    build_and_push_image
    update_secrets
    update_services
    health_check
    
    success "Deployment completed successfully!"
    show_status
}

# Destroy infrastructure
destroy() {
    warning "This will destroy all AWS infrastructure for $PROJECT_NAME"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log "Destruction cancelled"
        exit 0
    fi
    
    cd "$TERRAFORM_DIR"
    terraform destroy \
        -var="aws_region=$AWS_REGION" \
        -var="environment=$ENVIRONMENT" \
        -var="project_name=$PROJECT_NAME" \
        -auto-approve
    
    success "Infrastructure destroyed"
}

# Show help
show_help() {
    echo "AWS Deployment Script for GenX Trading Platform"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy           Deploy the complete application to AWS"
    echo "  infrastructure   Deploy only the infrastructure"
    echo "  build            Build and push Docker image"
    echo "  services         Update ECS services"
    echo "  secrets          Update application secrets"
    echo "  health           Perform health checks"
    echo "  status           Show current deployment status"
    echo "  backup           Create deployment backup"
    echo "  rollback DIR     Rollback to specific backup"
    echo "  destroy          Destroy all AWS infrastructure"
    echo "  help             Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  AWS_REGION       AWS region (default: us-east-1)"
    echo "  ENVIRONMENT      Environment name (default: production)"
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    infrastructure)
        check_prerequisites
        deploy_infrastructure
        ;;
    build)
        check_prerequisites
        build_and_push_image
        ;;
    services)
        check_prerequisites
        update_services
        ;;
    secrets)
        check_prerequisites
        update_secrets
        ;;
    health)
        health_check
        ;;
    status)
        show_status
        ;;
    backup)
        backup_deployment
        ;;
    rollback)
        if [ $# -lt 2 ]; then
            error "Please specify backup directory for rollback"
        fi
        rollback_deployment "$2"
        ;;
    destroy)
        destroy
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1. Use 'help' to see available commands."
        ;;
esac