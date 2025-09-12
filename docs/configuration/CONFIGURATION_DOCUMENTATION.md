# Configuration System Documentation and Examples

## 📚 **Complete Configuration Documentation for Production Deployment**

### **Overview**
This document provides comprehensive documentation for the dynamic AI configuration system, including schemas, inheritance patterns, validation rules, and practical examples for all environments.

---

## 🏗️ **Configuration Architecture**

### **Configuration Hierarchy**
```
Configuration System Architecture:
├── base.json (Core system defaults)
├── environments/
│   ├── development.json (Dev overrides)
│   ├── staging.json (Staging overrides)
│   └── production.json (Production overrides)
├── schemas/
│   ├── goal_parser_enhanced.json (Goal Parser validation)
│   └── campaign_generator_enhanced.json (Campaign Generator validation)
└── config_manager.py (Configuration management engine)
```

### **Inheritance Pattern**
```
Final Configuration = base.json + environment-specific.json
                     ↓
               Schema Validation
                     ↓
              Runtime Configuration
```

---

## 📋 **Configuration Schema Reference**

### **Goal Parser Configuration Schema**

#### **Required Sections:**
1. **`processing`** - Core processing parameters
2. **`intelligence`** - AI intelligence thresholds  
3. **`budget_thresholds`** - Dynamic budget calculation
4. **`performance_thresholds`** - Performance metrics

#### **Schema Structure:**
```json
{
  "processing": {
    "max_concurrent_requests": 10,
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "batch_size": 50,
    "max_text_length": 10000
  },
  "intelligence": {
    "semantic_threshold": 0.75,
    "confidence_threshold": 0.80,
    "learning_rate": 0.15,
    "decay_factor": 0.95,
    "pattern_matching_threshold": 0.70,
    "adaptation_threshold": 0.65
  },
  "budget_thresholds": {
    "base_ranges": {
      "micro": 500,
      "small": 5000,
      "medium": 50000,
      "large": 500000,
      "enterprise": 2000000
    },
    "industry_multipliers": {
      "technology": 1.5,
      "healthcare": 1.3,
      "finance": 1.4
    },
    "region_multipliers": {
      "north_america": 1.2,
      "europe": 1.1,
      "asia_pacific": 0.9
    }
  },
  "performance_thresholds": {
    "growth_rates": {
      "default": 5.0,
      "technology": 15.0,
      "healthcare": 8.0
    },
    "inflation_rates": {
      "default": 1.03,
      "north_america": 1.03,
      "europe": 1.025
    }
  }
}
```

### **Campaign Generator Configuration Schema**

#### **Required Sections:**
1. **`generation`** - Campaign generation parameters
2. **`channel_intelligence`** - Channel analysis configuration
3. **`channel_performance`** - Performance baselines
4. **`audience_channel_affinity`** - Audience targeting
5. **`seasonal_factors`** - Seasonal adjustments
6. **`optimization`** - Optimization settings
7. **`learning`** - Learning algorithms

#### **Schema Structure:**
```json
{
  "generation": {
    "max_campaigns_per_request": 5,
    "timeout_seconds": 120,
    "concurrent_generations": 3,
    "retry_attempts": 2
  },
  "channel_intelligence": {
    "analysis_depth": "standard",
    "confidence_threshold": 0.75,
    "industry_multipliers": {
      "default": {
        "social_media": 1.0,
        "search_advertising": 1.0,
        "email_marketing": 1.0
      }
    }
  },
  "channel_performance": {
    "search_advertising": {
      "ctr_range": [0.02, 0.08],
      "cpc_range": [1.5, 8.0],
      "conversion_rate_range": [0.02, 0.12]
    }
  },
  "audience_channel_affinity": {
    "age_groups": {
      "18_35": {
        "social_media": 0.90,
        "search_advertising": 0.75
      }
    }
  },
  "seasonal_factors": {
    "q1": 0.95,
    "q2": 1.05,
    "q3": 0.90,
    "q4": 1.15
  },
  "optimization": {
    "budget_allocation_strategy": "performance_weighted",
    "reserve_percentage": 0.15,
    "performance_weights": {
      "reach": 0.25,
      "engagement": 0.30,
      "conversion": 0.35,
      "cost_efficiency": 0.10
    }
  },
  "learning": {
    "learning_rate": 0.15,
    "decay_rate": 0.95
  }
}
```

---

## 🌍 **Environment-Specific Configuration**

### **Development Environment**
**Purpose**: Local development and testing  
**File**: `environments/development.json`

