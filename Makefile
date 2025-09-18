# ============================================================================
# MAKEFILE FOR QUALITY SYSTEM v2.0 DEVELOPMENT
# Simplifies common development tasks and ensures consistency
# ============================================================================

.PHONY: help setup dev test test-unit test-integration test-performance \
        test-security lint format type-check security-scan build deploy \
        clean logs monitoring backup restore

# Default target
help: ## Show this help message
	@echo "Quality System v2.0 - Development Commands"
	@echo "==========================================="
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

setup: ## Set up development environment
	@echo "🚀 Setting up development environment..."
	pip install -r requirements/development.txt
	pre-commit install
	docker-compose -f docker-compose.dev.yml pull
	$(MAKE) setup-db
	@echo "✅ Development environment ready!"

setup-db: ## Initialize development database
	@echo "🗄️  Setting up development database..."
	docker-compose -f docker-compose.dev.yml up -d postgres redis elasticsearch
	sleep 10
	python scripts/setup_dev_database.py
	python scripts/load_test_data.py
	@echo "✅ Database setup complete!"

# ============================================================================
# DEVELOPMENT WORKFLOW
# ============================================================================

dev: ## Start development environment
	@echo "🔧 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up --build
	
dev-detached: ## Start development environment in background
	@echo "🔧 Starting development environment (detached)..."
	docker-compose -f docker-compose.dev.yml up -d --build
	@echo "✅ Development environment running in background"
	@echo "📊 Grafana: http://localhost:3000 (admin/dev_password)"
	@echo "🔍 Kibana: http://localhost:5601"
	@echo "🎯 API: http://localhost:8000"

logs: ## Show application logs
	docker-compose -f docker-compose.dev.yml logs -f quality-system

monitoring: ## Open monitoring dashboard
	@echo "📊 Opening monitoring dashboards..."
	@echo "Grafana: http://localhost:3000"
	@echo "Kibana: http://localhost:5601"
	@echo "Prometheus: http://localhost:9090"

# ============================================================================
# TESTING
# ============================================================================

test: ## Run all tests
	@echo "🧪 Running all tests..."
	$(MAKE) test-unit
	$(MAKE) test-integration
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security-scan
	@echo "✅ All tests passed!"

test-unit: ## Run unit tests
	@echo "🔬 Running unit tests..."
	pytest tests/unit/ -v --cov=backend/services --cov-report=html --cov-report=term-missing
	@echo "✅ Unit tests completed!"

test-integration: ## Run integration tests
	@echo "🔗 Running integration tests..."
	docker-compose -f docker-compose.dev.yml up -d postgres redis elasticsearch
	sleep 15
	pytest tests/integration/ -v --tb=short
	@echo "✅ Integration tests completed!"

test-performance: ## Run performance tests
	@echo "⚡ Running performance tests..."
	docker-compose -f docker-compose.dev.yml --profile testing run --rm k6
	@echo "✅ Performance tests completed!"

test-security: ## Run security tests
	@echo "🛡️  Running security tests..."
	pytest tests/security/ -v --tb=short
	bandit -r backend/ -f json -o reports/security_report.json
	safety check --json --output reports/safety_report.json
	@echo "✅ Security tests completed!"

test-load: ## Run load tests against development environment
	@echo "🚛 Running load tests..."
	docker-compose -f docker-compose.dev.yml up -d quality-system
	sleep 30
	k6 run tests/load/stress_test.js --out json=reports/load_test_results.json
	@echo "✅ Load tests completed!"

# ============================================================================
# CODE QUALITY
# ============================================================================

lint: ## Run linting
	@echo "🔍 Running linters..."
	flake8 backend/ --config=.flake8
	black --check backend/
	isort --check-only backend/
	@echo "✅ Linting completed!"

format: ## Format code
	@echo "✨ Formatting code..."
	black backend/
	isort backend/
	@echo "✅ Code formatted!"

type-check: ## Run type checking
	@echo "🔤 Running type checks..."
	mypy backend/ --config-file=mypy.ini
	@echo "✅ Type checking completed!"

security-scan: ## Run security scans
	@echo "🛡️  Running security scans..."
	bandit -r backend/ -ll
	safety check
	semgrep --config=auto backend/
	@echo "✅ Security scanning completed!"

# ============================================================================
# BUILD AND DEPLOYMENT
# ============================================================================

build: ## Build production image
	@echo "🏗️  Building production image..."
	docker build -f Dockerfile.prod -t quality-system:latest .
	@echo "✅ Production image built!"

build-dev: ## Build development image
	@echo "🏗️  Building development image..."
	docker build -f Dockerfile.dev -t quality-system:dev .
	@echo "✅ Development image built!"

deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	$(MAKE) build
	docker tag quality-system:latest quality-system:staging
	# Add your staging deployment commands here
	@echo "✅ Deployed to staging!"

deploy-prod: ## Deploy to production
	@echo "🚀 Deploying to production..."
	@read -p "Are you sure you want to deploy to production? (y/N): " confirm && [ "$$confirm" = "y" ]
	$(MAKE) build
	$(MAKE) test
	docker tag quality-system:latest quality-system:prod
	# Add your production deployment commands here
	@echo "✅ Deployed to production!"

