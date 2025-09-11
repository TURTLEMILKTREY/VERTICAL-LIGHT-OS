# Configuration Schema Documentation

## Overview

This document describes the comprehensive configuration schema system for the VERTICAL-LIGHT-OS backend services. The system provides type-safe, validated, and environment-specific configuration management.

## Schema Structure

### Enhanced Schema Features

1. **JSON Schema Draft-07 Compliance**: All schemas use draft-07 for maximum compatibility
2. **Comprehensive Type Safety**: Every property has strict type definitions and validation
3. **Default Values**: All properties include sensible production defaults
4. **Validation Rules**: Min/max constraints, enums, and format validation
5. **Environment Inheritance**: Base configurations with environment overrides

## Configuration Inheritance

### Base Configuration (`base.json`)
- Contains default values for all environments
- Defines core system parameters
- Provides fallback values when environment configs are incomplete

### Environment Configuration (`development.json`, `production.json`)
- Inherits from base configuration
- Overrides environment-specific values
- Can add environment-specific properties

### Inheritance Rules
1. Environment config overrides base config
2. Environment variables override config files
3. Missing values fall back to defaults in schemas
4. Validation ensures all required values are present

## Goal Parser Configuration (`goal_parser_enhanced.json`)

### Core Sections

#### Processing Configuration
```json
{
  "processing": {
    "max_goals_per_request": 10,
    "timeout_seconds": 30.0,
    "concurrent_processing": 3,
    "retry_attempts": 2
  }
}
```

#### Intelligence Configuration
```json
{
  "intelligence": {
    "analysis_depth": "comprehensive",
    "confidence_threshold": 0.8,
    "market_data_weight": 0.7,
    "historical_weight": 0.3
  }
}
```

#### Budget Thresholds
```json
{
  "budget_thresholds": {
    "micro": [0, 1000],
    "small": [1000, 10000],
    "medium": [10000, 100000],
    "large": [100000, 1000000],
    "enterprise": [1000000, null]
  }
}
```

#### Performance Thresholds
```json
{
  "performance_thresholds": {
    "acquisition": {"min": 0.02, "target": 0.05, "max": 0.12},
    "engagement": {"min": 0.15, "target": 0.25, "max": 0.40},
    "retention": {"min": 0.60, "target": 0.75, "max": 0.90}
  }
}
```

#### Regional and Industry Multipliers
```json
{
  "region_multipliers": {
    "north_america": {"growth_rate": 1.05, "competition_factor": 1.2},
    "europe": {"growth_rate": 1.02, "competition_factor": 1.1},
    "asia_pacific": {"growth_rate": 1.08, "competition_factor": 0.9}
  },
  "industry_multipliers": {
    "technology": {"growth_factor": 1.15, "volatility": 0.3},
    "healthcare": {"growth_factor": 1.08, "volatility": 0.15},
    "finance": {"growth_factor": 1.05, "volatility": 0.25}
  }
}
```

#### Economic Factors
```json
{
  "economic_factors": {
    "base_growth_rate": 0.03,
    "inflation_adjustment": 0.025,
    "market_volatility": 0.15,
    "seasonal_variance": 0.1
  }
}
```

## Campaign Generator Configuration (`campaign_generator_enhanced.json`)

### Core Sections

#### Generation Configuration
```json
{
  "generation": {
    "max_campaigns_per_request": 5,
    "timeout_seconds": 120,
    "concurrent_generations": 3,
    "retry_attempts": 2
  }
}
```

#### Channel Intelligence
```json
{
  "channel_intelligence": {
    "analysis_depth": "standard",
    "confidence_threshold": 0.75,
    "industry_multipliers": {
      "technology": {
        "social_media": 1.1,
        "search_advertising": 1.2,
        "email_marketing": 1.0,
        "content_marketing": 1.3
      }
    }
  }
}
```

#### Channel Performance Baselines
```json
{
  "channel_performance": {
    "search_advertising": {
      "ctr_range": [0.02, 0.08],
      "cpc_range": [1.5, 8.0],
      "conversion_rate_range": [0.02, 0.12],
      "reach_potential": 0.95,
      "targeting_precision": 0.90
    }
  }
}
```

