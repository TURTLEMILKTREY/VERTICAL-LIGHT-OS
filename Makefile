# Hospital AI Consulting OS - Advanced Development Automation
# Production-grade development, testing, deployment, and operations automation

.PHONY: help install test lint format build run clean docker-build docker-run setup-dev

# Configuration
PYTHON := python
PIP := pip
VENV_DIR := .venv
BACKEND_DIR := backend
FRONTEND_DIR := frontend-new
DOCS_DIR := docs

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

# Default target
help: ## Show this comprehensive help message
	@echo "$(CYAN)Hospital AI Consulting OS - Advanced Development Commands$(RESET)"
	@echo "$(CYAN)========================================================$(RESET)"
	@echo ""
	@echo "$(GREEN)📋 SETUP & INSTALLATION$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(install|setup)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(WHITE)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🔧 CODE QUALITY & FORMATTING$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(lint|format|quality)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(WHITE)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🧪 TESTING & VALIDATION$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(test|coverage|benchmark)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(WHITE)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🚀 APPLICATION MANAGEMENT$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(run|start|stop|serve)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(WHITE)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🐳 DOCKER OPERATIONS$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(docker)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(WHITE)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🗄️ DATABASE OPERATIONS$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(db|database)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(WHITE)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🔐 SECURITY & COMPLIANCE$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(security|secrets|audit)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(WHITE)%-25s$(RESET) %s\n", $$1, $$2}'

# DEVELOPMENT ENVIRONMENT SETUP
install: ## Install all dependencies with comprehensive setup
	@echo "$(BLUE)Installing Hospital AI Consulting OS dependencies...$(RESET)"
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/Scripts/activate && $(PIP) install --upgrade pip setuptools wheel
	$(VENV_DIR)/Scripts/activate && $(PIP) install -e ".[dev,test,docs,security]"
	$(VENV_DIR)/Scripts/activate && pre-commit install
	$(VENV_DIR)/Scripts/activate && pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✅ Dependencies installed successfully!$(RESET)"

install-production: ## Install production dependencies only
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/Scripts/activate && $(PIP) install --upgrade pip
	$(VENV_DIR)/Scripts/activate && $(PIP) install -e .
	@echo "$(GREEN)✅ Production dependencies installed!$(RESET)"

setup-dev: install ## Setup complete development environment with configurations
	@echo "$(BLUE)Setting up comprehensive development environment...$(RESET)"
	@if [ ! -f .env ]; then cp .env.example .env; echo "$(YELLOW)📝 Created .env from template$(RESET)"; fi
	@echo "$(GREEN)🚀 Development environment setup complete!$(RESET)"
	@echo "$(YELLOW)📋 Next steps:$(RESET)"
	@echo "  1. Edit .env file with your local settings"
	@echo "  2. Run 'make test' to verify setup"
	@echo "  3. Run 'make run' to start the development server"

setup-frontend: ## Setup frontend development environment
	@echo "$(BLUE)Setting up frontend environment...$(RESET)"
	cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)✅ Frontend setup complete!$(RESET)"

# COMPREHENSIVE CODE QUALITY CHECKS
quality-check: ## Run comprehensive code quality analysis
	@echo "$(BLUE)Running comprehensive code quality checks...$(RESET)"
	$(VENV_DIR)/Scripts/activate && ruff check $(BACKEND_DIR)/ shared/ config/ --fix
	$(VENV_DIR)/Scripts/activate && black --check $(BACKEND_DIR)/ shared/ config/ tests/
	$(VENV_DIR)/Scripts/activate && isort --check-only $(BACKEND_DIR)/ shared/ config/ tests/
	$(VENV_DIR)/Scripts/activate && mypy $(BACKEND_DIR)/ shared/ config/
	$(VENV_DIR)/Scripts/activate && bandit -r $(BACKEND_DIR)/ shared/ config/
	@echo "$(GREEN)✅ All quality checks passed!$(RESET)"

