# Google Cloud Deployment Guide

This guide provides instructions for deploying the MCP Server application to Google Cloud Platform (GCP) using Terraform, Kubernetes, and Cloud Build.

## Prerequisites

Before you begin, make sure you have the following:

1. A Google Cloud Platform account
2. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured
3. [Terraform](https://www.terraform.io/downloads.html) installed (version 1.0.0 or later)
4. [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) installed
5. [kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/) installed

## Infrastructure Setup with Terraform

The project includes Terraform configurations to set up the required infrastructure on Google Cloud Platform.

### 1. Create a New GCP Project (Optional)

If you don't have a GCP project yet, create one:

```bash
gcloud projects create YOUR_PROJECT_ID --name="MCP Server"
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Billing for Your Project

Make sure billing is enabled for your project. You can do this through the [Google Cloud Console](https://console.cloud.google.com/billing/projects).

### 3. Run the Setup Script

We provide a setup script that creates a GCS bucket for Terraform state and generates the necessary configuration files:

```bash
cd fastapi-nextjs-project
chmod +x scripts/gcp/setup-project.sh
./scripts/gcp/setup-project.sh --project-id=YOUR_PROJECT_ID [--region=us-central1] [--zone=us-central1-a] [--enable-ai]
```

### 4. Review and Apply Terraform Configuration

Review the generated `terraform.tfvars` file and make any necessary adjustments:

```bash
cd terraform
# Review the configuration
cat terraform.tfvars
# Apply the configuration
terraform apply
```

This will create the following resources:
- VPC network and subnet
- Cloud SQL PostgreSQL instance with PostGIS
- GKE cluster with node pools
- Cloud Storage bucket for uploads
- Artifact Registry repository for Docker images
- Service accounts and IAM permissions

## Application Deployment

After the infrastructure is set up, you can deploy the application to GKE.

### 1. Build and Push Docker Images

You can build and push the Docker images manually:

```bash
# Build API image
docker build -t gcr.io/YOUR_PROJECT_ID/mcp-server-api:latest .
# Build Frontend image
docker build -t gcr.io/YOUR_PROJECT_ID/mcp-server-frontend:latest ./frontend
# Push images to Artifact Registry
docker push gcr.io/YOUR_PROJECT_ID/mcp-server-api:latest
docker push gcr.io/YOUR_PROJECT_ID/mcp-server-frontend:latest
```

For AI-enabled builds:

```bash
# Build AI-enabled API image
docker build -t gcr.io/YOUR_PROJECT_ID/mcp-server-api-ai:latest \
  --build-arg ENABLE_AI_FEATURES=true \
  --build-arg AI_MODEL_TYPE=jellyfish \
  .
# Push AI-enabled image
docker push gcr.io/YOUR_PROJECT_ID/mcp-server-api-ai:latest
```

### 2. Deploy to GKE

Use the provided deployment script:

```bash
chmod +x scripts/gcp/deploy.sh
./scripts/gcp/deploy.sh --project-id=YOUR_PROJECT_ID [--cluster=mcp-server-gke] [--region=us-central1] [--enable-ai]
```

This script will:
1. Configure kubectl to use your GKE cluster
2. Create the necessary Kubernetes secrets
3. Deploy the application using kustomize

## Setting Up CI/CD with Cloud Build

You can set up continuous integration and deployment using Cloud Build.

### 1. Connect Your GitHub Repository

Follow the [Cloud Build documentation](https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github) to connect your GitHub repository to Cloud Build.

### 2. Set Up Cloud Build Trigger

Use the provided script to set up a Cloud Build trigger:

```bash
chmod +x scripts/gcp/setup-cloudbuild.sh
./scripts/gcp/setup-cloudbuild.sh --project-id=YOUR_PROJECT_ID [--repo=github_yourusername_mcp-server] [--branch=^main$] [--cluster=mcp-server-gke] [--region=us-central1]
```

This will create a Cloud Build trigger that automatically builds and deploys your application when you push to the specified branch.

## Accessing the Application

### 1. Set Up DNS (Optional)

If you want to use a custom domain, create a DNS A record pointing to the external IP address of your GKE ingress:

```bash
# Get the external IP address
kubectl get ingress mcp-server-ingress -n mcp-server -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### 2. Access via IP Address or Port Forwarding

You can access the application using the external IP address of the ingress, or use port forwarding for testing:

```bash
# Port forwarding for frontend
kubectl port-forward svc/frontend -n mcp-server 8080:80
# Port forwarding for API
kubectl port-forward svc/api -n mcp-server 8000:80
```

Then access the application at http://localhost:8080 and the API at http://localhost:8000.

## AI Features

If you deployed with AI features enabled, you can access the AI-specific functionality through the frontend.

The AI-enabled deployment:
- Uses GPU-equipped nodes for the API
- Loads the specified AI model (default: Jellyfish-13B)
- Enables AI-specific UI elements in the frontend

## Monitoring and Logging

### Cloud Monitoring

You can monitor your GKE cluster and Cloud SQL instance using Cloud Monitoring:

1. Go to the [Cloud Monitoring Console](https://console.cloud.google.com/monitoring)
2. Navigate to "Dashboards" and select "GKE" or "Cloud SQL"

### Cloud Logging

View application logs in Cloud Logging:

1. Go to the [Cloud Logging Console](https://console.cloud.google.com/logs)
2. Use the following query to view API logs:
   ```
   resource.type="k8s_container"
   resource.labels.namespace_name="mcp-server"
   resource.labels.container_name="api"
   ```

## Scaling

### Horizontal Pod Autoscaling

You can set up Horizontal Pod Autoscaling for your deployments:

```bash
kubectl autoscale deployment api -n mcp-server --cpu-percent=80 --min=2 --max=10
kubectl autoscale deployment frontend -n mcp-server --cpu-percent=80 --min=2 --max=10
```

### Vertical Pod Autoscaling

For more efficient resource usage, consider setting up Vertical Pod Autoscaler:

1. Enable the Vertical Pod Autoscaler in your GKE cluster
2. Create VPA resources for your deployments

## Cleanup

To avoid incurring charges, you can delete the resources when they're no longer needed:

```bash
# Delete Kubernetes resources
kubectl delete namespace mcp-server

# Destroy Terraform-managed resources
cd terraform
terraform destroy
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check the database secret: `kubectl get secret postgres-secret -n mcp-server -o yaml`
   - Verify the Cloud SQL instance is running: `gcloud sql instances describe mcp-server-postgres`

2. **Pod Startup Issues**
   - Check pod logs: `kubectl logs -n mcp-server deployment/api`
   - Check pod events: `kubectl describe pod -n mcp-server -l app=api`

3. **AI Model Loading Issues**
   - Check GPU availability: `kubectl describe nodes -l ai=true`
   - Check pod resource allocation: `kubectl describe pod -n mcp-server -l app=api`

### Getting Help

If you encounter issues not covered in this guide, please:
1. Check the project documentation
2. Open an issue on the GitHub repository
3. Contact the project maintainers
