#!/bin/bash
# Script to set up NVIDIA GPU drivers on GKE

set -e

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo "gcloud is required but not installed. Aborting."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting."; exit 1; }

# Parse arguments
PROJECT_ID=""
CLUSTER_NAME="mcp-server-gke"
REGION="us-central1"

print_usage() {
  echo "Usage: $0 --project-id=<project_id> [--cluster=<cluster_name>] [--region=<region>]"
  echo "  --project-id  : GCP project ID (required)"
  echo "  --cluster     : GKE cluster name (default: mcp-server-gke)"
  echo "  --region      : GCP region (default: us-central1)"
}

for i in "$@"; do
  case $i in
    --project-id=*)
      PROJECT_ID="${i#*=}"
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

echo "Setting up NVIDIA GPU drivers on GKE"
echo "Project ID: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"

# Configure kubectl to use the GKE cluster
echo "Configuring kubectl to use the GKE cluster..."
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION --project $PROJECT_ID

# Check if the cluster has GPU nodes
GPU_NODES=$(kubectl get nodes -l ai=true --no-headers | wc -l)
if [ "$GPU_NODES" -eq 0 ]; then
  echo "No GPU nodes found in the cluster. Make sure you have created a node pool with GPUs."
  exit 1
fi

echo "Found $GPU_NODES GPU nodes in the cluster."

# Install NVIDIA device plugin
echo "Installing NVIDIA device plugin..."
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml

# Wait for the plugin to be ready
echo "Waiting for NVIDIA device plugin to be ready..."
kubectl -n kube-system wait --for=condition=ready pod -l name=nvidia-device-plugin-ds --timeout=60s

# Verify GPU availability
echo "Verifying GPU availability..."
kubectl get nodes -l ai=true -o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\\.com/gpu

echo "GPU setup complete!"
echo "You can now deploy workloads that use GPUs to the cluster."
