# Deployment Guide

## Prerequisites

- Kubernetes cluster (minikube recommended for local)
- kubectl configured
- Flux CLI installed
- Docker (for local development)

## Local Development

### Using Docker Compose

```bash
# Set AI provider API keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Start all services
make up

# Access services:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8080
# - Grafana: http://localhost:3001
# - MLflow: http://localhost:5000
# - n8n: http://localhost:5678
```

### Building Images

```bash
# Build backend
cd apps/backend
docker build -t cv-analyzer-backend:latest .

# Build worker
cd apps/worker
docker build -t cv-analyzer-worker:latest .

# Build frontend
cd apps/frontend
docker build -t cv-analyzer-frontend:latest .
```

## Kubernetes Deployment

### Bootstrap Minikube + Flux

```bash
# Run bootstrap script
./scripts/bootstrap.sh

# Or manually:
minikube start --cpus=4 --memory=8192 --disk-size=20g
minikube addons enable ingress
minikube addons enable metrics-server

flux install
flux bootstrap git --url=file://$(pwd) --branch=main --path=clusters/dev/flux-system
```

### Apply Manifests

```bash
# Apply infrastructure
kubectl apply -k clusters/dev/infrastructure

# Apply applications
kubectl apply -k clusters/dev/apps/backend
kubectl apply -k clusters/dev/apps/worker
kubectl apply -k clusters/dev/apps/frontend

# Apply observability (if using Helm)
# kubectl apply -k clusters/dev/observability
```

### Configure Secrets

Update `clusters/dev/infrastructure/secrets.yaml` with your API keys:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-provider-keys
  namespace: cv-analyzer
type: Opaque
stringData:
  openai-api-key: "your-actual-key"
  anthropic-api-key: "your-actual-key"
```

Apply secrets:
```bash
kubectl apply -f clusters/dev/infrastructure/secrets.yaml
```

### Access Services

```bash
# Port-forward to access services
kubectl port-forward -n cv-analyzer svc/frontend 3000:80
kubectl port-forward -n cv-analyzer svc/backend 8080:8080
kubectl port-forward -n observability svc/grafana 3001:80
kubectl port-forward -n mlflow svc/mlflow 5000:5000

# Or use ingress (if configured)
# Add cv-analyzer.local to /etc/hosts pointing to minikube IP
# Access at http://cv-analyzer.local
```

## Monitoring

### View Logs

```bash
# Backend logs
kubectl logs -f -n cv-analyzer deployment/backend

# Worker logs
kubectl logs -f -n cv-analyzer deployment/worker

# All pods
kubectl get pods -A
```

### View Metrics

```bash
# Prometheus
kubectl port-forward -n observability svc/prometheus 9090:9090
# Access at http://localhost:9090

# Grafana
kubectl port-forward -n observability svc/grafana 3001:80
# Access at http://localhost:3001 (admin/admin)
```

### View Traces

Access Tempo via Grafana Explore:
1. Open Grafana
2. Go to Explore
3. Select Tempo data source
4. Query traces

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl get pods -n cv-analyzer

# Describe pod
kubectl describe pod <pod-name> -n cv-analyzer

# Check events
kubectl get events -n cv-analyzer --sort-by='.lastTimestamp'
```

### Services not accessible

```bash
# Check services
kubectl get svc -n cv-analyzer

# Check ingress
kubectl get ingress -n cv-analyzer

# Check network policies
kubectl get networkpolicies -n cv-analyzer
```

### Flux not syncing

```bash
# Check Flux status
flux get all -n flux-system

# Force reconciliation
flux reconcile source git flux-system -n flux-system
flux reconcile kustomization -n flux-system --all
```

## Production Considerations

1. **Secrets Management**: Use External Secrets Operator or SOPS instead of plain secrets
2. **TLS**: Configure cert-manager for TLS certificates
3. **Resource Limits**: Adjust based on workload
4. **Scaling**: Configure HPA for auto-scaling
5. **Backup**: Set up backups for PostgreSQL and MinIO
6. **Monitoring**: Configure alerting rules in Prometheus
7. **Log Retention**: Configure log retention in Loki
8. **Network Policies**: Review and tighten network policies
9. **Pod Security**: Ensure PodSecurity policies are enforced
10. **Image Security**: Use image scanning and signed images
