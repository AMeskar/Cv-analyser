# AI CV Analyzer - Architecture

## Overview

Production-grade, GitOps-managed platform for analyzing CVs using pluggable AI providers, with full observability and experiment tracking.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ingress (nginx)                              │
│              TLS termination, routing                           │
└───────────────┬───────────────────────┬─────────────────────────┘
                │                       │
        ┌───────▼───────┐      ┌────────▼────────┐
        │   Frontend    │      │    Backend      │
        │  (React/Vite) │◄─────┤  (REST API)     │
        │   Port: 3000  │      │   Port: 8080    │
        └───────────────┘      └────────┬────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
            ┌───────▼──────┐    ┌───────▼──────┐    ┌────────▼────────┐
            │   MinIO      │    │    Redis     │    │   PostgreSQL    │
            │  (S3 API)    │    │   (Queue)    │    │   (Metadata)    │
            └──────────────┘    └───────┬──────┘    └─────────────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │     Worker      │
                                │  (Async Jobs)   │
                                └────────┬────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
            ┌───────▼──────┐    ┌───────▼──────┐    ┌────────▼────────┐
            │   OpenAI     │    │  Anthropic   │    │     MLflow      │
            │   Provider   │    │   Provider   │    │   (Tracking)    │
            └──────────────┘    └──────────────┘    └────────┬────────┘
                                                              │
                                                      ┌───────▼───────┐
                                                      │   PostgreSQL  │
                                                      │  (MLflow DB)  │
                                                      └───────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    n8n Workflow Engine                          │
│  Upload → Parse → AI Analyze → Store → MLflow → Notify         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Observability Stack (LGTM)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Grafana  │  │   Loki   │  │  Tempo   │  │  Mimir   │       │
│  │ (UI)     │  │ (Logs)   │  │ (Traces) │  │(Metrics) │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       └─────────────┴─────────────┴─────────────┘              │
│                         ▲                                       │
│                         │                                       │
│              ┌──────────▼──────────┐                            │
│              │   Grafana Alloy    │                            │
│              │   (Collector)      │                            │
│              └──────────┬──────────┘                            │
│                         │                                       │
│       ┌─────────────────┼─────────────────┐                   │
│       │                  │                 │                   │
│  ┌────▼────┐      ┌──────▼──────┐   ┌──────▼──────┐           │
│  │ Backend │      │   Worker    │   │  Prometheus │           │
│  │ Metrics │      │   Metrics   │   │  (Scrape)   │           │
│  │ Traces  │      │   Traces    │   └─────────────┘           │
│  │ Logs    │      │   Logs      │                             │
│  └─────────┘      └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React/Vite)
- **Purpose**: User interface for CV upload and analysis
- **Features**:
  - File upload (PDF/DOCX/TXT)
  - Parsing preview
  - Analysis trigger
  - Results display with scores
  - Job history and status timeline
  - OIDC-ready authentication (JWT sessions)

### Backend (REST API)
- **Purpose**: API gateway and request handler
- **Endpoints**:
  - `POST /api/v1/cv/upload` - Upload CV, returns `cv_id`
  - `POST /api/v1/cv/{cv_id}/analyze` - Trigger analysis, returns `job_id`
  - `GET /api/v1/jobs/{job_id}` - Job status and timeline
  - `GET /api/v1/cv/{cv_id}/report` - Final report and scores
- **Responsibilities**:
  - File validation (type, size)
  - Virus scan hook (placeholder)
  - Store files in MinIO
  - Enqueue jobs to Redis queue
  - Health endpoints (`/health`, `/ready`)
  - Prometheus metrics (`/metrics`)
  - OpenTelemetry tracing

### Worker Service
- **Purpose**: Async CV analysis processing
- **Responsibilities**:
  - Consume jobs from Redis queue
  - Parse CV (text extraction, normalization)
  - Call AI providers (OpenAI, Anthropic)
  - Generate structured analysis (JSON + Markdown)
  - Trigger n8n workflow
  - Log experiments to MLflow
  - Update job status
  - Metrics, tracing, structured logging

### AI Providers
- **Interface**: Pluggable provider abstraction
- **Implementations**:
  - OpenAI (GPT-4)
  - Anthropic (Claude)
- **Features**:
  - Prompt templates (versioned)
  - Request/response logging (redacted)
  - Token usage tracking
  - Latency metrics

### MLflow
- **Purpose**: Experiment tracking and model registry
- **Tracks**:
  - Model/provider used
  - Prompt version
  - Token usage
  - Latency
  - Score metrics
  - Evaluation metrics
