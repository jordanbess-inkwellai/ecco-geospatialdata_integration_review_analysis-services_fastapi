#!/bin/bash
# Script to set up Cloud Build for CI/CD

set -e

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo "gcloud is required but not installed. Aborting."; exit 1; }

# Parse arguments
PROJECT_ID=""
REPO_NAME="github_yourusername_mcp-server"
BRANCH_PATTERN="^main$"
CLUSTER_NAME="mcp-server-gke"
REGION="us-central1"

print_usage() {
  echo "Usage: $0 --project-id=<project_id> [--repo=<repo_name>] [--branch=<branch_pattern>] [--cluster=<cluster_name>] [--region=<region>]"
  echo "  --project-id  : GCP project ID (required)"
  echo "  --repo        : Cloud Source Repository name (default: github_yourusername_mcp-server)"
  echo "  --branch      : Branch pattern to trigger builds (default: ^main$)"
  echo "  --cluster     : GKE cluster name (default: mcp-server-gke)"
  echo "  --region      : GCP region (default: us-central1)"
}

for i in "$@"; do
  case $i in
    --project-id=*)
      PROJECT_ID="${i#*=}"
      shift
      ;;
    --repo=*)
      REPO_NAME="${i#*=}"
      shift
      ;;
    --branch=*)
      BRANCH_PATTERN="${i#*=}"
      shift
      ;;
    --cluster=*)
      CLUSTER_NAME="${i#*=}"
      shift
      ;;
    --region=*)
      REGION="${i#*=}"
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

echo "Setting up Cloud Build for CI/CD"
echo "Project ID: $PROJECT_ID"
echo "Repository: $REPO_NAME"
echo "Branch Pattern: $BRANCH_PATTERN"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com \
  container.googleapis.com \
  containerregistry.googleapis.com \
  --project $PROJECT_ID

# Get the project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Grant the Cloud Build service account permissions to deploy to GKE
echo "Granting Cloud Build service account permissions to deploy to GKE..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/container.developer"

# Create a Cloud Build trigger
echo "Creating Cloud Build trigger..."
gcloud builds triggers create github \
  --name="mcp-server-deploy" \
  --repo=$REPO_NAME \
  --branch-pattern=$BRANCH_PATTERN \
  --build-config="cloudbuild.yaml" \
  --substitutions="_CLOUDSDK_COMPUTE_ZONE=$REGION,_CLOUDSDK_CONTAINER_CLUSTER=$CLUSTER_NAME" \
  --project=$PROJECT_ID

echo "Cloud Build setup complete!"
echo "The CI/CD pipeline will be triggered on pushes to the $BRANCH_PATTERN branch."
