# Google Cloud VM Deployment Guide

This guide provides step-by-step instructions for deploying the GenX Trading Platform to Google Cloud Platform using Compute Engine VMs.

## Prerequisites

1. **Google Cloud Account**: Active GCP account with billing enabled
2. **Google Cloud SDK**: Install `gcloud` CLI tool
3. **Terraform** (Optional): For infrastructure as code deployment
4. **Domain Name** (Optional): For SSL and custom domain setup

## Deployment Methods

### Method 1: Terraform Deployment (Recommended)

#### 1. Install Terraform
```bash
# Download and install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

#### 2. Configure Google Cloud Authentication
```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable dns.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com
```

#### 3. Deploy Infrastructure
```bash
# Navigate to deploy directory
cd deploy

# Initialize Terraform
terraform init

# Review the plan
terraform plan -var="project_id=YOUR_PROJECT_ID" -var="domain_name=your-domain.com"

# Apply the configuration
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="domain_name=your-domain.com"
```

#### 4. Get Connection Information
```bash
# Get the external IP and SSH command
terraform output instance_ip
terraform output ssh_command
terraform output api_url
terraform output grafana_url
```

### Method 2: Manual Deployment

#### 1. Create VM Instance
```bash
# Create a VM instance
gcloud compute instances create genx-trading-vm \
    --zone=us-central1-a \
    --machine-type=e2-standard-4 \
    --network-tier=PREMIUM \
    --maintenance-policy=MIGRATE \
    --image=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB \
    --boot-disk-type=pd-standard \
    --tags=genx-trading
```

#### 2. Configure Firewall Rules
```bash
# Allow HTTP traffic
gcloud compute firewall-rules create genx-trading-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags genx-trading

# Allow HTTPS traffic
gcloud compute firewall-rules create genx-trading-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags genx-trading

# Allow API traffic
gcloud compute firewall-rules create genx-trading-api \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --target-tags genx-trading

# Allow monitoring traffic
gcloud compute firewall-rules create genx-trading-monitoring \
    --allow tcp:3000,tcp:9090 \
    --source-ranges 0.0.0.0/0 \
    --target-tags genx-trading
```

#### 3. SSH into VM and Run Setup
```bash
# SSH into the VM
gcloud compute ssh genx-trading-vm --zone=us-central1-a

# Download and run setup script
wget https://raw.githubusercontent.com/Mouy-leng/GenX_FX/main/deploy/gcp-vm-setup.sh
chmod +x gcp-vm-setup.sh
sudo ./gcp-vm-setup.sh
```

## Configuration

### 1. Environment Variables
After deployment, SSH into your VM and configure the environment:

```bash
# SSH into VM
gcloud compute ssh genx-trading-vm --zone=us-central1-a

# Edit environment file
sudo nano /opt/genx-trading/.env
```

Update the following variables:
- `BYBIT_API_KEY`: Your Bybit API key
- `BYBIT_API_SECRET`: Your Bybit API secret
- `FXCM_API_KEY`: Your FXCM API key
- `FXCM_API_SECRET`: Your FXCM API secret
- `DISCORD_TOKEN`: Your Discord bot token
- `TELEGRAM_TOKEN`: Your Telegram bot token
- `DOMAIN`: Your domain name (if using custom domain)

### 2. SSL Certificate Setup (Optional)
If you have a domain name:

```bash
# SSH into VM
gcloud compute ssh genx-trading-vm --zone=us-central1-a

# Run Certbot for SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. DNS Configuration (If using custom domain)
If you used Terraform with a domain name, update your domain's nameservers to use Google Cloud DNS:

```bash
# Get nameservers
terraform output domain_nameservers
```

Update your domain registrar to use these nameservers.

## Service Management

### Starting/Stopping Services
```bash
# SSH into VM
gcloud compute ssh genx-trading-vm --zone=us-central1-a

# Start services
sudo systemctl start genx-trading

# Stop services
sudo systemctl stop genx-trading

# Restart services
sudo systemctl restart genx-trading

# Check status
sudo systemctl status genx-trading
```