# ============================================================================
# MAINTENANCE
# ============================================================================

clean: ## Clean up development environment
	@echo "🧹 Cleaning up..."
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f
	docker volume prune -f
	@echo "✅ Cleanup completed!"

clean-data: ## Clean up data volumes (WARNING: Destructive!)
	@echo "🗑️  Cleaning up data volumes..."
	@read -p "This will delete ALL data. Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose -f docker-compose.dev.yml down -v
	docker volume rm $(docker volume ls -q --filter name=quality)
	@echo "✅ Data volumes cleaned!"

backup: ## Backup development data
	@echo "💾 Backing up development data..."
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	docker-compose -f docker-compose.dev.yml exec postgres pg_dump -U dev_user quality_dev > backups/$(shell date +%Y%m%d_%H%M%S)/postgres.sql
	docker-compose -f docker-compose.dev.yml exec redis redis-cli --rdb backups/$(shell date +%Y%m%d_%H%M%S)/redis.rdb
	@echo "✅ Backup completed!"

restore: ## Restore development data from backup
	@echo "📥 Restoring development data..."
	@read -p "Enter backup directory name: " backup_dir && \
	docker-compose -f docker-compose.dev.yml exec -T postgres psql -U dev_user -d quality_dev < backups/$$backup_dir/postgres.sql
	@echo "✅ Restore completed!"

# ============================================================================
# DEBUGGING AND TROUBLESHOOTING
# ============================================================================

debug-db: ## Connect to development database
	@echo "🗄️  Connecting to development database..."
	docker-compose -f docker-compose.dev.yml exec postgres psql -U dev_user -d quality_dev

debug-redis: ## Connect to Redis CLI
	@echo "🔴 Connecting to Redis..."
	docker-compose -f docker-compose.dev.yml exec redis redis-cli

debug-logs: ## Show detailed logs for debugging
	@echo "📋 Showing detailed logs..."
	docker-compose -f docker-compose.dev.yml logs --tail=100 -f

debug-shell: ## Get shell access to main application container
	@echo "🐚 Opening shell in application container..."
	docker-compose -f docker-compose.dev.yml exec quality-system /bin/bash

debug-metrics: ## Show current system metrics
	@echo "📊 Showing current metrics..."
	curl -s http://localhost:8000/metrics | head -20

debug-health: ## Check health of all services
	@echo "💚 Checking service health..."
	@echo "Quality System API:"
	@curl -s http://localhost:8000/health || echo "❌ API not responding"
	@echo "\nPostgreSQL:"
	@docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U dev_user || echo "❌ PostgreSQL not ready"
	@echo "\nRedis:"
	@docker-compose -f docker-compose.dev.yml exec redis redis-cli ping || echo "❌ Redis not responding"
	@echo "\nElasticsearch:"
	@curl -s http://localhost:9200/_cluster/health || echo "❌ Elasticsearch not responding"

# ============================================================================
# DOCUMENTATION
# ============================================================================

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	sphinx-build -b html docs/ docs/_build/html
	@echo "✅ Documentation generated at docs/_build/html/index.html"

docs-serve: ## Serve documentation locally
	@echo "📖 Serving documentation..."
	cd docs/_build/html && python -m http.server 8080

api-docs: ## Generate API documentation
	@echo "📋 Generating API documentation..."
	python scripts/generate_api_docs.py
	@echo "✅ API documentation generated!"

# ============================================================================
# UTILITIES
# ============================================================================

install-deps: ## Install/update dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements/development.txt
	npm install  # For frontend dependencies if needed
	@echo "✅ Dependencies installed!"

update-deps: ## Update dependencies to latest versions
	@echo "🔄 Updating dependencies..."
	pip-compile requirements/base.in --upgrade
	pip-compile requirements/development.in --upgrade
	pip-compile requirements/production.in --upgrade
	$(MAKE) install-deps
	@echo "✅ Dependencies updated!"

check-security-updates: ## Check for security updates in dependencies
	@echo "🔒 Checking for security updates..."
	safety check
	pip-audit
	@echo "✅ Security check completed!"

generate-config: ## Generate configuration files
	@echo "⚙️  Generating configuration files..."
	python scripts/generate_configs.py
	@echo "✅ Configuration files generated!"

# ============================================================================
# CI/CD SIMULATION
# ============================================================================

ci-pipeline: ## Simulate CI/CD pipeline locally
	@echo "🔄 Running CI/CD pipeline simulation..."
	$(MAKE) clean
	$(MAKE) setup
	$(MAKE) build-dev
	$(MAKE) test-unit
	$(MAKE) test-integration
	$(MAKE) test-security
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test-performance
	$(MAKE) build
	@echo "✅ CI/CD pipeline simulation completed successfully!"

pre-commit-check: ## Run all pre-commit checks
	@echo "✋ Running pre-commit checks..."
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test-unit
	@echo "✅ Pre-commit checks passed!"