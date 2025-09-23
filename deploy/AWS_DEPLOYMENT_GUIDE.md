# AWS Deployment Guide for GenX Trading Platform

This comprehensive guide covers the complete deployment of the GenX Trading Platform to Amazon Web Services (AWS) using modern infrastructure as code practices.

## 🏗️ Architecture Overview

The AWS deployment includes:

- **ECS Fargate** for containerized services
- **RDS PostgreSQL** for relational data storage
- **DocumentDB** for MongoDB-compatible document storage
- **ElastiCache Redis** for caching and session management
- **Application Load Balancer** for traffic routing
- **CloudWatch** for monitoring and logging
- **Secrets Manager** for secure credential storage
- **S3** for backups and static assets
- **ECR** for container image registry

## 📋 Prerequisites

### 1. AWS Account Setup
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Terraform v1.5+ installed
- Docker installed
- Git repository access

### 2. Required AWS Permissions
Your AWS user/role needs the following permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "ecs:*",
        "rds:*",
        "elasticache:*",
        "docdb:*",
        "ecr:*",
        "elbv2:*",
        "logs:*",
        "cloudwatch:*",
        "secretsmanager:*",
        "s3:*",
        "iam:*",
        "application-autoscaling:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Environment Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

## 🚀 Quick Start Deployment

### 1. Clone and Setup
```bash
git clone <your-repository>
cd genx-trading-platform
cd deploy
```

### 2. Configure Variables
Create a `terraform.tfvars` file:
```hcl
aws_region      = "us-east-1"
environment     = "production"
project_name    = "genx-trading"
domain_name     = "your-domain.com"  # Optional
certificate_arn = "arn:aws:acm:..."  # Optional SSL certificate
alert_email     = "admin@your-domain.com"
```

### 3. Deploy Everything
```bash
# Make deploy script executable
chmod +x aws-deploy.sh

# Run complete deployment
./aws-deploy.sh deploy
```

### 4. Configure GitHub Secrets
Add these secrets to your GitHub repository:
```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BYBIT_API_KEY=your-bybit-key
BYBIT_API_SECRET=your-bybit-secret
DISCORD_TOKEN=your-discord-token
TELEGRAM_TOKEN=your-telegram-token
# ... other API keys
```

## 📊 Service Architecture

### Core Services
1. **API Service** (`api`) - Main FastAPI application
2. **Discord Bot** (`discord-bot`) - Discord integration
3. **Telegram Bot** (`telegram-bot`) - Telegram integration
4. **WebSocket Feed** (`websocket-feed`) - Real-time data processing
5. **Scheduler** (`scheduler`) - Cron job management
6. **AI Trainer** (`ai-trainer`) - Machine learning models

### Database Services
- **PostgreSQL RDS** - Primary database
- **DocumentDB** - MongoDB-compatible storage
- **ElastiCache Redis** - Caching layer

### Infrastructure Services
- **Application Load Balancer** - Traffic distribution
- **CloudWatch** - Monitoring and logging
- **Secrets Manager** - Credential management
- **S3** - Backup storage

## 🔧 Configuration Management

### Environment Variables
Each service receives these environment variables:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
MONGODB_URL=mongodb://user:pass@host:27017/db
REDIS_URL=rediss://:pass@host:6379
SECRET_KEY=generated-secret-key
LOG_LEVEL=INFO
```

### Secrets Management
Sensitive data is stored in AWS Secrets Manager:
```json
{
  "BYBIT_API_KEY": "your-key",
  "BYBIT_API_SECRET": "your-secret",
  "DISCORD_TOKEN": "your-token",
  "TELEGRAM_TOKEN": "your-token"
}
```

## 📈 Monitoring and Observability

### CloudWatch Dashboard
Access your monitoring dashboard at:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=genx-trading-dashboard
```

### Key Metrics Monitored
- **ECS Services**: CPU, Memory, Task Count
- **RDS**: CPU, Connections, Storage
- **Redis**: CPU, Memory, Connections
- **ALB**: Response Time, Error Rates
- **Custom**: Trading Signals, API Errors

### Alerts Configuration
Alerts are sent via SNS for:
- High CPU/Memory usage (>80%)
- Database connection issues
- Application errors
- Health check failures

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
The deployment uses GitHub Actions with these stages:

1. **Test** - Run unit tests
2. **Build** - Create Docker images
3. **Deploy Infrastructure** - Terraform apply
4. **Deploy Services** - Update ECS services
5. **Verify** - Health checks
6. **Performance Test** - Load testing
7. **Security Scan** - Vulnerability assessment

### Manual Deployment Commands
```bash
# Deploy infrastructure only
./aws-deploy.sh infrastructure

# Build and push images
./aws-deploy.sh build

# Update services
./aws-deploy.sh services

# Check status
./aws-deploy.sh status

# Health check
./aws-deploy.sh health
```

## 🔒 Security Best Practices

