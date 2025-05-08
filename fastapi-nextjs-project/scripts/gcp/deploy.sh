#!/bin/bash
# Script to deploy MCP Server to GKE

set -e

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo "gcloud is required but not installed. Aborting."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting."; exit 1; }
command -v kustomize >/dev/null 2>&1 || { echo "kustomize is required but not installed. Aborting."; exit 1; }

# Parse arguments
PROJECT_ID=""
CLUSTER_NAME="mcp-server-gke"
REGION="us-central1"
ENABLE_AI="false"

print_usage() {
  echo "Usage: $0 --project-id=<project_id> [--cluster=<cluster_name>] [--region=<region>] [--enable-ai]"
  echo "  --project-id  : GCP project ID (required)"
  echo "  --cluster     : GKE cluster name (default: mcp-server-gke)"
  echo "  --region      : GCP region (default: us-central1)"
  echo "  --enable-ai   : Deploy with AI features enabled (default: false)"
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

echo "Deploying MCP Server to GKE"
echo "Project ID: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Enable AI: $ENABLE_AI"

# Configure kubectl to use the GKE cluster
echo "Configuring kubectl to use the GKE cluster..."
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION --project $PROJECT_ID

# Get Cloud SQL connection information
echo "Getting Cloud SQL connection information..."
DB_INSTANCE=$(gcloud sql instances list --filter="name:mcp-server-postgres" --format="value(name)" --project $PROJECT_ID)
DB_CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)" --project $PROJECT_ID)
DB_PRIVATE_IP=$(gcloud sql instances describe $DB_INSTANCE --format="value(ipAddresses[0].ipAddress)" --project $PROJECT_ID)

# Create a secret for database connection
echo "Creating database connection secret..."
kubectl create namespace mcp-server --dry-run=client -o yaml | kubectl apply -f -

# Get database credentials from Terraform state
DB_USER=$(cd terraform && terraform output -raw db_user 2>/dev/null || echo "postgres")
DB_PASSWORD=$(cd terraform && terraform output -raw db_password 2>/dev/null || echo "changeme")
DB_NAME=$(cd terraform && terraform output -raw db_name 2>/dev/null || echo "postgres")

# Create the database connection string
DB_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_PRIVATE_IP}/${DB_NAME}"

# Create the secret
kubectl create secret generic postgres-secret \
  --namespace=mcp-server \
  --from-literal=DB_USER=$DB_USER \
  --from-literal=DB_PASSWORD=$DB_PASSWORD \
  --from-literal=DB_NAME=$DB_NAME \
  --from-literal=DB_HOST=$DB_PRIVATE_IP \
  --from-literal=DB_PORT=5432 \
  --from-literal=DATABASE_URL=$DB_URL \
  --dry-run=client -o yaml | kubectl apply -f -

# Update image references in Kubernetes manifests
echo "Updating image references in Kubernetes manifests..."
sed -i "s|gcr.io/PROJECT_ID/|gcr.io/${PROJECT_ID}/|g" kubernetes/base/api-deployment.yaml
sed -i "s|gcr.io/PROJECT_ID/|gcr.io/${PROJECT_ID}/|g" kubernetes/base/frontend-deployment.yaml

# Deploy the application
echo "Deploying the application..."
if [ "$ENABLE_AI" = "true" ]; then
  echo "Deploying with AI features enabled..."
  kustomize build kubernetes/overlays/ai-enabled | kubectl apply -f -
else
  echo "Deploying without AI features..."
  kustomize build kubernetes/base | kubectl apply -f -
fi

echo "Deployment complete!"
echo "To access the application, set up an Ingress or use port-forwarding:"
echo "kubectl port-forward svc/frontend -n mcp-server 8080:80"
