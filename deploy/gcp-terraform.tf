# Google Cloud Platform Terraform Configuration for GenX Trading Platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Google Cloud Zone"
  type        = string
  default     = "us-central1-a"
}

variable "machine_type" {
  description = "Compute Engine machine type"
  type        = string
  default     = "e2-standard-4"  # 4 vCPUs, 16GB RAM
}

variable "disk_size" {
  description = "Boot disk size in GB"
  type        = number
  default     = 100
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

# Provider
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# VPC Network
resource "google_compute_network" "genx_network" {
  name                    = "genx-trading-network"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "genx_subnet" {
  name          = "genx-trading-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.genx_network.id
}

# Firewall Rules
resource "google_compute_firewall" "genx_firewall_ssh" {
  name    = "genx-trading-ssh"
  network = google_compute_network.genx_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["genx-trading"]
}

resource "google_compute_firewall" "genx_firewall_web" {
  name    = "genx-trading-web"
  network = google_compute_network.genx_network.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["genx-trading"]
}

resource "google_compute_firewall" "genx_firewall_api" {
  name    = "genx-trading-api"
  network = google_compute_network.genx_network.name

  allow {
    protocol = "tcp"
    ports    = ["8000"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["genx-trading"]
}

resource "google_compute_firewall" "genx_firewall_monitoring" {
  name    = "genx-trading-monitoring"
  network = google_compute_network.genx_network.name

  allow {
    protocol = "tcp"
    ports    = ["3000", "9090"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["genx-trading"]
}

# Static IP Address
resource "google_compute_address" "genx_static_ip" {
  name   = "genx-trading-static-ip"
  region = var.region
}

# Service Account
resource "google_service_account" "genx_service_account" {
  account_id   = "genx-trading-vm"
  display_name = "GenX Trading VM Service Account"
  description  = "Service account for GenX Trading Platform VM"
}

# Service Account Key
resource "google_service_account_key" "genx_service_account_key" {
  service_account_id = google_service_account.genx_service_account.name
}

# IAM Role Bindings
resource "google_project_iam_member" "genx_compute_admin" {
  project = var.project_id
  role    = "roles/compute.admin"
  member  = "serviceAccount:${google_service_account.genx_service_account.email}"
}

resource "google_project_iam_member" "genx_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.genx_service_account.email}"
}

resource "google_project_iam_member" "genx_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.genx_service_account.email}"
}

# Cloud Storage Bucket for backups
resource "google_storage_bucket" "genx_backups" {
  name          = "genx-trading-backups-${var.project_id}"
  location      = var.region
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

# Startup script
locals {
  startup_script = <<-EOF
    #!/bin/bash
    
    # Set environment variables
    export GOOGLE_CLOUD_PROJECT=${var.project_id}
    export GOOGLE_CLOUD_REGION=${var.region}
    
    # Update system
    apt-get update
    
    # Download and run setup script
    cd /tmp
    wget https://raw.githubusercontent.com/Mouy-leng/GenX_FX/main/deploy/gcp-vm-setup.sh
    chmod +x gcp-vm-setup.sh
    ./gcp-vm-setup.sh
    
    # Log completion
    echo "GenX Trading Platform setup completed at $(date)" >> /var/log/startup.log
  EOF
}

# Compute Instance
resource "google_compute_instance" "genx_vm" {
  name         = "genx-trading-vm"
  machine_type = var.machine_type
  zone         = var.zone

  tags = ["genx-trading"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = var.disk_size
      type  = "pd-standard"
    }
  }

  network_interface {
    network    = google_compute_network.genx_network.id
    subnetwork = google_compute_subnetwork.genx_subnet.id

    access_config {
      nat_ip = google_compute_address.genx_static_ip.address
    }
  }

  service_account {
    email  = google_service_account.genx_service_account.email
    scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  metadata = {
    startup-script = local.startup_script
  }

  metadata_startup_script = local.startup_script

  # Allow stopping for maintenance
  allow_stopping_for_update = true
}

# Cloud DNS (optional - only if domain is provided)
resource "google_dns_managed_zone" "genx_dns_zone" {
  count       = var.domain_name != "" ? 1 : 0
  name        = "genx-trading-zone"
  dns_name    = "${var.domain_name}."
  description = "DNS zone for GenX Trading Platform"
}

resource "google_dns_record_set" "genx_dns_a" {
  count        = var.domain_name != "" ? 1 : 0
  name         = var.domain_name
  managed_zone = google_dns_managed_zone.genx_dns_zone[0].name
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_address.genx_static_ip.address]
}

resource "google_dns_record_set" "genx_dns_www" {
  count        = var.domain_name != "" ? 1 : 0
  name         = "www.${var.domain_name}"
  managed_zone = google_dns_managed_zone.genx_dns_zone[0].name
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_address.genx_static_ip.address]
}

# Cloud Monitoring Dashboard
resource "google_monitoring_dashboard" "genx_dashboard" {
  dashboard_json = jsonencode({
    displayName = "GenX Trading Platform"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "VM CPU Utilization"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"gce_instance\" AND resource.labels.instance_name=\"genx-trading-vm\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
              }]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "VM Memory Utilization"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"gce_instance\" AND resource.labels.instance_name=\"genx-trading-vm\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
              }]
            }
          }
        }
      ]
    }
  })
}

# Outputs
output "instance_ip" {
  description = "External IP address of the instance"
  value       = google_compute_address.genx_static_ip.address
}

output "instance_name" {
  description = "Name of the instance"
  value       = google_compute_instance.genx_vm.name
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "gcloud compute ssh ${google_compute_instance.genx_vm.name} --zone=${var.zone}"
}

output "api_url" {
  description = "API URL"
  value       = "http://${google_compute_address.genx_static_ip.address}:8000"
}

output "grafana_url" {
  description = "Grafana URL"
  value       = "http://${google_compute_address.genx_static_ip.address}:3000"
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = "http://${google_compute_address.genx_static_ip.address}:9090"
}

output "backup_bucket" {
  description = "Backup bucket name"
  value       = google_storage_bucket.genx_backups.name
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.genx_service_account.email
}

output "domain_nameservers" {
  description = "Domain nameservers (if domain is configured)"
  value       = var.domain_name != "" ? google_dns_managed_zone.genx_dns_zone[0].name_servers : []
}
