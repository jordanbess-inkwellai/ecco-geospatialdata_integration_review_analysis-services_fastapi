#!/bin/bash
# Script to set up a new GCP project for MCP Server deployment

set -e

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo "gcloud is required but not installed. Aborting."; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "terraform is required but not installed. Aborting."; exit 1; }

# Parse arguments
PROJECT_ID=""
REGION="us-central1"
ZONE="us-central1-a"
ENABLE_AI="false"

print_usage() {
  echo "Usage: $0 --project-id=<project_id> [--region=<region>] [--zone=<zone>] [--enable-ai]"
  echo "  --project-id  : GCP project ID (required)"
  echo "  --region      : GCP region (default: us-central1)"
  echo "  --zone        : GCP zone (default: us-central1-a)"
  echo "  --enable-ai   : Enable AI features (default: false)"
}

for i in "$@"; do
  case $i in
    --project-id=*)
      PROJECT_ID="${i#*=}"
      shift
      ;;
    --region=*)
      REGION="${i#*=}"
      shift
      ;;
    --zone=*)
      ZONE="${i#*=}"
      shift
      ;;
    --enable-ai)
      ENABLE_AI="true"
      shift
      ;;
    --help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $i"
      print_usage
      exit 1
      ;;
  esac
done

if [ -z "$PROJECT_ID" ]; then
  echo "Error: --project-id is required"
  print_usage
  exit 1
fi

echo "Setting up GCP project: $PROJECT_ID"
echo "Region: $REGION"
echo "Zone: $ZONE"
echo "Enable AI: $ENABLE_AI"

# Create a GCS bucket for Terraform state
BUCKET_NAME="${PROJECT_ID}-terraform-state"
echo "Creating GCS bucket for Terraform state: $BUCKET_NAME"
gsutil mb -l $REGION gs://$BUCKET_NAME || {
  echo "Failed to create GCS bucket. It might already exist or you don't have permissions."
  echo "Continuing with setup..."
}

# Create terraform.tfvars file
echo "Creating terraform.tfvars file..."
cat > terraform/terraform.tfvars <<EOF
project_id        = "$PROJECT_ID"
project_prefix    = "mcp-server"
region            = "$REGION"
zone              = "$ZONE"
environment       = "development"

# Database settings
db_tier           = "db-custom-2-4096"  # 2 vCPUs, 4GB RAM
db_name           = "postgres"
db_user           = "postgres"
db_password       = "$(openssl rand -base64 12)"

# GKE settings
gke_num_nodes     = 2
gke_machine_type  = "e2-standard-2"  # 2 vCPUs, 8GB RAM

# AI features
enable_ai_features = $ENABLE_AI
gke_gpu_nodes      = 1
gke_gpu_machine_type = "n1-standard-4"  # 4 vCPUs, 15GB RAM
gpu_type           = "nvidia-tesla-t4"
EOF

echo "Initializing Terraform..."
cd terraform
terraform init -backend-config="bucket=$BUCKET_NAME" -backend-config="prefix=terraform/state"

echo "Setup complete!"
echo "To deploy the infrastructure, run:"
echo "cd terraform && terraform apply"
