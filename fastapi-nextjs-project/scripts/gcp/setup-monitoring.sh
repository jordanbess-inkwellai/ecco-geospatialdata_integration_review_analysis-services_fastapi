#!/bin/bash
# Script to set up monitoring for MCP Server on GCP

set -e

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo "gcloud is required but not installed. Aborting."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting."; exit 1; }

# Parse arguments
PROJECT_ID=""
CLUSTER_NAME="mcp-server-gke"
REGION="us-central1"
DB_INSTANCE="mcp-server-postgres"

print_usage() {
  echo "Usage: $0 --project-id=<project_id> [--cluster=<cluster_name>] [--region=<region>] [--db-instance=<db_instance>]"
  echo "  --project-id  : GCP project ID (required)"
  echo "  --cluster     : GKE cluster name (default: mcp-server-gke)"
  echo "  --region      : GCP region (default: us-central1)"
  echo "  --db-instance : Cloud SQL instance name (default: mcp-server-postgres)"
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
    --db-instance=*)
      DB_INSTANCE="${i#*=}"
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

echo "Setting up monitoring for MCP Server on GCP"
echo "Project ID: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo "DB Instance: $DB_INSTANCE"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable monitoring.googleapis.com \
  cloudprofiler.googleapis.com \
  cloudtrace.googleapis.com \
  --project $PROJECT_ID

# Configure kubectl to use the GKE cluster
echo "Configuring kubectl to use the GKE cluster..."
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION --project $PROJECT_ID

# Install Prometheus and Grafana using Helm
echo "Installing Prometheus and Grafana..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
  echo "Helm is required but not installed. Installing Helm..."
  curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
fi

# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Create ServiceMonitor for MCP Server
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: mcp-server
  namespace: monitoring
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: api
  namespaceSelector:
    matchNames:
      - mcp-server
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
EOF

# Set up Cloud SQL monitoring
echo "Setting up Cloud SQL monitoring..."
gcloud beta monitoring dashboards create \
  --config-from-file=<(cat <<EOF
{
  "displayName": "MCP Server - Cloud SQL",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "CPU Utilization",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\" resource.type=\"cloudsql_database\" resource.label.\"database_id\"=\"$PROJECT_ID:$DB_INSTANCE\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }
          ]
        }
      },
      {
        "title": "Memory Utilization",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudsql.googleapis.com/database/memory/utilization\" resource.type=\"cloudsql_database\" resource.label.\"database_id\"=\"$PROJECT_ID:$DB_INSTANCE\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }
          ]
        }
      },
      {
        "title": "Disk Utilization",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudsql.googleapis.com/database/disk/utilization\" resource.type=\"cloudsql_database\" resource.label.\"database_id\"=\"$PROJECT_ID:$DB_INSTANCE\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }
          ]
        }
      },
      {
        "title": "Connections",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\" resource.type=\"cloudsql_database\" resource.label.\"database_id\"=\"$PROJECT_ID:$DB_INSTANCE\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }
          ]
        }
      }
    ]
  }
}
EOF
) \
  --project=$PROJECT_ID

