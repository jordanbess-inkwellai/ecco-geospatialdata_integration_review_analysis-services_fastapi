# Deployment Guide

This document provides instructions for deploying the MCP Server application in various environments.

## Prerequisites

Before deploying the application, ensure you have the following:

1. Python 3.9 or higher
2. Node.js 16 or higher
3. PostgreSQL 13 or higher with PostGIS extension
4. DuckDB with required extensions
5. Martin server
6. Kestra server (optional)
7. Docker and Docker Compose (for containerized deployment)
8. Kubernetes (for orchestrated deployment)

## Environment Configuration

Create a `.env` file in the root directory with the following variables:

```
# Database settings
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# API settings
API_V1_STR=/api/v1
SECRET_KEY=your-secret-key
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# DuckDB settings
DUCKDB_DATA_DIR=/path/to/duckdb/data
DUCKDB_MEMORY_LIMIT=4GB
DUCKDB_TEMP_DIR=/path/to/duckdb/temp
HOSTFS_ALLOWED_DIRS=/path/to/data,/path/to/uploads,/path/to/exports

# ODBC settings for Nanodbc extension
ODBC_DRIVER_PATHS=/path/to/odbc/drivers
ODBC_CONNECTION_STRINGS={"sqlserver":"Driver={SQL Server};Server=myserver;Database=mydatabase;Trusted_Connection=yes;","oracle":"Driver={Oracle};DBQ=mydb;Uid=myuser;Pwd=mypassword;"}

# Martin settings
MARTIN_SERVER_URL=http://localhost:3000
MARTIN_PG_CONNECTION_STRING=postgresql://postgres:postgres@localhost:5432/postgres
MARTIN_PMTILES_DIRECTORY=/path/to/pmtiles
MARTIN_MBTILES_DIRECTORY=/path/to/mbtiles
MARTIN_RASTER_DIRECTORY=/path/to/raster
MARTIN_TERRAIN_DIRECTORY=/path/to/terrain
MARTIN_DEFAULT_STYLE_DIRECTORY=/path/to/styles

# Kestra settings
KESTRA_API_URL=http://localhost:8080
KESTRA_AUTH_ENABLED=false
KESTRA_DEFAULT_NAMESPACE=default

# Box.com settings
BOX_CLIENT_ID=your-box-client-id
BOX_CLIENT_SECRET=your-box-client-secret
BOX_ENTERPRISE_ID=your-box-enterprise-id

# AI settings
AI_ENABLED=false
```

## Local Development Deployment

### Backend

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Create a `.env.local` file:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

## Docker Deployment

### Using Docker Compose

1. Create a `docker-compose.yml` file:
   ```yaml
   version: '3'

   services:
     db:
       image: postgis/postgis:13-3.1
       environment:
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: postgres
         POSTGRES_DB: postgres
       volumes:
         - postgres_data:/var/lib/postgresql/data
       ports:
         - "5432:5432"

     martin:
       image: urbica/martin:latest
       environment:
         DATABASE_URL: postgres://postgres:postgres@db:5432/postgres
       ports:
         - "3000:3000"
       depends_on:
         - db

     kestra:
       image: kestra/kestra:latest
       environment:
         KESTRA_CONFIGURATION: |
           kestra:
             repository:
               type: postgres
               postgres:
                 url: jdbc:postgresql://db:5432/postgres
                 user: postgres
                 password: postgres
       ports:
         - "8080:8080"
       depends_on:
         - db

     backend:
       build:
         context: .
         dockerfile: Dockerfile.backend
       environment:
         DATABASE_URL: postgresql://postgres:postgres@db:5432/postgres
         MARTIN_SERVER_URL: http://martin:3000
         KESTRA_API_URL: http://kestra:8080
       volumes:
         - ./data:/app/data
       ports:
         - "8000:8000"
       depends_on:
         - db
         - martin
         - kestra

     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile
       environment:
         NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
       ports:
         - "3000:3000"
       depends_on:
         - backend

   volumes:
     postgres_data:
   ```