- **Storage**: PostgreSQL backend

### n8n
- **Purpose**: Workflow orchestration
- **Workflow**:
  1. Upload received
  2. Parse CV
  3. AI analyze
  4. Store report
  5. Log to MLflow
  6. Notify (webhook stub)
  7. Update job status
- **Integration**: Webhook triggers from backend/worker

### Observability Stack

#### Grafana Alloy
- **Purpose**: Unified metrics, logs, and traces collector
- **Collects from**:
  - Backend (metrics, traces, logs)
  - Worker (metrics, traces, logs)
  - Prometheus (scrapes)
- **Sends to**:
  - Loki (logs)
  - Tempo (traces)
  - Mimir (metrics)

#### LGTM Stack
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation
- **Tempo**: Distributed tracing
- **Mimir**: Metrics storage and querying

#### Prometheus
- **Purpose**: Metrics scraping and short-term storage
- **Scrapes**: Backend, Worker, Alloy
- **Metrics**: RED (Rate, Errors, Duration), queue depth

## Data Flow

### CV Analysis Flow

1. **Upload**:
   - User uploads CV → Frontend
   - Frontend → Backend `/api/v1/cv/upload`
   - Backend validates → Stores in MinIO → Returns `cv_id`

2. **Analysis Trigger**:
   - Frontend → Backend `/api/v1/cv/{cv_id}/analyze`
   - Backend enqueues job to Redis → Returns `job_id`
   - Backend triggers n8n webhook

3. **Processing**:
   - Worker consumes job from Redis
   - Worker fetches CV from MinIO
   - Worker parses CV (text extraction, normalization)
   - Worker calls AI provider (with prompt template)
   - Worker generates analysis (JSON + Markdown)
   - Worker stores report in MinIO/PostgreSQL
   - Worker logs experiment to MLflow
   - Worker updates job status
   - Worker triggers n8n workflow completion

4. **Results**:
   - Frontend polls `/api/v1/jobs/{job_id}` for status
   - Frontend fetches `/api/v1/cv/{cv_id}/report` when complete
   - Frontend displays results with timeline

## Security Boundaries

### Network Policies
- **Default**: Deny all ingress/egress
- **Frontend**: Allow ingress from Ingress, egress to Backend
- **Backend**: Allow ingress from Frontend/Ingress, egress to MinIO/Redis/PostgreSQL/n8n
- **Worker**: Allow ingress from Redis, egress to MinIO/PostgreSQL/AI providers/n8n/MLflow
- **Observability**: Allow ingress from Alloy, egress to Loki/Tempo/Mimir

### RBAC
- ServiceAccounts for each component
- Minimal permissions (principle of least privilege)
- Secrets access via external-secrets or SOPS

### Secrets Management
- **Choice**: External Secrets Operator (ESO)
- AI provider keys stored in Kubernetes Secrets
- ESO syncs from external secret store (or local secrets for dev)

## Kubernetes Resources

### Namespaces
- `cv-analyzer` - Application components
- `observability` - LGTM stack, Alloy, Prometheus
- `mlflow` - MLflow tracking server
- `n8n` - n8n workflow engine
- `flux-system` - FluxCD controllers

### Resource Management
- Resource requests and limits for all pods
- PodSecurity admission policies (restricted)
- HorizontalPodAutoscaler for scalable components

## GitOps Structure

```
/clusters/dev
  ├── flux-system/          # Flux bootstrap
  ├── infrastructure/        # Base infrastructure (ingress, cert-manager, etc.)
  ├── apps/                 # Application components
  │   ├── frontend/
  │   ├── backend/
  │   ├── worker/
  │   ├── mlflow/
  │   └── n8n/
  └── observability/        # Observability stack
```

## Technology Choices

- **Frontend**: React 18, Vite, TypeScript, React Query
- **Backend**: Python (FastAPI) or Go (Gin) - **Choice: Python FastAPI**
- **Worker**: Same as backend (Python FastAPI with async workers)
- **Queue**: Redis with RQ (Redis Queue) or Celery
- **Storage**: MinIO (S3-compatible), PostgreSQL
- **AI Providers**: OpenAI, Anthropic
- **Orchestration**: n8n
- **Experiment Tracking**: MLflow
- **Observability**: Grafana LGTM + Alloy + Prometheus
- **GitOps**: FluxCD v2
- **Secrets**: External Secrets Operator
- **Ingress**: nginx-ingress
- **Certificates**: cert-manager (stub for dev)
