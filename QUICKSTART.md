# Quick Start Guide

## Overview

This is a production-grade AI CV Analyzer platform with:
- **Frontend**: React/Vite application
- **Backend**: FastAPI REST API
- **Worker**: Async CV analysis service
- **AI Providers**: OpenAI and Anthropic
- **MLflow**: Experiment tracking
- **n8n**: Workflow orchestration
- **Observability**: LGTM stack (Grafana, Loki, Tempo, Mimir) + Alloy + Prometheus

## Quick Start (Local Development)

### 1. Prerequisites

```bash
# Install Docker and Docker Compose
# Install Node.js 18+ (for frontend)
# Install Python 3.11+ (for backend/worker)
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 3. Start Services

```bash
# Start all services with Docker Compose
make up

# Or manually:
docker-compose up -d
```

### 4. Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **Grafana**: http://localhost:3001 (admin/admin)
- **MLflow**: http://localhost:5000
- **n8n**: http://localhost:5678
- **Prometheus**: http://localhost:9090

### 5. Test the Application

1. Open http://localhost:3000
2. Upload a CV (PDF, DOCX, or TXT)
3. Click "Start Analysis"
4. View the analysis results

## Quick Start (Kubernetes)

### 1. Prerequisites

```bash
# Install minikube, kubectl, flux CLI
```

### 2. Bootstrap

```bash
# Run bootstrap script
./scripts/bootstrap.sh

# Or manually:
minikube start --cpus=4 --memory=8192 --disk-size=20g
minikube addons enable ingress
flux install
flux bootstrap git --url=file://$(pwd) --branch=main --path=clusters/dev/flux-system
```

### 3. Configure Secrets

Edit `clusters/dev/infrastructure/secrets.yaml` with your API keys, then:

```bash
kubectl apply -f clusters/dev/infrastructure/secrets.yaml
```

### 4. Apply Manifests

```bash
kubectl apply -k clusters/dev/infrastructure
kubectl apply -k clusters/dev/apps/backend
kubectl apply -k clusters/dev/apps/worker
kubectl apply -k clusters/dev/apps/frontend
```

### 5. Access Services

```bash
# Port-forward
kubectl port-forward -n cv-analyzer svc/frontend 3000:80
kubectl port-forward -n cv-analyzer svc/backend 8080:8080
kubectl port-forward -n observability svc/grafana 3001:80
```

## Project Structure

```
.
├── apps/
│   ├── frontend/          # React/Vite frontend
│   ├── backend/           # FastAPI REST API
│   └── worker/            # Async CV analysis worker
├── infra/
│   ├── mlflow/            # MLflow configuration
│   ├── n8n/               # n8n configuration
│   └── observability/    # LGTM + Alloy + Prometheus
├── clusters/
│   └── dev/               # FluxCD GitOps configs
│       ├── infrastructure/ # Base infrastructure
│       ├── apps/          # Application kustomizations
│       └── observability/ # Observability kustomizations
├── scripts/               # Bootstrap and utility scripts
├── docs/                  # Documentation
├── docker-compose.yml     # Local development
└── Makefile              # Common tasks
```

## Key Features

### 1. Pluggable AI Providers

- OpenAI (GPT-4)
- Anthropic (Claude)
- Easy to add more (see `docs/ADDING_PROVIDER.md`)

### 2. Full Observability

- **Metrics**: Prometheus + Mimir
- **Logs**: Loki
- **Traces**: Tempo
- **Dashboards**: Grafana
- **Collection**: Grafana Alloy

### 3. Experiment Tracking

- MLflow tracks every analysis
- Logs provider, prompt version, tokens, latency, scores
- Compare experiments

### 4. Workflow Orchestration

- n8n workflows for complex pipelines
- Webhook triggers
- Status updates

### 5. Production-Ready

- Network policies (default deny)
- RBAC with ServiceAccounts
- Resource limits
- Health checks
- Structured logging
- Distributed tracing

## Common Tasks

### Run Tests

```bash
make test
```

### Lint Code

```bash
make lint
```

### Build Images

```bash
cd apps/backend && docker build -t cv-analyzer-backend:latest .
cd apps/worker && docker build -t cv-analyzer-worker:latest .
cd apps/frontend && docker build -t cv-analyzer-frontend:latest .
```

### View Logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f worker

# Kubernetes
kubectl logs -f -n cv-analyzer deployment/backend
kubectl logs -f -n cv-analyzer deployment/worker
```

### Check Metrics

```bash
# Prometheus
curl http://localhost:9090/metrics

# Backend metrics
curl http://localhost:8080/metrics

# Worker metrics
curl http://localhost:9091/metrics
```

## Troubleshooting

### Services not starting

1. Check logs: `docker-compose logs` or `kubectl logs`
2. Check health: `curl http://localhost:8080/health`
3. Check dependencies (Redis, PostgreSQL, MinIO)

### Analysis failing

1. Check worker logs
2. Verify AI provider API keys
3. Check MLflow connection
4. Verify MinIO access

### Flux not syncing

```bash
flux get all -n flux-system
flux reconcile source git flux-system -n flux-system
```

## Next Steps

1. **Configure Secrets**: Update API keys in secrets
2. **Customize Prompts**: Edit `apps/worker/src/cv_analyzer/parsers/prompts.py`
3. **Add Dashboards**: Import Grafana dashboards from `infra/observability/dashboards/`
4. **Set Up Alerts**: Configure Prometheus alerting rules
5. **Add Providers**: Follow `docs/ADDING_PROVIDER.md`

## Documentation

- [Architecture](./ARCHITECTURE.md) - System architecture
- [Deployment](./docs/DEPLOYMENT.md) - Deployment guide
- [Adding Provider](./docs/ADDING_PROVIDER.md) - How to add AI providers

## Support

For issues or questions, check the documentation or review the code structure.