# Set up GKE monitoring
echo "Setting up GKE monitoring..."
gcloud beta monitoring dashboards create \
  --config-from-file=<(cat <<EOF
{
  "displayName": "MCP Server - GKE",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "CPU Usage",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"kubernetes.io/container/cpu/core_usage_time\" resource.type=\"k8s_container\" resource.label.\"cluster_name\"=\"$CLUSTER_NAME\" resource.label.\"namespace_name\"=\"mcp-server\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE",
                    "crossSeriesReducer": "REDUCE_SUM",
                    "groupByFields": [
                      "resource.label.\"pod_name\""
                    ]
                  }
                }
              }
            }
          ]
        }
      },
      {
        "title": "Memory Usage",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"kubernetes.io/container/memory/used_bytes\" resource.type=\"k8s_container\" resource.label.\"cluster_name\"=\"$CLUSTER_NAME\" resource.label.\"namespace_name\"=\"mcp-server\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN",
                    "crossSeriesReducer": "REDUCE_SUM",
                    "groupByFields": [
                      "resource.label.\"pod_name\""
                    ]
                  }
                }
              }
            }
          ]
        }
      },
      {
        "title": "Network Received Bytes",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"kubernetes.io/pod/network/received_bytes_count\" resource.type=\"k8s_pod\" resource.label.\"cluster_name\"=\"$CLUSTER_NAME\" resource.label.\"namespace_name\"=\"mcp-server\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE",
                    "crossSeriesReducer": "REDUCE_SUM",
                    "groupByFields": [
                      "resource.label.\"pod_name\""
                    ]
                  }
                }
              }
            }
          ]
        }
      },
      {
        "title": "Network Sent Bytes",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"kubernetes.io/pod/network/sent_bytes_count\" resource.type=\"k8s_pod\" resource.label.\"cluster_name\"=\"$CLUSTER_NAME\" resource.label.\"namespace_name\"=\"mcp-server\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE",
                    "crossSeriesReducer": "REDUCE_SUM",
                    "groupByFields": [
                      "resource.label.\"pod_name\""
                    ]
                  }
                }
              }
            }
          ]
        }
      }
    ]
  }
}
EOF
) \
  --project=$PROJECT_ID

# Set up alerting policies
echo "Setting up alerting policies..."
gcloud alpha monitoring policies create \
  --policy-from-file=<(cat <<EOF
{
  "displayName": "MCP Server - High CPU Usage",
  "documentation": {
    "content": "CPU usage is high on MCP Server pods",
    "mimeType": "text/markdown"
  },
  "conditions": [
    {
      "displayName": "CPU Usage > 80%",
      "conditionThreshold": {
        "filter": "metric.type=\"kubernetes.io/container/cpu/limit_utilization\" resource.type=\"k8s_container\" resource.label.\"cluster_name\"=\"$CLUSTER_NAME\" resource.label.\"namespace_name\"=\"mcp-server\"",
        "aggregations": [
          {
            "alignmentPeriod": "300s",
            "perSeriesAligner": "ALIGN_MEAN",
            "crossSeriesReducer": "REDUCE_MEAN",
            "groupByFields": [
              "resource.label.\"pod_name\""
            ]
          }
        ],
        "comparison": "COMPARISON_GT",
        "thresholdValue": 0.8,
        "duration": "300s",
        "trigger": {
          "count": 1
        }
      }
    }
  ],
  "alertStrategy": {
    "autoClose": "604800s"
  },
  "combiner": "OR"
}
EOF
) \
  --project=$PROJECT_ID

gcloud alpha monitoring policies create \
  --policy-from-file=<(cat <<EOF
{
  "displayName": "MCP Server - High Memory Usage",
  "documentation": {
    "content": "Memory usage is high on MCP Server pods",
    "mimeType": "text/markdown"
  },
  "conditions": [
    {
      "displayName": "Memory Usage > 80%",
      "conditionThreshold": {
        "filter": "metric.type=\"kubernetes.io/container/memory/limit_utilization\" resource.type=\"k8s_container\" resource.label.\"cluster_name\"=\"$CLUSTER_NAME\" resource.label.\"namespace_name\"=\"mcp-server\"",
        "aggregations": [
          {
            "alignmentPeriod": "300s",
            "perSeriesAligner": "ALIGN_MEAN",
            "crossSeriesReducer": "REDUCE_MEAN",
            "groupByFields": [
              "resource.label.\"pod_name\""
            ]
          }
        ],
        "comparison": "COMPARISON_GT",
        "thresholdValue": 0.8,
        "duration": "300s",
        "trigger": {
          "count": 1
        }
      }
    }
  ],
  "alertStrategy": {
    "autoClose": "604800s"
  },
  "combiner": "OR"
}
EOF
) \
  --project=$PROJECT_ID

echo "Monitoring setup complete!"
echo "You can access the dashboards in the Cloud Console:"
echo "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo ""
echo "To access Grafana, run:"
echo "kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80"
echo "Then open http://localhost:3000 and log in with username 'admin' and password 'admin'"