```json
{
  "processing": {
    "max_concurrent_requests": 5,
    "timeout_seconds": 60
  },
  "intelligence": {
    "learning_rate": 0.25,
    "confidence_threshold": 0.70
  },
  "api_integration": {
    "enabled": false,
    "mock_data": true,
    "debug_mode": true
  },
  "logging": {
    "level": "DEBUG",
    "detailed_performance": true
  },
  "caching": {
    "ttl_seconds": 300,
    "max_cache_size": 1000
  }
}
```

### **Staging Environment**
**Purpose**: Pre-production testing and validation  
**File**: `environments/staging.json`

```json
{
  "processing": {
    "max_concurrent_requests": 8,
    "timeout_seconds": 45
  },
  "intelligence": {
    "learning_rate": 0.20,
    "confidence_threshold": 0.75
  },
  "api_integration": {
    "enabled": true,
    "rate_limiting": true,
    "sandbox_mode": true
  },
  "logging": {
    "level": "INFO",
    "performance_monitoring": true
  },
  "caching": {
    "ttl_seconds": 1800,
    "max_cache_size": 5000
  }
}
```

### **Production Environment**
**Purpose**: Live production deployment  
**File**: `environments/production.json`

```json
{
  "processing": {
    "max_concurrent_requests": 15,
    "timeout_seconds": 30
  },
  "intelligence": {
    "learning_rate": 0.15,
    "confidence_threshold": 0.80
  },
  "api_integration": {
    "enabled": true,
    "rate_limiting": true,
    "circuit_breaker": true,
    "retry_attempts": 3
  },
  "logging": {
    "level": "ERROR",
    "structured": true,
    "security_audit": true
  },
  "caching": {
    "ttl_seconds": 3600,
    "max_cache_size": 20000,
    "distributed": true
  },
  "monitoring": {
    "health_checks": true,
    "performance_alerts": true,
    "sla_monitoring": true
  }
}
```

---

## 🔧 **Configuration Usage Examples**

### **Basic Configuration Access**
```python
from config.config_manager import get_config_manager

# Get configuration manager
config = get_config_manager()

# Access nested configuration values
timeout = config.get('processing.timeout_seconds', 30)
confidence = config.get('intelligence.confidence_threshold', 0.8)

# Environment-aware access
if config.environment == 'development':
    debug_mode = config.get('api_integration.debug_mode', False)
```

### **Dynamic Configuration in Goal Parser**
```python
class UltraDynamicGoalParser:
    def __init__(self):
        self.config_manager = get_config_manager()
        
    def parse_goal(self, goal_text):
        # Get dynamic thresholds
        confidence_threshold = self.config_manager.get(
            'intelligence.confidence_threshold', 0.8
        )
        semantic_threshold = self.config_manager.get(
            'intelligence.semantic_threshold', 0.75
        )
        
        # Use dynamic budget ranges
        budget_ranges = self.config_manager.get(
            'budget_thresholds.base_ranges', {}
        )
        
        # Apply industry multipliers
        industry_multipliers = self.config_manager.get(
            'budget_thresholds.industry_multipliers', {}
        )
```

### **Dynamic Configuration in Campaign Generator**
```python
class UltraDynamicCampaignGenerator:
    def __init__(self):
        self.config_manager = get_config_manager()
        
    def generate_campaign(self, goal_data):
        # Get dynamic generation settings
        max_campaigns = self.config_manager.get(
            'generation.max_campaigns_per_request', 5
        )
        timeout = self.config_manager.get(
            'generation.timeout_seconds', 120
        )
        
        # Use dynamic channel performance data
        channel_performance = self.config_manager.get(
            'channel_performance', {}
        )
        
        # Apply seasonal factors
        seasonal_factors = self.config_manager.get(
            'seasonal_factors', {}
        )
```

---

## 📊 **Configuration Validation Rules**

### **Validation Requirements**
1. **Type Safety**: All values must match schema-defined types
2. **Range Validation**: Numeric values within specified ranges
3. **Required Fields**: All required sections must be present
4. **Cross-Reference**: Inheritance consistency between environments
5. **Business Logic**: Values must make business sense

### **Validation Examples**
```python
# Automatic validation on load
config = ConfigurationManager(base_path='/config')

# Manual validation
validation_results = config.validate_all()
if validation_results['overall_status'] != 'PASSED':
    raise ConfigurationError("Invalid configuration")

# Environment-specific validation
config.environment = 'production'
if not config.reload('production'):
    raise ConfigurationError("Failed to load production config")
```

---

## 🔄 **Configuration Inheritance Examples**