### Viewing Logs
```bash
# Application logs
sudo docker-compose -f /opt/genx-trading/docker-compose.production.yml logs -f

# System logs
sudo journalctl -u genx-trading -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Monitoring

### Grafana Dashboard
- URL: `http://YOUR_VM_IP:3000/grafana`
- Username: `admin`
- Password: Check `/opt/genx-trading/.env` for `GRAFANA_PASSWORD`

### Prometheus Metrics
- URL: `http://YOUR_VM_IP:9090/prometheus`
- Access restricted to internal networks

### Google Cloud Monitoring
Access the Google Cloud Console to view:
- VM performance metrics
- Custom dashboards
- Alerting policies

## Backup and Recovery

### Automated Backups
The system automatically:
- Creates daily backups at 2 AM
- Uploads backups to Google Cloud Storage
- Retains local backups for 7 days
- Retains cloud backups for 90 days

### Manual Backup
```bash
# SSH into VM
gcloud compute ssh genx-trading-vm --zone=us-central1-a

# Run backup manually
sudo /usr/local/bin/backup-genx.sh
```

### Restore from Backup
```bash
# List available backups
gsutil ls gs://genx-trading-backups-YOUR_PROJECT_ID/backups/

# Download backup
gsutil cp gs://genx-trading-backups-YOUR_PROJECT_ID/backups/postgres_YYYYMMDD_HHMMSS.sql /tmp/

# Restore database
docker exec -i genx-postgres psql -U genx_user -d genx_trading < /tmp/postgres_YYYYMMDD_HHMMSS.sql
```

## Scaling

### Vertical Scaling (Resize VM)
```bash
# Stop the instance
gcloud compute instances stop genx-trading-vm --zone=us-central1-a

# Change machine type
gcloud compute instances set-machine-type genx-trading-vm \
    --machine-type=e2-standard-8 \
    --zone=us-central1-a

# Start the instance
gcloud compute instances start genx-trading-vm --zone=us-central1-a
```

### Horizontal Scaling (Load Balancer)
For high availability, consider setting up:
- Multiple VM instances
- Google Cloud Load Balancer
- Managed instance groups
- Cloud SQL for database

## Security

### Best Practices
1. **Regular Updates**: Keep the system updated
2. **Firewall Rules**: Restrict access to necessary ports only
3. **SSH Keys**: Use SSH keys instead of passwords
4. **SSL Certificates**: Always use HTTPS in production
5. **Service Account**: Use least privilege principle

### Monitoring and Alerts
Set up alerts for:
- High CPU usage
- Memory usage
- Disk space
- API response times
- Failed trading signals

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker status
sudo systemctl status docker

# Check service logs
sudo journalctl -u genx-trading -f

# Check container logs
sudo docker-compose -f /opt/genx-trading/docker-compose.production.yml logs
```

#### Database Connection Issues
```bash
# Check PostgreSQL container
sudo docker exec -it genx-postgres psql -U genx_user -d genx_trading

# Check database logs
sudo docker logs genx-postgres
```

#### Network Issues
```bash
# Check firewall rules
gcloud compute firewall-rules list

# Test connectivity
curl http://localhost:8000/health
```

### Getting Help
- Check logs first: `/opt/genx-trading/logs/`
- Review service status: `systemctl status genx-trading`
- Monitor resource usage: `htop`
- Check Google Cloud Console for VM metrics

## Cost Optimization

### Instance Scheduling
Consider using:
- Preemptible instances for development
- Instance scheduling for non-24/7 workloads
- Committed use discounts for production

### Storage Optimization
- Use appropriate disk types (SSD vs Standard)
- Enable lifecycle policies for backups
- Monitor storage usage regularly

## Cleanup

### Remove All Resources
If using Terraform:
```bash
terraform destroy -var="project_id=YOUR_PROJECT_ID"
```

Manual cleanup:
```bash
# Delete VM instance
gcloud compute instances delete genx-trading-vm --zone=us-central1-a

# Delete firewall rules
gcloud compute firewall-rules delete genx-trading-http genx-trading-https genx-trading-api genx-trading-monitoring

# Delete storage bucket
gsutil rm -r gs://genx-trading-backups-YOUR_PROJECT_ID
```
