# ⚙️ Configuration System
## Enterprise-Grade Dynamic Configuration Management

This directory contains the complete configuration management system for Vertical Light OS, designed to eliminate hardcoded values and enable environment-specific deployments with enterprise-grade features.

---

## 📁 Directory Structure

```
config/
├── README.md                    # This file - configuration overview
├── base.json                    # Base configuration inherited by all environments
├── schema.json                  # JSON Schema for configuration validation
├── configuration_manager.py     # Configuration management system
└── environments/
    ├── development.json         # Development environment overrides
    ├── staging.json            # Staging environment overrides
    └── production.json         # Production environment overrides
```

---

## 🎯 Purpose & Goals

### **Eliminates Hardcoded Values**
This configuration system addresses **127 hardcoded values** identified in the system analysis, enabling:
- **Dynamic value management** without code changes
- **Environment-specific optimizations** for dev/staging/production
- **Real-time configuration updates** via hot-reload
- **Market-driven intelligence** through API integration

### **Enterprise Features**
- **🔒 Security**: Environment variable substitution, API key rotation, encryption support
- **📊 Monitoring**: APM integration, performance tracking, comprehensive logging
- **✅ Validation**: JSON Schema validation with business logic checks
- **🔄 Hot-Reload**: Zero-downtime configuration updates
- **🧵 Thread-Safe**: Concurrent access protection for production environments

---

## 🚀 Quick Start

### **1. Basic Usage**
```python
from config.configuration_manager import get_config, get_config_section

# Get individual configuration values
cache_ttl = get_config('cache.default_ttl', default=3600)
api_timeout = get_config('api_integration.timeout_seconds', default=30)

# Get entire configuration sections
cache_config = get_config_section('cache')
learning_config = get_config_section('learning_system')
```

### **2. Environment Setup**
```bash
# Development Environment
export ENVIRONMENT=development
python main.py

# Production Environment
export ENVIRONMENT=production
export REDIS_URL=redis://prod-cluster:6379/0
export GOOGLE_ADS_API_KEY=your_production_api_key
export DATABASE_URL=postgresql://user:pass@prod-db:5432/db
python main.py
```

### **3. Configuration Management**
```python
from config.configuration_manager import ConfigurationManager

# Initialize with hot-reload for development
config_manager = ConfigurationManager(
    environment="development",
    enable_hot_reload=True
)

# Validate configuration
validation_result = config_manager.validate_current_config()
if not validation_result.is_valid:
    print(f"Configuration errors: {validation_result.errors}")
```

---

## ⚙️ Configuration Sections

### **System Configuration**
Basic system identification, environment detection, and debugging settings.

### **Cache Configuration** 
Redis/memory caching with TTL management, memory limits, and performance optimization.

### **API Integration**
External API endpoints, authentication, rate limiting, retry logic, and health checking.

### **Dynamic Values**
Real-time value sources, update frequencies, validation rules, and fallback strategies.

### **Learning System**
Machine learning weights, pattern storage, adaptation parameters, and backup settings.

### **Monitoring & Security**
Logging levels, metrics collection, alerting thresholds, and security controls.

---

## 🔧 Environment-Specific Features

### **Development Environment**
- **Mock APIs** for offline development
- **Memory caching** for fast iteration
- **Debug logging** with console output
- **Hot-reload enabled** by default
- **Reduced security** for easy testing

### **Staging Environment**  
- **Production-like APIs** with staging credentials
- **Redis caching** with staging cluster
- **Monitoring enabled** with staging APM
- **Security features** enabled for testing
- **Performance tracking** for optimization

### **Production Environment**
- **Full API integration** with production credentials
- **Redis clustering** with high availability
- **Comprehensive monitoring** and alerting
- **Enterprise security** with encryption and auditing
- **Performance optimization** with aggressive caching

---

## 📊 Performance Characteristics

| Operation | Performance | Notes |
|-----------|-------------|-------|
| Initial Configuration Load | 50-100ms | One-time startup cost |
| Cached Value Access | <1ms | Thread-safe read operations |
| Hot-Reload Check | 5-10ms | File timestamp verification |
| Configuration Validation | 10-50ms | Schema and business logic |
| Memory Usage | 1-5MB | Complete configuration in memory |

---

## 🛡️ Security Features

### **Credential Management**
- **No secrets in config files** - All credentials via environment variables
- **Environment variable substitution** with `${VARIABLE_NAME}` syntax  
- **API key rotation** with configurable intervals
- **Default value support** with `${VARIABLE_NAME:default}` syntax

### **Production Security**
- **Request/response encryption** for API communications
- **IP whitelisting** with configurable allowed addresses
- **Comprehensive audit logging** for security compliance
- **Security headers** for web interface protection
- **Rate limiting per IP** to prevent abuse

---

## ✅ Validation System

### **JSON Schema Validation**
- **Type checking** for all configuration values
- **Range validation** for numeric values
- **Format validation** for URLs, IPs, and other structured data
- **Required field validation** to ensure completeness

### **Business Logic Validation**
- **Learning weight validation** - ensures weights sum to 1.0
- **Source weight consistency** - validates API source weights
- **Cache TTL relationships** - ensures logical TTL hierarchies
- **Performance threshold validation** - prevents invalid performance settings

---

## 🔗 Integration Points

### **With Production Roadmap**
- Foundation for Day 2-21 implementation phases
- Enables systematic hardcoded value elimination
- Supports API integration and dynamic data sources
- Provides monitoring and error handling framework

### **With Analysis Results**  
- Directly addresses all 127 identified hardcoded values
- Maps each value to appropriate configuration section
- Provides validation and fallback strategies
- Enables business impact-based prioritization

### **With Development Workflow**
- Environment-specific settings for different deployment stages
- Hot-reload capabilities for rapid development cycles
- Comprehensive error handling and debugging support
- Professional documentation and usage examples

---

## 📈 Migration Path

### **From Hardcoded Values**
1. **Identify** hardcoded values in your code
2. **Add** corresponding configuration entries
3. **Replace** hardcoded values with `get_config()` calls
4. **Test** configuration loading across environments
5. **Validate** business logic with dynamic values

### **Example Migration**
```python
# Before (hardcoded)
BUDGET_THRESHOLDS = {
    'micro': 500,
    'small': 5000,
    'medium': 50000
}

# After (dynamic)
from config.configuration_manager import get_config_section

def get_budget_thresholds():
    return get_config_section('dynamic_values.budget_classification.emergency_fallback_values')
```

---

## 🆘 Troubleshooting

### **Common Issues**
1. **Configuration file not found** - Check environment variable and file paths
2. **Schema validation failed** - Verify all required fields are present
3. **Environment variable not found** - Set required environment variables
4. **Hot-reload not working** - Enable with `CONFIG_HOT_RELOAD=true`

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug configuration loading
config_manager = ConfigurationManager()
```

---

## 📚 Additional Documentation

For comprehensive documentation and usage examples:

- **📋 [Complete Configuration Guide](../docs/configuration/configuration-system.md)**
- **🏗️ [Architecture Design](../docs/configuration/architecture-design.md)**  
- **📊 [System Analysis](../docs/analysis/)**
- **🚀 [Production Roadmap](../docs/production-readiness/)**

---

*Configuration System Version: 1.0.0*  
*Enterprise-grade configuration management for Vertical Light OS*
