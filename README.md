# AI CV Analyzer Platform

Production-grade, GitOps-managed platform for analyzing CVs using pluggable AI providers, with full observability and experiment tracking.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system architecture and component descriptions.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- kubectl
- minikube
- flux CLI
- age (for SOPS) or External Secrets Operator
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend/worker development)

### Bootstrap Minikube + Flux

```bash
# Create minikube cluster
make minikube-up

# Install Flux
make flux-install

# Bootstrap Flux from local git
make flux-bootstrap

# Or bootstrap from GitHub (if repo is pushed)
# make flux-bootstrap-github
```

### Local Development

```bash
# Start all services locally
make up

# Run tests
make test

# Lint code
make lint

# Load testing
make load-test

# Stop services
make down
```

### Deploy to Kubernetes

```bash
# Apply Flux configurations
kubectl apply -k clusters/dev/

# Check Flux sync status
flux get all -n flux-system

# View logs
kubectl logs -f -n cv-analyzer deployment/backend
kubectl logs -f -n cv-analyzer deployment/worker
```

## Repository Structure

```
.
├── apps/
│   ├── frontend/          # React/Vite frontend
│   ├── backend/           # FastAPI REST API
│   └── worker/            # Async CV analysis worker
├── infra/
│   ├── mlflow/            # MLflow tracking server
│   ├── n8n/               # n8n workflow engine
│   └── observability/     # LGTM + Alloy + Prometheus
├── clusters/
│   └── dev/               # FluxCD GitOps configs
│       ├── flux-system/   # Flux bootstrap
│       ├── infrastructure/ # Base infra (ingress, cert-manager)
│       ├── apps/          # Application kustomizations
│       └── observability/ # Observability kustomizations
├── scripts/               # Bootstrap and utility scripts
├── Makefile              # Common tasks
├── docker-compose.yml    # Local development
└── README.md             # This file
```

## Adding a New AI Provider

1. Create a new provider class in `apps/backend/src/cv_analyzer/providers/` implementing the `AIProvider` interface
2. Add provider configuration in `apps/backend/config.py`
3. Update Kubernetes secrets with provider API key
4. Add provider selection logic in worker service
5. Test with sample CV

See [docs/ADDING_PROVIDER.md](./docs/ADDING_PROVIDER.md) for detailed instructions.

## Viewing Traces/Logs/Metrics

### Grafana Dashboards

```bash
# Port-forward Grafana
kubectl port-forward -n observability svc/grafana 3001:80

# Access at http://localhost:3001
# Default credentials: admin/admin (change on first login)
```

### Loki Logs

```bash
# Query logs via Grafana Explore or Loki API
kubectl port-forward -n observability svc/loki 3100:3100
curl http://localhost:3100/loki/api/v1/query_range?query={job="backend"}
```

### Tempo Traces

```bash
# View traces via Grafana Explore
# Or query Tempo API
kubectl port-forward -n observability svc/tempo 3200:3200
```

### Prometheus Metrics

```bash
# Query metrics
kubectl port-forward -n observability svc/prometheus 9090:9090
# Access at http://localhost:9090
```

## Development Workflow

1. **Local Development**: Use `docker-compose.yml` for rapid iteration
2. **Testing**: Run `make test` to execute unit and integration tests
3. **GitOps**: Push changes, Flux syncs automatically (or manually with `flux reconcile`)
4. **Observability**: Monitor via Grafana dashboards

## Security

- NetworkPolicies enforce default-deny with explicit allows
- RBAC with minimal permissions
- Secrets managed via External Secrets Operator
- PodSecurity policies (restricted mode)
- TLS termination at ingress (cert-manager for prod)

## Troubleshooting

### Flux not syncing

```bash
# Check Flux status
flux get all -n flux-system

# Force reconciliation
flux reconcile source git flux-system -n flux-system
flux reconcile kustomization -n flux-system --all
```

### Pods not starting

```bash
# Check pod status
kubectl get pods -A

# Check events
kubectl describe pod <pod-name> -n <namespace>

# Check logs
kubectl logs <pod-name> -n <namespace>
```

### Services not accessible

```bash
# Check ingress
kubectl get ingress -A

# Check services
kubectl get svc -A

# Check network policies
kubectl get networkpolicies -A
```

## License

MIT