### Network Security
- VPC with public/private subnets
- Security groups with minimal access
- NAT gateways for outbound traffic
- No direct internet access to databases

### Data Security
- Encryption at rest for all databases
- Encryption in transit (TLS/SSL)
- Secrets stored in AWS Secrets Manager
- IAM roles with least privilege

### Container Security
- Regular vulnerability scanning
- Non-root containers
- Minimal base images
- Security updates via automated pipelines

## 📦 Backup and Recovery

### Automated Backups
- **RDS**: 7-day automated backups
- **DocumentDB**: 5-day automated backups
- **Application Data**: S3 backup storage

### Manual Backup
```bash
# Create deployment backup
./aws-deploy.sh backup

# Backup databases manually
aws rds create-db-snapshot \
  --db-instance-identifier genx-trading-postgres \
  --db-snapshot-identifier backup-$(date +%Y%m%d)
```

### Disaster Recovery
```bash
# Rollback to previous deployment
./aws-deploy.sh rollback backups/20240101-120000

# Restore from RDS snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier genx-trading-postgres-restore \
  --db-snapshot-identifier backup-20240101
```

## ⚡ Performance Optimization

### Auto Scaling
The API service auto-scales based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 80%)
- Min instances: 2
- Max instances: 10

### Database Performance
- **RDS**: db.t3.medium with GP3 storage
- **Redis**: cache.t3.micro cluster
- **DocumentDB**: db.t3.medium instances

### Load Balancer Optimization
- Health checks every 30 seconds
- Target group routing
- Sticky sessions for WebSocket connections

## 🚨 Troubleshooting

### Common Issues

#### 1. ECS Service Not Starting
```bash
# Check service status
aws ecs describe-services \
  --cluster genx-trading-cluster \
  --services genx-trading-api

# Check task logs
aws logs get-log-events \
  --log-group-name /ecs/genx-trading \
  --log-stream-name api/api/[task-id]
```

#### 2. Database Connection Issues
```bash
# Test RDS connectivity
aws rds describe-db-instances \
  --db-instance-identifier genx-trading-postgres

# Check security groups
aws ec2 describe-security-groups \
  --group-names genx-trading-rds-*
```

#### 3. Load Balancer Issues
```bash
# Check target health
aws elbv2 describe-target-health \
  --target-group-arn [target-group-arn]

# Check ALB logs (if enabled)
aws s3 ls s3://your-alb-logs-bucket/
```

### Debug Commands
```bash
# Get service logs
aws logs filter-log-events \
  --log-group-name /ecs/genx-trading \
  --filter-pattern "ERROR"

# Check ECS task definitions
aws ecs describe-task-definition \
  --task-definition genx-trading-api

# Monitor real-time logs
aws logs tail /ecs/genx-trading --follow
```

## 💰 Cost Optimization

### Current Estimated Costs (us-east-1)
- **ECS Fargate**: ~$50-150/month
- **RDS PostgreSQL**: ~$30-80/month
- **DocumentDB**: ~$80-200/month
- **ElastiCache**: ~$15-40/month
- **ALB**: ~$20-30/month
- **Data Transfer**: ~$10-50/month

**Total**: ~$205-550/month

### Cost Optimization Tips
1. Use Reserved Instances for RDS
2. Enable auto-scaling for ECS services
3. Use GP3 storage for cost savings
4. Monitor and optimize data transfer
5. Set up billing alerts

## 🔄 Updates and Maintenance

### Regular Maintenance
```bash
# Update services (zero-downtime)
./aws-deploy.sh services

# Update infrastructure
./aws-deploy.sh infrastructure

# Check for security updates
aws ecr get-login-password | docker login --username AWS --password-stdin [ecr-url]
docker pull [image]:latest
```

### Version Management
- Images tagged with Git commit SHA
- Infrastructure versioned with Terraform
- Database migrations handled automatically

## 📞 Support and Resources

### AWS Resources
- [ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [RDS Documentation](https://docs.aws.amazon.com/rds/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)

### Monitoring URLs
After deployment, access these URLs:
- **Application**: `http://[alb-dns-name]`
- **API Docs**: `http://[alb-dns-name]/docs`
- **Health Check**: `http://[alb-dns-name]/health`
- **CloudWatch Dashboard**: See outputs after terraform apply

### Emergency Contacts
For production issues:
1. Check CloudWatch alerts
2. Review application logs
3. Contact platform team
4. Escalate to AWS support if needed

## 🎯 Next Steps

After successful deployment:

1. **Domain Setup**: Configure Route 53 for custom domain
2. **SSL Certificate**: Set up ACM certificate
3. **Monitoring**: Configure additional alerts
4. **Backup Testing**: Test restore procedures
5. **Performance Testing**: Run load tests
6. **Documentation**: Update team documentation

---

This guide provides a complete reference for deploying and managing the GenX Trading Platform on AWS. For additional support, refer to the troubleshooting section or contact the platform team.