### **Base Configuration** (`base.json`)
```json
{
  "processing": {
    "timeout_seconds": 30,
    "retry_attempts": 3
  },
  "intelligence": {
    "confidence_threshold": 0.8
  }
}
```

### **Development Override** (`development.json`)
```json
{
  "processing": {
    "timeout_seconds": 60
  },
  "debug": {
    "enabled": true,
    "verbose_logging": true
  }
}
```

### **Final Development Configuration**
```json
{
  "processing": {
    "timeout_seconds": 60,    // Overridden
    "retry_attempts": 3       // Inherited
  },
  "intelligence": {
    "confidence_threshold": 0.8  // Inherited
  },
  "debug": {
    "enabled": true,          // Environment-specific
    "verbose_logging": true   // Environment-specific
  }
}
```

---

## 🛠️ **Configuration Management Best Practices**

### **1. Environment Detection**
```python
# Automatic environment detection
config = ConfigurationManager()  # Auto-detects from ENV vars

# Manual environment specification
config = ConfigurationManager(environment='production')

# Runtime environment switching
config.environment = 'staging'
config.reload()
```

### **2. Hot Reload Configuration**
```python
# Enable file watching for live updates
config = ConfigurationManager(enable_hot_reload=True)

# Manual reload
config.reload()

# Environment-specific reload
config.reload('production')
```

### **3. Configuration Validation**
```python
# Validate on startup
if not config.validate_all()['overall_status'] == 'PASSED':
    raise SystemExit("Configuration validation failed")

# Validate specific sections
schema_results = config.validate_schemas()
inheritance_results = config.validate_inheritance()
```

### **4. Error Handling**
```python
try:
    value = config.get('processing.timeout_seconds')
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    value = 30  # Fallback default
```

---

## 🚨 **Troubleshooting Guide**

### **Common Issues**

#### **1. Configuration Not Loading**
```bash
# Check file permissions
ls -la /config/

# Validate JSON syntax
python -m json.tool config/base.json

# Check environment detection
echo $ENVIRONMENT
```

#### **2. Schema Validation Failures**
```bash
# Run validation tool
python backend/tools/validate_configuration.py

# Check specific schema
jsonschema -i config/goal_parser.json schemas/goal_parser_enhanced.json
```

#### **3. Environment Inheritance Issues**
```python
# Debug inheritance chain
config_info = config.get_configuration_info()
print(config_info['inheritance_chain'])

# Check environment-specific overrides
env_config = config.get_environment_config('production')
```

---

## 📈 **Performance Considerations**

### **Configuration Caching**
- Configuration values are cached in memory for performance
- Cache TTL configurable per environment
- Hot-reload invalidates cache automatically

### **Access Patterns**
```python
# Efficient: Cache configuration at startup
class MyService:
    def __init__(self):
        self.timeout = config.get('processing.timeout_seconds', 30)
        self.confidence = config.get('intelligence.confidence_threshold', 0.8)

# Inefficient: Repeated config access
def process_goal(goal):
    timeout = config.get('processing.timeout_seconds', 30)  # Every call
    # ... processing logic
```

### **Memory Usage**
- Configuration manager uses singleton pattern
- Memory footprint scales with configuration size
- Automatic cleanup of expired cache entries

---

## 🔒 **Security Considerations**

### **Sensitive Configuration**
```python
# Environment variables for secrets
DATABASE_PASSWORD = os.environ.get('DB_PASSWORD')
API_KEYS = os.environ.get('EXTERNAL_API_KEYS')

# Encrypted configuration sections
config.set_encrypted('database.password', password)
decrypted = config.get_decrypted('database.password')
```

### **Access Control**
```python
# Read-only configuration
config.set_readonly('system.version')

# Environment-specific access
if config.environment == 'production':
    config.restrict_writes()
```

---

## ✅ **Configuration Checklist for Production**

### **Pre-Deployment Validation**
- [ ] All configuration files validate against schemas
- [ ] Environment inheritance works correctly
- [ ] No hardcoded values in application code
- [ ] All required configuration sections present
- [ ] Performance thresholds appropriate for environment
- [ ] Security configuration properly set
- [ ] Monitoring and logging configured
- [ ] Backup and recovery procedures tested

### **Post-Deployment Monitoring**
- [ ] Configuration loading performance
- [ ] Cache hit rates and efficiency
- [ ] Hot-reload functionality
- [ ] Error rates and fallback usage
- [ ] Business metric consistency

---

**This completes the comprehensive configuration documentation and examples for Hour 4-6 of Day 2.**