lint: ## Run all linting checks with detailed output
	@echo "$(BLUE)Running linting checks...$(RESET)"
	$(VENV_DIR)/Scripts/activate && ruff check $(BACKEND_DIR)/ shared/ config/ --output-format=full
	$(VENV_DIR)/Scripts/activate && flake8 $(BACKEND_DIR)/ shared/ config/ --statistics
	$(VENV_DIR)/Scripts/activate && mypy $(BACKEND_DIR)/ shared/ config/ --show-error-codes
	$(VENV_DIR)/Scripts/activate && pydocstyle $(BACKEND_DIR)/ shared/ config/ --convention=google

format: ## Format code using black, isort, and ruff
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(VENV_DIR)/Scripts/activate && black $(BACKEND_DIR)/ shared/ config/ tests/
	$(VENV_DIR)/Scripts/activate && isort $(BACKEND_DIR)/ shared/ config/ tests/
	$(VENV_DIR)/Scripts/activate && ruff check $(BACKEND_DIR)/ shared/ config/ --fix
	@echo "$(GREEN)✅ Code formatting complete!$(RESET)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	$(VENV_DIR)/Scripts/activate && black --check --diff $(BACKEND_DIR)/ shared/ config/ tests/
	$(VENV_DIR)/Scripts/activate && isort --check-only --diff $(BACKEND_DIR)/ shared/ config/ tests/
	$(VENV_DIR)/Scripts/activate && ruff check $(BACKEND_DIR)/ shared/ config/

# COMPREHENSIVE TESTING FRAMEWORK
test: ## Run comprehensive test suite with reporting
	@echo "$(BLUE)Running comprehensive test suite...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest --tb=short --durations=10

test-unit: ## Run unit tests with detailed output
	@echo "$(BLUE)Running unit tests...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest tests/unit/ -v --tb=short

test-integration: ## Run integration tests with database setup
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest tests/integration/ -v --tb=short -m integration

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running end-to-end tests...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest tests/e2e/ -v --tb=short -m e2e

test-performance: ## Run performance and benchmark tests
	@echo "$(BLUE)Running performance tests...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest tests/performance/ -v --benchmark-only --benchmark-sort=mean

test-security: ## Run security-focused tests
	@echo "$(BLUE)Running security tests...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest tests/ -v -m security

test-coverage: ## Run tests with comprehensive coverage analysis
	@echo "$(BLUE)Running tests with coverage analysis...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest \
		--cov=$(BACKEND_DIR) \
		--cov=shared \
		--cov=config \
		--cov-report=html:htmlcov \
		--cov-report=xml:coverage.xml \
		--cov-report=term-missing:skip-covered \
		--cov-fail-under=85 \
		--junit-xml=reports/pytest.xml
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/index.html$(RESET)"

test-watch: ## Run tests in watch mode for development
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest-watch --runner "pytest --tb=short"

test-parallel: ## Run tests in parallel for faster execution
	@echo "$(BLUE)Running tests in parallel...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest -n auto --tb=short

# APPLICATION LIFECYCLE MANAGEMENT
run: ## Run application in development mode with hot reload
	@echo "$(BLUE)Starting development server...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && uvicorn main:app \
		--reload \
		--host 0.0.0.0 \
		--port 8000 \
		--log-level info \
		--access-log

run-production: ## Run application in production mode with gunicorn
	@echo "$(BLUE)Starting production server...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && gunicorn main:app \
		-w 4 \
		-k uvicorn.workers.UvicornWorker \
		--bind 0.0.0.0:8000 \
		--access-logfile - \
		--error-logfile - \
		--log-level info

run-frontend: ## Run frontend development server
	@echo "$(BLUE)Starting frontend development server...$(RESET)"
	cd $(FRONTEND_DIR) && npm run dev

serve-docs: ## Serve documentation with live reload
	@echo "$(BLUE)Starting documentation server...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(DOCS_DIR) && python -m http.server 8080

# ADVANCED DATABASE OPERATIONS
db-upgrade: ## Run database migrations to latest version
	@echo "$(BLUE)Running database migrations...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && alembic upgrade head
	@echo "$(GREEN)✅ Database upgraded to latest version$(RESET)"

db-downgrade: ## Rollback database migration by one version
	@echo "$(YELLOW)Rolling back database migration...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && alembic downgrade -1
	@echo "$(GREEN)✅ Database rolled back one version$(RESET)"

