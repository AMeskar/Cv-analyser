ex#!/bin/bash
set -e

echo "=== CV Analyzer Platform Bootstrap ==="

# Check prerequisites
command -v kubectl >/dev/null 2>&1 || { echo "kubectl required but not installed. Aborting." >&2; exit 1; }
command -v minikube >/dev/null 2>&1 || { echo "minikube required but not installed. Aborting." >&2; exit 1; }
command -v flux >/dev/null 2>&1 || { echo "flux CLI required but not installed. Aborting." >&2; exit 1; }

# Start minikube
echo "Starting minikube cluster..."
minikube start --cpus=4 --memory=8192 --disk-size=20g || echo "Minikube already running"

# Enable addons
echo "Enabling minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server

# Install Flux
echo "Installing Flux..."
flux install

# Bootstrap Flux from local git
echo "Bootstrapping Flux from local git..."
flux bootstrap git \
  --url=file://$(pwd) \
  --branch=main \
  --path=clusters/dev/flux-system || echo "Flux already bootstrapped"

# Wait for Flux to be ready
echo "Waiting for Flux to be ready..."
kubectl wait --for=condition=ready pod -l app=source-controller -n flux-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=kustomize-controller -n flux-system --timeout=300s

# Apply infrastructure
echo "Applying infrastructure..."
kubectl apply -k clusters/dev/infrastructure

# Apply applications
echo "Applying applications..."
kubectl apply -k clusters/dev/apps/backend
kubectl apply -k clusters/dev/apps/worker
kubectl apply -k clusters/dev/apps/frontend

echo "=== Bootstrap Complete ==="
echo "To access services:"
echo "  Frontend: kubectl port-forward -n cv-analyzer svc/frontend 3000:80"
echo "  Backend: kubectl port-forward -n cv-analyzer svc/backend 8080:8080"
echo "  Grafana: kubectl port-forward -n observability svc/grafana 3001:80"