#### Audience Channel Affinity
```json
{
  "audience_channel_affinity": {
    "age_groups": {
      "18_35": {
        "social_media": {"base": 0.90, "sophistication_factor": 0.05},
        "search_advertising": {"base": 0.75, "sophistication_factor": 0.10}
      }
    }
  }
}
```

#### Optimization Configuration
```json
{
  "optimization": {
    "budget_allocation_strategy": "hybrid",
    "reserve_percentage": 0.15,
    "performance_weights": {
      "reach": 0.25,
      "engagement": 0.30,
      "conversion": 0.35,
      "cost_efficiency": 0.10
    }
  }
}
```

#### Learning Configuration
```json
{
  "learning": {
    "learning_rate": 0.2,
    "decay_rate": 0.8,
    "adaptation_threshold": 0.1
  }
}
```

## Validation Rules

### Type Safety
- All numeric values have min/max constraints
- Strings use enum validation where appropriate
- Arrays specify item types and length constraints
- Objects define required properties and disallow additional properties

### Business Logic Validation
- Budget ranges must be logical (min < max)
- Percentages constrained to [0, 1] range
- Performance multipliers within realistic bounds [0.1, 3.0]
- Timeout values within practical limits

### Default Values Strategy
- Conservative defaults for production safety
- Performance-optimized values for common use cases
- Industry-standard baselines for marketing metrics
- Fail-safe fallbacks for all critical parameters

## Environment-Specific Overrides

### Development Environment
```json
{
  "processing": {
    "timeout_seconds": 60,
    "max_goals_per_request": 3
  },
  "intelligence": {
    "analysis_depth": "basic"
  }
}
```

### Production Environment
```json
{
  "processing": {
    "timeout_seconds": 30,
    "concurrent_processing": 5
  },
  "caching": {
    "market_data_ttl_hours": 1,
    "performance_cache_ttl": 900
  }
}
```

## Usage Examples

### Loading Configuration
```python
from config.config_manager import ConfigurationManager

# Initialize manager
config_manager = ConfigurationManager()

# Get goal parser configuration
processing_config = config_manager.get('goal_parser.processing')
timeout = config_manager.get('goal_parser.processing.timeout_seconds', default=30)

# Get campaign generator configuration
channel_performance = config_manager.get('campaign_generator.channel_performance.search_advertising')
learning_rate = config_manager.get('campaign_generator.learning.learning_rate')
```

### Environment-Specific Loading
```python
# Load production configuration
prod_config = config_manager.get('goal_parser.processing', environment='production')

# Load development configuration with fallback
dev_timeout = config_manager.get('goal_parser.processing.timeout_seconds', 
                                default=60, environment='development')
```

## Best Practices

### Configuration Design
1. **Always provide defaults**: Every configuration value should have a sensible default
2. **Use validation**: Leverage JSON Schema constraints to catch invalid configurations
3. **Document everything**: Include descriptions for all configuration properties
4. **Environment separation**: Use environment-specific configs for deployment differences
5. **Hot-reload support**: Design configurations to support runtime updates

### Performance Optimization
1. **Use caching**: Enable caching for frequently accessed configuration values
2. **Batch operations**: Load related configuration sections together
3. **Monitor access patterns**: Track which configurations are accessed most frequently
4. **Validate once**: Perform validation during initialization, not on every access

### Security Considerations
1. **Sensitive values**: Use environment variables for secrets and credentials
2. **Access control**: Restrict configuration modification in production
3. **Audit trail**: Log configuration changes and access patterns
4. **Validation**: Always validate configuration values to prevent injection attacks

## Migration Guide

When updating from hardcoded values to configuration:

1. **Identify hardcoded values** in your code
2. **Add to schema** with appropriate validation rules
3. **Set defaults** in base configuration
4. **Update code** to use `config_manager.get()`
5. **Test thoroughly** in development environment
6. **Deploy incrementally** with monitoring