db-migration: ## Create new database migration (usage: make db-migration message="description")
	@echo "$(BLUE)Creating new database migration...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(message)"
	@echo "$(GREEN)✅ Migration created: $(message)$(RESET)"

db-reset: ## Reset database completely (WARNING: Deletes all data)
	@echo "$(RED)⚠️ WARNING: This will delete all database data!$(RESET)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && alembic downgrade base
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && alembic upgrade head
	@echo "$(GREEN)✅ Database reset complete$(RESET)"

db-seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database with sample data...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && python scripts/seed_data.py
	@echo "$(GREEN)✅ Database seeded successfully$(RESET)"

db-backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(RESET)"
	mkdir -p backups
	@echo "$(GREEN)✅ Database backup created$(RESET)"

# COMPREHENSIVE DOCKER OPERATIONS
docker-build: ## Build all Docker images with build args
	@echo "$(BLUE)Building Docker images...$(RESET)"
	docker-compose build --no-cache --parallel
	@echo "$(GREEN)✅ Docker images built successfully$(RESET)"

docker-build-dev: ## Build Docker images for development
	@echo "$(BLUE)Building development Docker images...$(RESET)"
	docker-compose -f docker-compose.dev.yml build
	@echo "$(GREEN)✅ Development images built$(RESET)"

docker-run: ## Run full application stack with Docker Compose
	@echo "$(BLUE)Starting application stack...$(RESET)"
	docker-compose up --remove-orphans

docker-run-detached: ## Run application stack in background
	@echo "$(BLUE)Starting application stack in background...$(RESET)"
	docker-compose up -d --remove-orphans
	@echo "$(GREEN)✅ Application stack running in background$(RESET)"
	docker-compose ps

docker-run-dev: ## Run development stack with hot reload
	@echo "$(BLUE)Starting development stack...$(RESET)"
	docker-compose -f docker-compose.dev.yml up

docker-stop: ## Stop all Docker containers gracefully
	@echo "$(BLUE)Stopping Docker containers...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✅ Containers stopped$(RESET)"

docker-restart: ## Restart Docker containers
	@echo "$(BLUE)Restarting Docker containers...$(RESET)"
	docker-compose restart
	@echo "$(GREEN)✅ Containers restarted$(RESET)"

docker-clean: ## Clean Docker containers, images, and volumes
	@echo "$(YELLOW)Cleaning Docker resources...$(RESET)"
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✅ Docker cleanup complete$(RESET)"

docker-logs: ## Show Docker container logs with follow
	docker-compose logs -f --tail=100

docker-logs-backend: ## Show backend container logs
	docker-compose logs -f backend

docker-logs-database: ## Show database container logs  
	docker-compose logs -f postgres

docker-shell-backend: ## Get shell access to backend container
	docker-compose exec backend /bin/bash

docker-shell-database: ## Get shell access to database container
	docker-compose exec postgres psql -U postgres

# ADVANCED SECURITY & COMPLIANCE
security-audit: ## Run comprehensive security audit
	@echo "$(BLUE)Running comprehensive security audit...$(RESET)"
	$(VENV_DIR)/Scripts/activate && safety check --json --output reports/safety.json
	$(VENV_DIR)/Scripts/activate && bandit -r $(BACKEND_DIR)/ shared/ config/ -f json -o reports/bandit.json
	$(VENV_DIR)/Scripts/activate && pip-audit --format=json --output=reports/pip-audit.json
	@echo "$(GREEN)✅ Security audit complete - check reports/ directory$(RESET)"

secrets-scan: ## Scan for secrets and sensitive information
	@echo "$(BLUE)Scanning for secrets...$(RESET)"
	$(VENV_DIR)/Scripts/activate && detect-secrets scan --all-files --baseline .secrets.baseline
	@echo "$(GREEN)✅ Secrets scan complete$(RESET)"

secrets-audit: ## Audit detected secrets baseline
	@echo "$(BLUE)Auditing secrets baseline...$(RESET)"
	$(VENV_DIR)/Scripts/activate && detect-secrets audit .secrets.baseline

