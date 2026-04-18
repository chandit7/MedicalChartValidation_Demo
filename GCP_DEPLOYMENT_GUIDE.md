# Deploy Medical Chart Validation System to Google Cloud Platform (GCP)

This guide covers multiple deployment options for running your Dockerized application on GCP.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Option 1: Cloud Run (Recommended - Easiest)](#option-1-cloud-run-recommended)
3. [Option 2: Google Kubernetes Engine (GKE)](#option-2-google-kubernetes-engine-gke)
4. [Option 3: Compute Engine VM](#option-3-compute-engine-vm)
5. [Option 4: App Engine Flexible](#option-4-app-engine-flexible)
6. [Cost Comparison](#cost-comparison)

---

## Prerequisites

### 1. Install Google Cloud SDK

**Windows (PowerShell):**
```powershell
# Download and install
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**Or download from**: https://cloud.google.com/sdk/docs/install

### 2. Initialize gcloud

```bash
# Login to your Google account
gcloud auth login

# Set your project (replace YOUR_PROJECT_ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Set Environment Variables

```bash
# Set your GCP project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"  # Choose your preferred region
export SERVICE_NAME="medchart-app"
```

---

## Option 1: Cloud Run (Recommended)

**Best for**: Serverless, auto-scaling, pay-per-use, easiest deployment

### Step 1: Build and Push Docker Image

```bash
# Build the image
docker build -t gcr.io/$PROJECT_ID/medchart-app:latest .

# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/medchart-app:latest
```

### Step 2: Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy medchart-app \
  --image gcr.io/$PROJECT_ID/medchart-app:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "STREAMLIT_SERVER_PORT=8501,STREAMLIT_SERVER_ADDRESS=0.0.0.0"
```

### Step 3: Add Persistent Storage (Optional)

Cloud Run is stateless by default. For persistent database:

**Option A: Use Cloud SQL**
```bash
# Create Cloud SQL instance
gcloud sql instances create medchart-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=$REGION

# Connect Cloud Run to Cloud SQL
gcloud run services update medchart-app \
  --add-cloudsql-instances $PROJECT_ID:$REGION:medchart-db
```

**Option B: Use Cloud Storage**
```bash
# Create a bucket for database
gsutil mb -l $REGION gs://$PROJECT_ID-medchart-data

# Mount in Cloud Run (requires custom setup)
```

### Step 4: Access Your Application

```bash
# Get the service URL
gcloud run services describe medchart-app --region=$REGION --format='value(status.url)'
```

Visit the URL in your browser!

### Step 5: Update Deployment

```bash
# Rebuild and redeploy
docker build -t gcr.io/$PROJECT_ID/medchart-app:latest .
docker push gcr.io/$PROJECT_ID/medchart-app:latest
gcloud run deploy medchart-app --image gcr.io/$PROJECT_ID/medchart-app:latest --region=$REGION
```

---

## Option 2: Google Kubernetes Engine (GKE)

**Best for**: Complex applications, microservices, full control

### Step 1: Create GKE Cluster

```bash
# Create a cluster
gcloud container clusters create medchart-cluster \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --region=$REGION \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=3
```

### Step 2: Build and Push Image

```bash
# Build and push
docker build -t gcr.io/$PROJECT_ID/medchart-app:latest .
docker push gcr.io/$PROJECT_ID/medchart-app:latest
```

### Step 3: Create Kubernetes Manifests

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: medchart-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: medchart-app
  template:
    metadata:
      labels:
        app: medchart-app
    spec:
      containers:
      - name: medchart-app
        image: gcr.io/YOUR_PROJECT_ID/medchart-app:latest
        ports:
        - containerPort: 8501
        env:
        - name: STREAMLIT_SERVER_PORT
          value: "8501"
        - name: STREAMLIT_SERVER_ADDRESS
          value: "0.0.0.0"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: medchart-service
spec:
  type: LoadBalancer
  selector:
    app: medchart-app
  ports:
  - port: 80
    targetPort: 8501
```

### Step 4: Deploy to GKE

```bash
# Get cluster credentials
gcloud container clusters get-credentials medchart-cluster --region=$REGION

# Apply manifests
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods
kubectl get services

# Get external IP
kubectl get service medchart-service
```

### Step 5: Add Persistent Volume

Create `k8s-pvc.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: medchart-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

Update deployment to use PVC:

```yaml
# Add to deployment spec
volumes:
- name: data-volume
  persistentVolumeClaim:
    claimName: medchart-data

# Add to container spec
volumeMounts:
- name: data-volume
  mountPath: /app/data
```

---

## Option 3: Compute Engine VM

**Best for**: Full control, traditional VM deployment

### Step 1: Create VM Instance

```bash
# Create VM with Docker pre-installed
gcloud compute instances create medchart-vm \
  --image-family=cos-stable \
  --image-project=cos-cloud \
  --machine-type=e2-medium \
  --zone=us-central1-a \
  --tags=http-server,https-server \
  --metadata=startup-script='#!/bin/bash
    docker pull gcr.io/'$PROJECT_ID'/medchart-app:latest
    docker run -d -p 80:8501 \
      -v /mnt/data:/app/data \
      --name medchart-app \
      gcr.io/'$PROJECT_ID'/medchart-app:latest'
```

### Step 2: Configure Firewall

```bash
# Allow HTTP traffic
gcloud compute firewall-rules create allow-medchart \
  --allow tcp:80 \
  --target-tags http-server \
  --description "Allow HTTP traffic to medchart app"
```

### Step 3: Get External IP

```bash
# Get the external IP
gcloud compute instances describe medchart-vm \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### Step 4: SSH and Manage

```bash
# SSH into VM
gcloud compute ssh medchart-vm --zone=us-central1-a

# Inside VM - check logs
docker logs medchart-app

# Update application
docker pull gcr.io/$PROJECT_ID/medchart-app:latest
docker stop medchart-app
docker rm medchart-app
docker run -d -p 80:8501 -v /mnt/data:/app/data --name medchart-app gcr.io/$PROJECT_ID/medchart-app:latest
```

---

## Option 4: App Engine Flexible

**Best for**: Managed platform, automatic scaling

### Step 1: Create `app.yaml`

```yaml
runtime: custom
env: flex

service: medchart-app

automatic_scaling:
  min_num_instances: 1
  max_num_instances: 3
  cpu_utilization:
    target_utilization: 0.65

resources:
  cpu: 2
  memory_gb: 2
  disk_size_gb: 10

network:
  forwarded_ports:
    - 8501

env_variables:
  STREAMLIT_SERVER_PORT: "8501"
  STREAMLIT_SERVER_ADDRESS: "0.0.0.0"
```

### Step 2: Deploy

```bash
# Deploy to App Engine
gcloud app deploy app.yaml

# View logs
gcloud app logs tail -s medchart-app

# Get URL
gcloud app browse
```

---

## Cost Comparison

### Monthly Cost Estimates (Approximate)

| Service | Configuration | Estimated Cost/Month |
|---------|--------------|---------------------|
| **Cloud Run** | 2 vCPU, 2GB RAM, 1M requests | $15-30 |
| **GKE** | 2 nodes, e2-medium | $50-80 |
| **Compute Engine** | 1 VM, e2-medium | $25-35 |
| **App Engine Flex** | 1-3 instances | $40-70 |

**Recommendation**: Start with **Cloud Run** for lowest cost and easiest management.

---

## Complete Deployment Script

Save this as `deploy-to-gcp.sh`:

```bash
#!/bin/bash

# Configuration
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="medchart-app"

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build image
echo "Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# Configure Docker
echo "Configuring Docker authentication..."
gcloud auth configure-docker

# Push image
echo "Pushing image to GCR..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "STREAMLIT_SERVER_PORT=8501,STREAMLIT_SERVER_ADDRESS=0.0.0.0,STREAMLIT_SERVER_HEADLESS=true"

# Get service URL
echo "Deployment complete!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "Your application is available at: $SERVICE_URL"
```

### Run the script:

```bash
# Make executable
chmod +x deploy-to-gcp.sh

# Run
./deploy-to-gcp.sh
```

---

## Monitoring and Logging

### View Logs

```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=medchart-app" --limit 50

# Or use Cloud Console
# https://console.cloud.google.com/logs
```

### Set Up Monitoring

```bash
# Create uptime check
gcloud monitoring uptime create medchart-uptime \
  --resource-type=uptime-url \
  --host=YOUR_SERVICE_URL \
  --path=/_stcore/health
```

---

## Security Best Practices

### 1. Use Secret Manager for API Keys

```bash
# Create secret
echo -n "your-groq-api-key" | gcloud secrets create groq-api-key --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding groq-api-key \
  --member=serviceAccount:YOUR_SERVICE_ACCOUNT \
  --role=roles/secretmanager.secretAccessor

# Update Cloud Run to use secret
gcloud run services update medchart-app \
  --update-secrets=GROQ_API_KEY=groq-api-key:latest
```

### 2. Enable HTTPS Only

```bash
# Cloud Run enforces HTTPS by default
# For custom domain:
gcloud run domain-mappings create --service medchart-app --domain your-domain.com
```

### 3. Restrict Access

```bash
# Remove public access
gcloud run services remove-iam-policy-binding medchart-app \
  --member="allUsers" \
  --role="roles/run.invoker"

# Add specific users
gcloud run services add-iam-policy-binding medchart-app \
  --member="user:email@example.com" \
  --role="roles/run.invoker"
```

---

## Troubleshooting

### Issue: Container fails to start

```bash
# Check logs
gcloud run services logs read medchart-app --limit=50

# Common fixes:
# 1. Ensure port 8501 is exposed
# 2. Check environment variables
# 3. Verify image builds locally first
```

### Issue: Out of memory

```bash
# Increase memory
gcloud run services update medchart-app --memory 4Gi
```

### Issue: Slow cold starts

```bash
# Set minimum instances
gcloud run services update medchart-app --min-instances 1
```

---

## Cleanup

### Remove Cloud Run Service

```bash
gcloud run services delete medchart-app --region=$REGION
```

### Remove GKE Cluster

```bash
gcloud container clusters delete medchart-cluster --region=$REGION
```

### Remove Compute Engine VM

```bash
gcloud compute instances delete medchart-vm --zone=us-central1-a
```

### Remove Container Images

```bash
gcloud container images delete gcr.io/$PROJECT_ID/medchart-app:latest
```

---

## Next Steps

1. **Set up CI/CD**: Use Cloud Build for automated deployments
2. **Add Custom Domain**: Map your domain to Cloud Run
3. **Enable Monitoring**: Set up alerts and dashboards
4. **Implement Backups**: Regular database backups to Cloud Storage
5. **Load Testing**: Test with expected traffic patterns

---

## Support Resources

- **GCP Documentation**: https://cloud.google.com/docs
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **GKE Docs**: https://cloud.google.com/kubernetes-engine/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-11  
**Author**: Bob (Plan Mode)