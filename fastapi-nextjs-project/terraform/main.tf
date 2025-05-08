terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    # This will be configured via terraform init -backend-config
    # bucket = "your-terraform-state-bucket"
    # prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "compute.googleapis.com",
    "containerregistry.googleapis.com",
    "container.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "sqladmin.googleapis.com",
    "servicenetworking.googleapis.com",
    "artifactregistry.googleapis.com"
  ])
  project = var.project_id
  service = each.key

  disable_dependent_services = true
  disable_on_destroy         = false
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${var.project_prefix}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.services]
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.project_prefix}-subnet"
  ip_cidr_range = "10.0.0.0/16"
  region        = var.region
  network       = google_compute_network.vpc.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/16"
  }
}

# Cloud Router for NAT
resource "google_compute_router" "router" {
  name    = "${var.project_prefix}-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

# NAT Gateway
resource "google_compute_router_nat" "nat" {
  name                               = "${var.project_prefix}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Private IP address for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.project_prefix}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

# Private VPC connection
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Cloud SQL PostgreSQL instance with PostGIS
resource "google_sql_database_instance" "postgres" {
  name             = "${var.project_prefix}-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  depends_on = [
    google_service_networking_connection.private_vpc_connection
  ]

  settings {
    tier              = var.db_tier
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }

    database_flags {
      name  = "cloudsql.enable_pgaudit"
      value = "on"
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"
    }

    backup_configuration {
      enabled            = true
      start_time         = "02:00"
      binary_log_enabled = false
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
  }

  deletion_protection = var.environment == "production" ? true : false
}

# Create PostgreSQL database
resource "google_sql_database" "database" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
}

# Create PostgreSQL user
resource "google_sql_user" "user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Artifact Registry Repository for Docker images
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${var.project_prefix}-repo"
  format        = "DOCKER"
  depends_on    = [google_project_service.services]
}

# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = "${var.project_prefix}-gke"
  location = var.region

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.subnet.id

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All"
    }
  }

  depends_on = [
    google_project_service.services
  ]
}

# GKE Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.project_prefix}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.gke_num_nodes

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/trace.append",
    ]

    labels = {
      env = var.environment
    }

    machine_type = var.gke_machine_type
    disk_size_gb = 100
    disk_type    = "pd-standard"

    metadata = {
      disable-legacy-endpoints = "true"
    }

    tags = ["gke-node", "${var.project_prefix}-gke"]
  }
}

# GPU Node Pool (optional, for AI features)
resource "google_container_node_pool" "gpu_nodes" {
  count      = var.enable_ai_features ? 1 : 0
  name       = "${var.project_prefix}-gpu-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.gke_gpu_nodes

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
    ]

    labels = {
      env = var.environment
      ai  = "true"
    }

    guest_accelerator {
      type  = var.gpu_type
      count = 1
    }

    machine_type = var.gke_gpu_machine_type
    disk_size_gb = 100
    disk_type    = "pd-standard"

    metadata = {
      disable-legacy-endpoints = "true"
    }

    tags = ["gke-node", "gpu-node", "${var.project_prefix}-gke"]
  }
}

# Cloud Storage bucket for uploads
resource "google_storage_bucket" "uploads" {
  name          = "${var.project_id}-uploads"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Service Account for the application
resource "google_service_account" "app_service_account" {
  account_id   = "${var.project_prefix}-app-sa"
  display_name = "Service Account for MCP Server Application"
}

# Grant Storage Object Admin role to the service account for the uploads bucket
resource "google_storage_bucket_iam_member" "app_storage_admin" {
  bucket = google_storage_bucket.uploads.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Grant Cloud SQL Client role to the service account
resource "google_project_iam_member" "app_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Outputs
output "kubernetes_cluster_name" {
  value       = google_container_cluster.primary.name
  description = "GKE Cluster Name"
}

output "kubernetes_cluster_host" {
  value       = "https://${google_container_cluster.primary.endpoint}"
  description = "GKE Cluster Host"
  sensitive   = true
}

output "db_instance_name" {
  value       = google_sql_database_instance.postgres.name
  description = "Cloud SQL instance name"
}

output "db_connection_name" {
  value       = google_sql_database_instance.postgres.connection_name
  description = "Cloud SQL connection name"
}

output "db_private_ip" {
  value       = google_sql_database_instance.postgres.private_ip_address
  description = "Cloud SQL private IP address"
}

output "artifact_registry_repository" {
  value       = google_artifact_registry_repository.repo.name
  description = "Artifact Registry repository"
}

output "uploads_bucket" {
  value       = google_storage_bucket.uploads.name
  description = "Cloud Storage bucket for uploads"
}

output "service_account_email" {
  value       = google_service_account.app_service_account.email
  description = "Service Account email"
}
