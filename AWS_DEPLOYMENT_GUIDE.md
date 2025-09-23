# GenX_FX AWS Deployment Guide

## Overview
This guide will help you deploy the GenX_FX trading system to AWS using secure authentication methods.

**Account Details:**
- Email: genxapitrading@gmail.com
- Username: keamouyleng

## Prerequisites

### 1. Install AWS CLI
```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# macOS
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### 2. Configure AWS Credentials
**IMPORTANT:** Do NOT use hardcoded credentials in scripts. Use AWS CLI configuration instead.

```bash
# Configure AWS CLI
aws configure
```

When prompted, enter:
- **AWS Access Key ID**: Get this from AWS Console > IAM > Users > keamouyleng > Security credentials
- **AWS Secret Access Key**: Get this from the same location
- **Default region**: Choose your preferred region (e.g., us-east-1, eu-west-1)
- **Default output format**: json

## Deployment Options

### Option 1: Automated Secure Deployment (Recommended)
```bash
# Run the secure deployment script
./aws/secure_deploy.sh
```

This script will:
1. Check AWS CLI installation
2. Guide you through credential setup
3. Create AWS resources (S3, DynamoDB, CloudWatch)
4. Package and deploy your application
5. Create an EC2 instance with your trading system

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Setup AWS Resources
```bash
# Run the setup script
./aws/setup.sh
```

#### Step 2: Deploy Application
```bash
# Run the deployment script
./aws/deploy.sh
```

## What Gets Deployed

### AWS Resources Created:
- **S3 Bucket**: For storing deployment packages and trading data
- **DynamoDB Table**: For storing trading signals and data
- **CloudWatch Log Group**: For application logging
- **EC2 Instance**: t3.medium instance running your trading system
- **Security Group**: Allows SSH (port 22) and application (port 8000) access

### Application Components:
- Core trading logic (`core/`)
- API services (`api/`)
- Utility functions (`utils/`)
- Configuration files (`config/`)
- Main application (`main.py`)
- Dependencies (`requirements.txt`)

## Post-Deployment

### 1. Access Your Instance
```bash
# SSH into your EC2 instance
ssh -i <key-file>.pem ec2-user@<public-ip>
```

### 2. Monitor Your Application
```bash
# Check application logs
sudo journalctl -u genx-ea.service -f

# Check CloudWatch logs
aws logs describe-log-streams --log-group-name "/aws/genx-fx/trading-logs"
```

### 3. View Instance Information
```bash
# Check instance details
cat instance_info.json

# Check AWS configuration
cat aws_config.json
```

## Security Best Practices

### ✅ Do's:
- Use AWS CLI configuration for credentials
- Store sensitive data in AWS Secrets Manager
- Use IAM roles for EC2 instances
- Enable CloudTrail for audit logging
- Regularly update security groups

### ❌ Don'ts:
- Never hardcode credentials in scripts
- Don't commit `.pem` files to version control
- Don't expose unnecessary ports
- Don't use root user for application

## Troubleshooting

### Common Issues:

1. **AWS CLI not configured**
   ```bash
   aws configure
   ```

2. **Permission denied on key file**
   ```bash
   chmod 400 <key-file>.pem
   ```

3. **Instance not accessible**
   - Check security group rules
   - Verify key pair is correct
   - Check instance status in AWS Console

4. **Application not starting**
   ```bash
   # SSH into instance and check logs
   sudo journalctl -u genx-ea.service
   ```

## Cost Optimization

### Estimated Monthly Costs (us-east-1):
- **EC2 t3.medium**: ~$30/month
- **S3 Storage**: ~$0.023/GB/month
- **DynamoDB**: Pay per request (~$1-5/month for typical usage)
- **CloudWatch**: ~$0.50/month for basic logging

### Cost Reduction Tips:
- Use Spot Instances for non-critical workloads
- Set up S3 lifecycle policies
- Monitor and optimize DynamoDB usage
- Use CloudWatch alarms for cost alerts

## Support

For issues or questions:
1. Check the logs in CloudWatch
2. Review the `instance_info.json` file
3. SSH into the instance for debugging
4. Check AWS Console for resource status

## Next Steps

After successful deployment:
1. Configure your trading parameters
2. Set up monitoring and alerts
3. Implement backup strategies
4. Consider scaling options (Auto Scaling Groups, Load Balancers)
5. Set up CI/CD pipelines for future deployments

---

**Note**: This deployment uses secure authentication methods and follows AWS best practices. Never share your AWS credentials or private key files.