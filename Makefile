.PHONY: help minikube-up minikube-down flux-install flux-bootstrap flux-bootstrap-github up down test lint load-test clean

help:
	@echo "Available targets:"
	@echo "  minikube-up          - Create minikube cluster"
	@echo "  minikube-down        - Delete minikube cluster"
	@echo "  flux-install         - Install Flux CLI and controllers"
	@echo "  flux-bootstrap       - Bootstrap Flux from local git"
	@echo "  flux-bootstrap-github - Bootstrap Flux from GitHub"
	@echo "  up                   - Start local development (docker-compose)"
	@echo "  down                 - Stop local development"
	@echo "  test                 - Run all tests"
	@echo "  lint                 - Lint all code"
	@echo "  load-test            - Run load tests"
	@echo "  clean                - Clean build artifacts"

# Minikube
minikube-up:
	@echo "Creating minikube cluster..."
	minikube start --cpus=4 --memory=8192 --disk-size=20g
	minikube addons enable ingress
	minikube addons enable metrics-server
	@echo "Minikube cluster ready!"

minikube-down:
	minikube delete

# Flux
flux-install:
	@echo "Installing Flux CLI..."
	@which flux || (echo "Flux CLI not found. Install from https://fluxcd.io/docs/installation/" && exit 1)
	@echo "Installing Flux controllers..."
	flux install

flux-bootstrap:
	@echo "Bootstrapping Flux from local git..."
	flux bootstrap git \
		--url=file://$(PWD) \
		--branch=main \
		--path=clusters/dev/flux-system

flux-bootstrap-github:
	@echo "Bootstrapping Flux from GitHub..."
	@read -p "GitHub repo URL (e.g., https://github.com/user/repo): " repo_url; \
	flux bootstrap github \
		--owner=$$(echo $$repo_url | cut -d'/' -f4) \
		--repository=$$(echo $$repo_url | cut -d'/' -f5 | cut -d'.' -f1) \
		--branch=main \
		--path=clusters/dev/flux-system

# Local Development
up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8080"
	@echo "Grafana: http://localhost:3001"
	@echo "MLflow: http://localhost:5000"
	@echo "n8n: http://localhost:5678"

down:
	docker-compose down

# Testing
test:
	@echo "Running backend tests..."
	cd apps/backend && python -m pytest tests/ -v
	@echo "Running worker tests..."
	cd apps/worker && python -m pytest tests/ -v
	@echo "Running frontend tests..."
	cd apps/frontend && npm test

lint:
	@echo "Linting backend..."
	cd apps/backend && ruff check . && black --check .
	@echo "Linting frontend..."
	cd apps/frontend && npm run lint

load-test:
	@echo "Running load tests..."
	cd scripts && python load_test.py

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -r {} + 2>/dev/null || true
