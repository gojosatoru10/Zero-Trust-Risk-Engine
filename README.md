# Zero Trust Risk Engine - Cloud Native Deployment

## 📌 Project Overview

This project is an end-to-end cloud-native deployment of a **Zero Trust Risk Engine**. It uses Machine Learning (LightGBM) to analyze login telemetry in real-time and predict whether a user access request is "Safe" or "Malicious."

The system is containerized using **Docker**, orchestrated with **Kubernetes**, and configured with **Horizontal Pod Autoscaling (HPA)** to handle traffic spikes.

## 🚀 Features

- **ML-Based Risk Analysis:** Predicts risk based on MITRE ATT&CK patterns, OS, and Suspicion Level.
- **Hybrid Zero Trust Policy:** Automatically blocks access if the AI predicts a threat OR if the suspicion level is "High."
- **API-First Design:** Built with FastAPI and Uvicorn.
- **Self-Healing:** Implements Kubernetes Liveness and Readiness probes.
- **Auto-Scaling:** Scales from 1 to 5 pods based on CPU usage.

## 🛠️ Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **ML Model:** LightGBM (Scikit-Learn pipeline)
- **Containerization:** Docker
- **Orchestration:** Kubernetes (K8s)

## 🔧 Installation & Setup

### 1. Prerequisites

- Docker Desktop (with Kubernetes enabled)
- Python 3.12+

### 2. Run Locally (Docker)

```bash
# Pull the image
docker pull honoredk10/risk-engine:v1

# Run container
docker run -p 8000:8000 honoredk10/risk-engine:v1

```

### 3. Deploy to Kubernetes

```bash
# Apply all manifests (deployment, service, autoscaling, and health patches)
kubectl apply -f deployment.yaml -f service.yaml -f hpa.yaml -f health-patch.yaml

# Watch pod creation
kubectl get pods -w

# Wait until the deployment becomes ready
kubectl rollout status deployment/risk-engine-deployment

# Manually reset to a single replica (optional)
kubectl scale deployment risk-engine-deployment --replicas=1

# Expose the API locally (Ctrl+C to stop forwarding)
kubectl port-forward service/risk-engine-service 8000:8000

# Hit the FastAPI health endpoint once port-forwarding is active
curl http://127.0.0.1:8000/healthz
```