2. Create a `Dockerfile.backend` file:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       libpq-dev \
       gdal-bin \
       libgdal-dev \
       && rm -rf /var/lib/apt/lists/*

   # Install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Create data directories
   RUN mkdir -p data/duckdb data/martin/pmtiles data/martin/mbtiles data/martin/raster data/martin/terrain data/martin/styles

   # Run migrations
   RUN alembic upgrade head

   # Start the application
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. Create a `Dockerfile` for the frontend:
   ```dockerfile
   FROM node:16-alpine

   WORKDIR /app

   # Install dependencies
   COPY package.json package-lock.json ./
   RUN npm ci

   # Copy application code
   COPY . .

   # Build the application
   RUN npm run build

   # Start the application
   CMD ["npm", "start"]
   ```

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

### Using Docker Swarm

1. Initialize Docker Swarm:
   ```bash
   docker swarm init
   ```

2. Create a `docker-stack.yml` file:
   ```yaml
   version: '3.8'

   services:
     db:
       image: postgis/postgis:13-3.1
       environment:
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: postgres
         POSTGRES_DB: postgres
       volumes:
         - postgres_data:/var/lib/postgresql/data
       ports:
         - "5432:5432"
       deploy:
         replicas: 1
         placement:
           constraints:
             - node.role == manager

     martin:
       image: urbica/martin:latest
       environment:
         DATABASE_URL: postgres://postgres:postgres@db:5432/postgres
       ports:
         - "3000:3000"
       depends_on:
         - db
       deploy:
         replicas: 2

     kestra:
       image: kestra/kestra:latest
       environment:
         KESTRA_CONFIGURATION: |
           kestra:
             repository:
               type: postgres
               postgres:
                 url: jdbc:postgresql://db:5432/postgres
                 user: postgres
                 password: postgres
       ports:
         - "8080:8080"
       depends_on:
         - db
       deploy:
         replicas: 1

     backend:
       image: mcp-server-backend:latest
       environment:
         DATABASE_URL: postgresql://postgres:postgres@db:5432/postgres
         MARTIN_SERVER_URL: http://martin:3000
         KESTRA_API_URL: http://kestra:8080
       volumes:
         - data_volume:/app/data
       ports:
         - "8000:8000"
       depends_on:
         - db
         - martin
         - kestra
       deploy:
         replicas: 3
         update_config:
           parallelism: 1
           delay: 10s
         restart_policy:
           condition: on-failure

     frontend:
       image: mcp-server-frontend:latest
       environment:
         NEXT_PUBLIC_API_URL: http://backend:8000/api/v1
       ports:
         - "3000:3000"
       depends_on:
         - backend
       deploy:
         replicas: 2
         update_config:
           parallelism: 1
           delay: 10s
         restart_policy:
           condition: on-failure

   volumes:
     postgres_data:
     data_volume:
   ```

3. Build the images:
   ```bash
   docker build -t mcp-server-backend:latest -f Dockerfile.backend .
   docker build -t mcp-server-frontend:latest -f frontend/Dockerfile ./frontend
   ```

4. Deploy the stack:
   ```bash
   docker stack deploy -c docker-stack.yml mcp-server
   ```

## Kubernetes Deployment

### Prerequisites

1. A Kubernetes cluster
2. kubectl configured to communicate with your cluster
3. Helm installed

### Deployment Steps

1. Create a namespace:
   ```bash
   kubectl create namespace mcp-server
   ```

2. Create a ConfigMap for environment variables:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: mcp-server-config
     namespace: mcp-server
   data:
     DATABASE_URL: postgresql://postgres:postgres@postgres:5432/postgres
     MARTIN_SERVER_URL: http://martin:3000
     KESTRA_API_URL: http://kestra:8080
     NEXT_PUBLIC_API_URL: http://backend:8000/api/v1
   ```

3. Create a Secret for sensitive information:
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: mcp-server-secrets
     namespace: mcp-server
   type: Opaque
   stringData:
     SECRET_KEY: your-secret-key
     BOX_CLIENT_ID: your-box-client-id
     BOX_CLIENT_SECRET: your-box-client-secret
     BOX_ENTERPRISE_ID: your-box-enterprise-id
   ```

4. Deploy PostgreSQL using Helm:
   ```bash
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm install postgres bitnami/postgresql \
     --namespace mcp-server \
     --set postgresqlUsername=postgres \
     --set postgresqlPassword=postgres \
     --set postgresqlDatabase=postgres \
     --set image.repository=postgis/postgis \
     --set image.tag=13-3.1
   ```

5. Create a deployment for Martin:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: martin
     namespace: mcp-server
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: martin
     template:
       metadata:
         labels:
           app: martin
       spec:
         containers:
         - name: martin
           image: urbica/martin:latest
           env:
           - name: DATABASE_URL
             value: postgres://postgres:postgres@postgres:5432/postgres
           ports:
           - containerPort: 3000
   ```

6. Create a service for Martin:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: martin
     namespace: mcp-server
   spec:
     selector:
       app: martin
     ports:
     - port: 3000
       targetPort: 3000
     type: ClusterIP
   ```

7. Deploy Kestra using Helm:
   ```bash
   helm repo add kestra https://kestra-io.github.io/helm-charts
   helm install kestra kestra/kestra \
     --namespace mcp-server \
     --set postgresql.enabled=false \
     --set externalPostgresql.host=postgres \
     --set externalPostgresql.port=5432 \
     --set externalPostgresql.user=postgres \
     --set externalPostgresql.password=postgres \
     --set externalPostgresql.database=postgres
   ```

8. Create a deployment for the backend:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: backend
     namespace: mcp-server
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: backend
     template:
       metadata:
         labels:
           app: backend
       spec:
         containers:
         - name: backend
           image: mcp-server-backend:latest
           envFrom:
           - configMapRef:
               name: mcp-server-config
           - secretRef:
               name: mcp-server-secrets
           ports:
           - containerPort: 8000
           volumeMounts:
           - name: data-volume
             mountPath: /app/data
         volumes:
         - name: data-volume
           persistentVolumeClaim:
             claimName: data-pvc
   ```

9. Create a service for the backend:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: backend
     namespace: mcp-server
   spec:
     selector:
       app: backend
     ports:
     - port: 8000
       targetPort: 8000
     type: ClusterIP
   ```

10. Create a deployment for the frontend:
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: frontend
      namespace: mcp-server
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: frontend
      template:
        metadata:
          labels:
            app: frontend
        spec:
          containers:
          - name: frontend
            image: mcp-server-frontend:latest
            envFrom:
            - configMapRef:
                name: mcp-server-config
            ports:
            - containerPort: 3000
    ```

11. Create a service for the frontend:
    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: frontend
      namespace: mcp-server
    spec:
      selector:
        app: frontend
      ports:
      - port: 3000
        targetPort: 3000
      type: ClusterIP
    ```

12. Create an Ingress for external access:
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: mcp-server-ingress
      namespace: mcp-server
      annotations:
        nginx.ingress.kubernetes.io/rewrite-target: /
    spec:
      rules:
      - host: mcp-server.example.com
        http:
          paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
    ```

13. Apply all the Kubernetes manifests:
    ```bash
    kubectl apply -f kubernetes/
    ```

## Cloud Deployment

### AWS Deployment

1. Create an Amazon RDS PostgreSQL instance with PostGIS extension
2. Create an Amazon ECS cluster
3. Create task definitions for each service
4. Create ECS services for each task definition
5. Set up an Application Load Balancer
6. Configure Route 53 for DNS

### Azure Deployment

1. Create an Azure Database for PostgreSQL with PostGIS extension
2. Create an Azure Kubernetes Service (AKS) cluster
3. Deploy the application using Kubernetes manifests
4. Set up an Azure Application Gateway
5. Configure Azure DNS for domain name

### Google Cloud Deployment

1. Create a Cloud SQL PostgreSQL instance with PostGIS extension
2. Create a Google Kubernetes Engine (GKE) cluster
3. Deploy the application using Kubernetes manifests
4. Set up a Cloud Load Balancer
5. Configure Cloud DNS for domain name

## Continuous Integration and Deployment

### GitHub Actions

Create a `.github/workflows/ci-cd.yml` file:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgis/postgis:13-3.1
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest --cov=app tests/
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres

    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'

    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci

    - name: Run frontend tests
      run: |
        cd frontend
        npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1

    - name: Login to DockerHub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Build and push backend
      uses: docker/build-push-action@v2
      with:
        context: .
        file: ./Dockerfile.backend
        push: true
        tags: yourusername/mcp-server-backend:latest

    - name: Build and push frontend
      uses: docker/build-push-action@v2
      with:
        context: ./frontend
        file: ./frontend/Dockerfile
        push: true
        tags: yourusername/mcp-server-frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v2

    - name: Set up kubectl
      uses: azure/setup-kubectl@v1

    - name: Set up Kubernetes config
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBE_CONFIG }}" > $HOME/.kube/config

    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f kubernetes/
```

### GitLab CI/CD

Create a `.gitlab-ci.yml` file:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""

test:
  stage: test
  image: python:3.9
  services:
    - name: postgis/postgis:13-3.1
      alias: postgres
  variables:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_DB: postgres
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/postgres
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=app tests/
  only:
    - main
    - merge_requests

build-backend:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE/backend:latest -f Dockerfile.backend .
    - docker push $CI_REGISTRY_IMAGE/backend:latest
  only:
    - main

build-frontend:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE/frontend:latest -f frontend/Dockerfile ./frontend
    - docker push $CI_REGISTRY_IMAGE/frontend:latest
  only:
    - main

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT
    - kubectl apply -f kubernetes/
  only:
    - main
```

## Monitoring and Logging

### Prometheus and Grafana

1. Install Prometheus and Grafana using Helm:
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/prometheus \
     --namespace monitoring \
     --create-namespace

   helm repo add grafana https://grafana.github.io/helm-charts
   helm install grafana grafana/grafana \
     --namespace monitoring \
     --set persistence.enabled=true
   ```

2. Configure Prometheus to scrape the application:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: prometheus-server-conf
     namespace: monitoring
     labels:
       name: prometheus-server-conf
   data:
     prometheus.yml: |-
       global:
         scrape_interval: 15s
         evaluation_interval: 15s
       scrape_configs:
         - job_name: 'kubernetes-pods'
           kubernetes_sd_configs:
             - role: pod
           relabel_configs:
             - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
               action: keep
               regex: true
             - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
               action: replace
               target_label: __metrics_path__
               regex: (.+)
             - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
               action: replace
               regex: ([^:]+)(?::\d+)?;(\d+)
               replacement: $1:$2
               target_label: __address__
             - action: labelmap
               regex: __meta_kubernetes_pod_label_(.+)
             - source_labels: [__meta_kubernetes_namespace]
               action: replace
               target_label: kubernetes_namespace
             - source_labels: [__meta_kubernetes_pod_name]
               action: replace
               target_label: kubernetes_pod_name
   ```

3. Add Prometheus annotations to the backend deployment:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: backend
     namespace: mcp-server
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: backend
     template:
       metadata:
         labels:
           app: backend
         annotations:
           prometheus.io/scrape: "true"
           prometheus.io/port: "8000"
           prometheus.io/path: "/metrics"
       spec:
         containers:
         - name: backend
           image: mcp-server-backend:latest
           # ...
   ```

### ELK Stack

1. Install Elasticsearch, Logstash, and Kibana using Helm:
   ```bash
   helm repo add elastic https://helm.elastic.co
   helm install elasticsearch elastic/elasticsearch \
     --namespace logging \
     --create-namespace

   helm install logstash elastic/logstash \
     --namespace logging

   helm install kibana elastic/kibana \
     --namespace logging \
     --set service.type=LoadBalancer
   ```

2. Install Filebeat to collect logs:
   ```bash
   helm install filebeat elastic/filebeat \
     --namespace logging \
     --set filebeatConfig.filebeat.yml.filebeat.inputs[0].type=container \
     --set filebeatConfig.filebeat.yml.filebeat.inputs[0].paths[0]=/var/log/containers/*.log
   ```

## Backup and Disaster Recovery

### Database Backup

1. Set up regular PostgreSQL backups:
   ```bash
   kubectl create cronjob postgres-backup \
     --image=postgres:13 \
     --schedule="0 1 * * *" \
     --namespace=mcp-server \
     -- sh -c 'pg_dump -h postgres -U postgres -d postgres -f /backup/postgres-$(date +%Y%m%d).sql && aws s3 cp /backup/postgres-$(date +%Y%m%d).sql s3://your-backup-bucket/'
   ```

2. Configure backup retention policy:
   ```bash
   kubectl create cronjob cleanup-backups \
     --image=amazon/aws-cli \
     --schedule="0 2 * * *" \
     --namespace=mcp-server \
     -- sh -c 'aws s3 ls s3://your-backup-bucket/ | sort | head -n -7 | awk "{print \$4}" | xargs -I {} aws s3 rm s3://your-backup-bucket/{}'
   ```

### Application Data Backup

1. Set up regular application data backups:
   ```bash
   kubectl create cronjob data-backup \
     --image=amazon/aws-cli \
     --schedule="0 3 * * *" \
     --namespace=mcp-server \
     -- sh -c 'aws s3 sync /app/data s3://your-backup-bucket/data/'
   ```

## Security Considerations

1. Enable HTTPS with Let's Encrypt:
   ```bash
   helm repo add jetstack https://charts.jetstack.io
   helm install cert-manager jetstack/cert-manager \
     --namespace cert-manager \
     --create-namespace \
     --set installCRDs=true
   ```

2. Create a ClusterIssuer for Let's Encrypt:
   ```yaml
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: your-email@example.com
       privateKeySecretRef:
         name: letsencrypt-prod
       solvers:
       - http01:
           ingress:
             class: nginx
   ```

3. Update the Ingress to use HTTPS:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: mcp-server-ingress
     namespace: mcp-server
     annotations:
       nginx.ingress.kubernetes.io/rewrite-target: /
       cert-manager.io/cluster-issuer: letsencrypt-prod
   spec:
     tls:
     - hosts:
       - mcp-server.example.com
       secretName: mcp-server-tls
     rules:
     - host: mcp-server.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: frontend
               port:
                 number: 3000
         - path: /api
           pathType: Prefix
           backend:
             service:
               name: backend
               port:
                 number: 8000
   ```

4. Set up network policies:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: backend-network-policy
     namespace: mcp-server
   spec:
     podSelector:
       matchLabels:
         app: backend
     policyTypes:
     - Ingress
     - Egress
     ingress:
     - from:
       - podSelector:
           matchLabels:
             app: frontend
       ports:
       - protocol: TCP
         port: 8000
     egress:
     - to:
       - podSelector:
           matchLabels:
             app: postgres
       ports:
       - protocol: TCP
         port: 5432
     - to:
       - podSelector:
           matchLabels:
             app: martin
       ports:
       - protocol: TCP
         port: 3000
     - to:
       - podSelector:
           matchLabels:
             app: kestra
       ports:
       - protocol: TCP
         port: 8080
   ```

## Conclusion

This deployment guide provides instructions for deploying the MCP Server application in various environments. By following these instructions, you can deploy the application in a local development environment, using Docker, Kubernetes, or in the cloud.

Remember to:
1. Configure the environment variables for your specific deployment
2. Set up monitoring and logging
3. Configure backup and disaster recovery
4. Implement security best practices

For more information, refer to the documentation for each component:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/docs/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Martin Documentation](https://martin.maplibre.org/)
- [Kestra Documentation](https://kestra.io/docs/)