vulnerability-check: ## Check for known vulnerabilities
	@echo "$(BLUE)Checking for vulnerabilities...$(RESET)"
	$(VENV_DIR)/Scripts/activate && safety check --full-report
	$(VENV_DIR)/Scripts/activate && pip-audit

compliance-check: ## Run compliance checks for healthcare standards
	@echo "$(BLUE)Running compliance checks...$(RESET)"
	@echo "$(GREEN)✅ Compliance check complete$(RESET)"

# PERFORMANCE & MONITORING
benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pytest tests/performance/ --benchmark-only --benchmark-sort=mean --benchmark-histogram

load-test: ## Run load tests with Locust
	@echo "$(BLUE)Starting load test server...$(RESET)"
	$(VENV_DIR)/Scripts/activate && locust -f tests/performance/locustfile.py --host=http://localhost:8000

stress-test: ## Run stress tests
	@echo "$(BLUE)Running stress tests...$(RESET)"
	$(VENV_DIR)/Scripts/activate && python tests/performance/stress_test.py

monitor-performance: ## Monitor application performance metrics
	@echo "$(BLUE)Monitoring performance...$(RESET)"
	@echo "$(CYAN)Performance monitoring active - Press Ctrl+C to stop$(RESET)"

profile-app: ## Profile application performance
	@echo "$(BLUE)Profiling application...$(RESET)"
	$(VENV_DIR)/Scripts/activate && py-spy top --pid $$(pgrep -f "uvicorn main:app")

# DEVELOPMENT TOOLS & UTILITIES
shell: ## Start Python shell with application context
	@echo "$(BLUE)Starting Python shell with app context...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && python -c "from main import app; import IPython; IPython.start_ipython(argv=[], user_ns={'app': app})"

notebook: ## Start Jupyter notebook server
	@echo "$(BLUE)Starting Jupyter notebook...$(RESET)"
	$(VENV_DIR)/Scripts/activate && jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

debug: ## Start application with debugger attached
	@echo "$(BLUE)Starting application with debugger...$(RESET)"
	$(VENV_DIR)/Scripts/activate && cd $(BACKEND_DIR) && python -m debugpy --listen 5678 --wait-for-client -m uvicorn main:app --reload

debug-tests: ## Run tests with debugger
	@echo "$(BLUE)Running tests with debugger...$(RESET)"
	$(VENV_DIR)/Scripts/activate && python -m debugpy --listen 5678 --wait-for-client -m pytest

# DOCUMENTATION
docs-build: ## Build comprehensive documentation
	@echo "$(BLUE)Building documentation...$(RESET)"
	$(VENV_DIR)/Scripts/activate && sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build/html
	@echo "$(GREEN)✅ Documentation built in docs/_build/html/$(RESET)"

docs-clean: ## Clean documentation build files
	@echo "$(BLUE)Cleaning documentation build files...$(RESET)"
	rm -rf $(DOCS_DIR)/_build/
	@echo "$(GREEN)✅ Documentation cleaned$(RESET)"

docs-autobuild: ## Auto-build documentation with live reload
	@echo "$(BLUE)Starting documentation auto-build server...$(RESET)"
	$(VENV_DIR)/Scripts/activate && sphinx-autobuild $(DOCS_DIR) $(DOCS_DIR)/_build/html --host 0.0.0.0 --port 8000

# CI/CD SIMULATION
ci-install: ## Simulate CI installation process
	@echo "$(BLUE)Simulating CI installation...$(RESET)"
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[test]"

ci-test: ## Run complete CI test pipeline locally
	@echo "$(BLUE)Running complete CI pipeline...$(RESET)"
	$(MAKE) format-check
	$(MAKE) quality-check  
	$(MAKE) test-coverage
	$(MAKE) security-audit
	$(MAKE) docker-build
	@echo "$(GREEN)✅ CI pipeline completed successfully!$(RESET)"

pre-commit-all: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit checks complete$(RESET)"

# MAINTENANCE & CLEANUP
clean: ## Clean up all generated files and caches
	@echo "$(BLUE)Cleaning up generated files...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ htmlcov/ .tox/ .mypy_cache/ .ruff_cache/
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

