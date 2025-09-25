# Contributing to Hospital AI Consulting OS

Welcome to the Hospital AI Consulting OS project! We appreciate your interest in contributing to this innovative healthcare technology platform.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Submission Process](#submission-process)
- [Review Process](#review-process)
- [Recognition](#recognition)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to team@verticallight.ai.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend development)
- Docker and Docker Compose
- Git version control
- VS Code or similar IDE

### First Time Setup

1. **Fork the Repository**
   ```bash
   # Fork the repo on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/VERTICAL-LIGHT-OS.git
   cd VERTICAL-LIGHT-OS
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies
   pip install -e ".[dev]"
   
   # Set up pre-commit hooks
   pre-commit install
   ```

3. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your local settings
   ```

4. **Run Tests**
   ```bash
   # Run all tests
   pytest
   
   # Run specific test categories
   pytest -m unit
   pytest -m integration
   ```

## Development Setup

### Backend Development

```bash
# Start backend development server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Start frontend development server
cd frontend-new
npm install
npm run dev
```

### Database Setup

```bash
# Start local database
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head
```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes** - Fix issues in existing functionality
- **Feature development** - Add new features or capabilities
- **Documentation** - Improve documentation and guides
- **Testing** - Add or improve test coverage
- **Performance** - Optimize performance and efficiency
- **Security** - Enhance security measures

### Finding Issues to Work On

1. **Good First Issues** - Look for issues tagged `good-first-issue`
2. **Help Wanted** - Issues tagged `help-wanted` need contributor assistance
3. **Bug Reports** - Issues tagged `bug` that need fixing
4. **Feature Requests** - Issues tagged `enhancement` for new features

### Creating Issues

Before creating a new issue:

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** provided in the repository
3. **Provide detailed information** including:
   - Clear description of the problem or enhancement
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Screenshots or logs (if applicable)

## Code Standards

### Python Code Standards

We follow strict coding standards:

```python
# Use type hints for all function parameters and returns
def process_hospital_data(
    hospital_id: str, 
    metrics: Dict[str, float]
) -> HospitalProfile:
    """
    Process hospital data and return hospital profile.
    
    Args:
        hospital_id: Unique identifier for hospital
        metrics: Dictionary of performance metrics
        
    Returns:
        Processed hospital profile instance
        
    Raises:
        ValueError: If hospital_id is invalid
        ValidationError: If metrics data is malformed
    """
    pass

# Use descriptive variable names
hospital_financial_metrics = calculate_financial_performance(revenue_data)

# Follow Google-style docstrings
def analyze_patient_flow(
    admission_data: List[PatientRecord],
    time_period: DateRange
) -> FlowAnalysis:
    """
    Analyze patient flow patterns for optimization opportunities.
    
    This function processes patient admission and discharge data to identify
    bottlenecks, peak times, and optimization opportunities in hospital
    patient flow management.
    
    Args:
        admission_data: List of patient admission records
        time_period: Date range for analysis
        
    Returns:
        Comprehensive flow analysis with recommendations
        
    Raises:
        InsufficientDataError: If not enough data for meaningful analysis
        
    Example:
        >>> records = get_patient_records('2024-01-01', '2024-01-31')
        >>> period = DateRange('2024-01-01', '2024-01-31')
        >>> analysis = analyze_patient_flow(records, period)
        >>> print(analysis.peak_hours)
        ['08:00-10:00', '14:00-16:00']
    """
    pass
```

### Code Quality Tools

All code must pass these quality checks:

- **Black** - Code formatting
- **isort** - Import sorting
- **Ruff** - Linting and additional checks
- **MyPy** - Type checking
- **Bandit** - Security analysis
- **pytest** - Test execution

### Configuration Files

The project uses standardized configuration:

- `pyproject.toml` - Main Python project configuration
- `.pre-commit-config.yaml` - Pre-commit hooks
- `tox.ini` - Multi-environment testing

## Testing Requirements

### Test Coverage

- **Minimum 85% code coverage** required
- **All new features** must include comprehensive tests
- **Bug fixes** must include regression tests

### Test Categories

```python
# Unit tests - Fast, isolated tests
@pytest.mark.unit
def test_hospital_schema_validation():
    """Test hospital data model validation."""
    pass

# Integration tests - Test component interactions
@pytest.mark.integration
def test_hms_connector_integration():
    """Test HMS connector with real API."""
    pass

# End-to-end tests - Complete user workflows
@pytest.mark.e2e
def test_complete_hospital_onboarding():
    """Test complete hospital setup workflow."""
    pass

# Performance tests - Verify performance requirements
@pytest.mark.performance
def test_large_dataset_processing():
    """Test performance with large hospital datasets."""
    pass
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_hospital_schemas.py
│   └── test_hms_connectors.py
├── integration/             # Integration tests
│   └── test_hospital_integration.py
├── e2e/                     # End-to-end tests
│   └── test_user_workflows.py
├── performance/             # Performance tests
│   └── test_performance.py
└── fixtures/                # Test data and fixtures
    └── sample_data.json
```

## Submission Process

### 1. Branch Strategy

```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b bugfix/issue-description

# For documentation
git checkout -b docs/documentation-update
```

### 2. Development Workflow

```bash
# Make your changes
# Add tests for new functionality
# Ensure all tests pass
pytest

# Run code quality checks
pre-commit run --all-files

# Commit with descriptive message
git add .
git commit -m "feat: add hospital performance analytics

- Implement performance metrics calculation
- Add benchmarking against industry standards  
- Include comprehensive test coverage
- Update API documentation

Closes #123"
```

### 3. Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Build process or auxiliary tool changes
- `perf:` - Performance improvements
- `ci:` - Continuous integration changes

**Examples:**
```bash
feat(analytics): add hospital performance benchmarking

fix(connector): resolve HMS connection timeout issue

docs(api): update authentication documentation

test(integration): add comprehensive HMS integration tests
```

### 4. Pull Request Process

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Use the provided PR template
   - Link related issues
   - Provide detailed description
   - Include screenshots/demos if applicable

3. **PR Requirements**
   - All tests must pass
   - Code coverage must meet requirements
   - Code review approval required
   - Documentation updated if needed

## Review Process

### Code Review Checklist

**Functionality:**
- [ ] Code solves the intended problem
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance impact is acceptable

**Code Quality:**
- [ ] Code follows project standards
- [ ] Functions are well-documented
- [ ] Variable names are descriptive
- [ ] Code is maintainable

**Testing:**
- [ ] Comprehensive test coverage
- [ ] Tests are well-written
- [ ] Edge cases are tested
- [ ] Integration tests pass

**Security:**
- [ ] No security vulnerabilities
- [ ] Input validation is proper
- [ ] Sensitive data is protected
- [ ] Authentication/authorization is correct

### Review Timeline

- **Initial review:** 1-2 business days
- **Follow-up reviews:** 24 hours for requested changes
- **Final approval:** After all requirements are met

## Development Best Practices

### Hospital Domain Knowledge

When contributing to hospital-related features:

1. **Understand Healthcare Context**
   - Research Indian healthcare system
   - Understand hospital operations
   - Consider regulatory requirements

2. **Data Privacy and Security**
   - Follow HIPAA-like principles
   - Implement proper data anonymization
   - Ensure secure data handling

3. **Performance Considerations**
   - Hospital systems must be highly available
   - Response times should be under 2 seconds
   - Consider offline capabilities

### AI/ML Development

For AI and machine learning components:

1. **Data Quality**
   - Implement data validation
   - Handle missing or corrupted data
   - Document data requirements

2. **Model Performance**
   - Include model evaluation metrics
   - Implement model versioning
   - Add monitoring for model drift

3. **Explainability**
   - Make AI decisions interpretable
   - Provide reasoning for recommendations
   - Enable audit trails

## Recognition

### Contributor Levels

- **First-time Contributors** - Listed in CONTRIBUTORS.md
- **Regular Contributors** - Featured in release notes
- **Core Contributors** - Added to README acknowledgments
- **Maintainers** - Given repository permissions

### Annual Recognition

- Top contributors featured on website
- Conference speaking opportunities
- Open source achievement certificates
- Potential hiring opportunities

## Resources

### Documentation
- [Project README](../README.md)
- [API Documentation](../api/)
- [Architecture Overview](../architecture/)
- [Deployment Guide](../deployment/)

### Communication
- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and ideas  
- **Email** - team@verticallight.ai for private matters

### Learning Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Hospital Management Systems Overview](https://www.who.int/publications/i/item/9789241511407)

## Getting Help

If you need help:

1. **Check existing documentation** in this repository
2. **Search closed issues** for similar problems
3. **Ask in GitHub Discussions** for general questions
4. **Create an issue** for specific bugs or feature requests
5. **Email us** at team@verticallight.ai for urgent matters

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).

---

Thank you for contributing to the Hospital AI Consulting OS! Your contributions help improve healthcare technology and make a meaningful impact on hospital operations across India.

For questions about contributing, please reach out to our team at team@verticallight.ai or create an issue in the repository.