variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "mcp-server"
}

variable "region" {
  description = "The GCP region to deploy resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone to deploy resources"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
  default     = "development"
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "db_tier" {
  description = "The machine type for the Cloud SQL instance"
  type        = string
  default     = "db-custom-2-4096" # 2 vCPUs, 4GB RAM
}

variable "db_name" {
  description = "The name of the database to create"
  type        = string
  default     = "postgres"
}

variable "db_user" {
  description = "The username for the database"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "The password for the database user"
  type        = string
  sensitive   = true
}

variable "gke_num_nodes" {
  description = "Number of nodes in the GKE node pool"
  type        = number
  default     = 2
}

variable "gke_machine_type" {
  description = "Machine type for GKE nodes"
  type        = string
  default     = "e2-standard-2" # 2 vCPUs, 8GB RAM
}

variable "enable_ai_features" {
  description = "Whether to enable AI features and create GPU node pool"
  type        = bool
  default     = false
}

variable "gke_gpu_nodes" {
  description = "Number of GPU nodes in the GKE node pool"
  type        = number
  default     = 1
}

variable "gke_gpu_machine_type" {
  description = "Machine type for GPU nodes"
  type        = string
  default     = "n1-standard-4" # 4 vCPUs, 15GB RAM
}

variable "gpu_type" {
  description = "Type of GPU to attach to nodes"
  type        = string
  default     = "nvidia-tesla-t4"
}