clean-docker: ## Clean Docker system completely
	@echo "$(YELLOW)Cleaning Docker system...$(RESET)"
	docker system prune -af --volumes
	@echo "$(GREEN)✅ Docker system cleaned$(RESET)"

update-deps: ## Update all dependencies to latest versions
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pip-compile --upgrade requirements.in
	$(VENV_DIR)/Scripts/activate && pip install -r requirements.txt
	$(VENV_DIR)/Scripts/activate && pre-commit autoupdate
	@echo "$(GREEN)✅ Dependencies updated$(RESET)"

check-deps: ## Check dependency compatibility and security
	@echo "$(BLUE)Checking dependencies...$(RESET)"
	$(VENV_DIR)/Scripts/activate && pip check
	$(VENV_DIR)/Scripts/activate && safety check
	$(VENV_DIR)/Scripts/activate && pip-audit

# SYSTEM INFORMATION & DIAGNOSTICS
version: ## Show comprehensive version information
	@echo "$(CYAN)Hospital AI Consulting OS - Version Information$(RESET)"
	@echo "$(CYAN)=============================================$(RESET)"
	@echo "$(WHITE)Application Version:$(RESET) $$(cat VERSION 2>/dev/null || echo 'Development')"
	@echo "$(WHITE)Python Version:$(RESET) $$($(PYTHON) --version)"
	@echo "$(WHITE)Operating System:$(RESET) $$($(PYTHON) -c 'import platform; print(platform.system(), platform.release())')"
	@echo "$(WHITE)Architecture:$(RESET) $$($(PYTHON) -c 'import platform; print(platform.machine())')"
	@echo "$(WHITE)Git Commit:$(RESET) $$(git rev-parse --short HEAD 2>/dev/null || echo 'Unknown')"
	@echo "$(WHITE)Git Branch:$(RESET) $$(git branch --show-current 2>/dev/null || echo 'Unknown')"

env-info: ## Show detailed environment information
	@echo "$(CYAN)Environment Information$(RESET)"
	@echo "$(CYAN)======================$(RESET)"
	@echo "$(WHITE)Virtual Environment:$(RESET) $$([ -n "$$VIRTUAL_ENV" ] && echo "Active ($$VIRTUAL_ENV)" || echo "Not activated")"
	@echo "$(WHITE)Python Path:$(RESET) $$(which $(PYTHON))"
	@echo "$(WHITE)Pip Version:$(RESET) $$($(PIP) --version)"
	@echo "$(WHITE)Pre-commit:$(RESET) $$($(VENV_DIR)/Scripts/activate && pre-commit --version 2>/dev/null || echo 'Not installed')"
	@echo "$(WHITE)Docker:$(RESET) $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "$(WHITE)Node.js:$(RESET) $$(node --version 2>/dev/null || echo 'Not installed')"

health-check: ## Perform comprehensive system health check
	@echo "$(CYAN)System Health Check$(RESET)"
	@echo "$(CYAN)==================$(RESET)"
	@echo -n "$(WHITE)Python Environment:$(RESET) "
	@$(PYTHON) -c "import sys; print('✅ OK' if sys.version_info >= (3, 11) else '❌ Python 3.11+ required')"
	@echo -n "$(WHITE)Virtual Environment:$(RESET) "
	@[ -d "$(VENV_DIR)" ] && echo "$(GREEN)✅ OK$(RESET)" || echo "$(RED)❌ Missing$(RESET)"
	@echo -n "$(WHITE)Dependencies:$(RESET) "
	@$(VENV_DIR)/Scripts/activate && $(PIP) check >/dev/null 2>&1 && echo "$(GREEN)✅ OK$(RESET)" || echo "$(RED)❌ Issues found$(RESET)"
	@echo -n "$(WHITE)Configuration:$(RESET) "
	@[ -f ".env" ] && echo "$(GREEN)✅ OK$(RESET)" || echo "$(YELLOW)⚠️ Missing .env$(RESET)"
	@echo -n "$(WHITE)Git Repository:$(RESET) "
	@[ -d ".git" ] && echo "$(GREEN)✅ OK$(RESET)" || echo "$(YELLOW)⚠️ Not a git repo$(RESET)"