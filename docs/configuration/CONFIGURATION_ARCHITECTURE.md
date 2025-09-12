# Enterprise Configuration Architecture

## Overview

This project uses a **modular, enterprise-grade configuration system** designed for scalability, developer productivity, and team collaboration. The architecture supports multiple environments, service isolation, and easy onboarding for new developers.

## Configuration Structure

```
backend/config/
├── base.json                 # Core system settings (all environments)
├── campaign_generator.json   # Campaign generation service config
├── goal_parser.json         # Goal parsing service config
├── crm_sync.json           # CRM synchronization service config
├── environments/           # Environment-specific overrides
│   ├── development.json
│   ├── staging.json
│   └── production.json
├── schemas/               # JSON validation schemas
│   ├── campaign_generator.schema.json
│   └── goal_parser.schema.json
└── user.{env}.json       # Developer-specific local overrides
```

## Configuration Priority (Highest to Lowest)

1. **User Overrides** (`user.development.json`) - Developer-specific settings
2. **Environment Config** (`environments/production.json`) - Environment overrides
3. **Service Configs** (`campaign_generator.json`) - Service-specific settings
4. **Environment Variables** - Runtime environment variables
5. **Base Config** (`base.json`) - Default system settings

## Service Configuration Architecture

### Modular Design Benefits

- **Developer Isolation**: Each service has its own config file
- **Team Productivity**: Multiple developers can work on different services without conflicts
- **Scalability**: Easy to add new services without touching existing configs
- **Clear Ownership**: Each team/service owns its configuration
- **Easier Testing**: Service configs can be modified independently

### Service Config Example

**campaign_generator.json**:
```json
{
  "generation": {
    "max_campaigns_per_request": 5,
    "concurrent_generation_threads": 3,
    "timeout_seconds": 120
  },
  "channel_intelligence": {
    "performance_cache_ttl_hours": 6,
    "market_data_refresh_minutes": 30,
    "real_time_data": true
  },
  "channel_performance": {
    "search_advertising": {
      "ctr_range": [0.02, 0.08],
      "cpc_range": [1.5, 8.0],
      "conversion_rate_range": [0.02, 0.12],
      "targeting_precision": 0.9
    }
  }
}
```

## Developer Usage

### Basic Configuration Access

```python
from config.config_manager import ConfigurationManager

config_manager = ConfigurationManager()

# Access service configuration
campaign_config = config_manager.get('campaign_generator')

# Access specific service setting
timeout = config_manager.get('campaign_generator.generation.timeout_seconds')

# Access with fallback
max_campaigns = config_manager.get('campaign_generator.generation.max_campaigns_per_request', 3)
```

### Environment-Specific Configuration

```python
# Get production-specific value
prod_config = config_manager.get('campaign_generator', environment='production')

# Set development override
config_manager.set('campaign_generator.generation.timeout_seconds', 300, environment='development')
```

## Developer Onboarding

### For New Developers

1. **Clone the repository**
2. **Copy example configs**:
   ```bash
   cp backend/config/user.development.json.example backend/config/user.development.json
   ```
3. **Customize your local settings** in `user.development.json`
4. **Start development** - your settings won't conflict with teammates

### For New Services

1. **Create service config**: `backend/config/new_service.json`
2. **Add validation schema**: `backend/config/schemas/new_service.schema.json`
3. **Use in code**:
   ```python
   config = config_manager.get('new_service')
   ```

## Environment Management

### Development
- Uses `base.json` + `environments/development.json` + your `user.development.json`
- Hot-reload enabled for fast development
- Relaxed validation for experimentation

### Staging
- Uses `base.json` + `environments/staging.json`
- Production-like settings with debugging enabled
- Full validation enabled

### Production
- Uses `base.json` + `environments/production.json`
- Optimized for performance and reliability
- Strict validation and monitoring

## Configuration Best Practices

### For Service Teams

1. **Keep service configs focused** - Only include settings for your service
2. **Use meaningful defaults** - Set sensible defaults in your service config
3. **Document all settings** - Add comments explaining complex configurations
4. **Version your schemas** - Maintain JSON schemas for validation

### For DevOps Teams

1. **Environment overrides only** - Use environment configs for environment-specific values
2. **Secrets management** - Never store secrets in config files, use environment variables
3. **Monitoring** - Set up alerts for configuration validation failures
4. **Backup configs** - Version control all configuration files

### For Developers

1. **Use user overrides** - Create `user.{env}.json` for local development settings
2. **Test configuration changes** - Run configuration validation before committing
3. **Follow naming conventions** - Use snake_case for keys, group related settings
4. **Don't commit user files** - Keep `user.*.json` in `.gitignore`

## Configuration Validation

All configurations are validated against JSON schemas:

```bash
# Validate all configurations
python -m backend.tools.validate_configuration

# Validate specific service
python -m backend.tools.validate_configuration --service campaign_generator
```

## Hot Reload

Configuration changes are automatically detected and reloaded in development:

```python
# Configuration will update automatically when files change
config_manager = ConfigurationManager()
# File system watching is enabled by default in development
```

## Troubleshooting

### Common Issues

1. **Configuration not found**: Check if service config file exists
2. **Values not updating**: Verify configuration priority order
3. **Validation errors**: Check schema definitions in `schemas/` directory
4. **Performance issues**: Disable hot-reload in production

### Debug Configuration

```python
# Get configuration loading information
info = config_manager.get_configuration_info()
print(f"Loaded configurations: {info['loaded_configs']}")
print(f"Configuration sources: {info['sources']}")
print(f"Cache hit ratio: {info['cache_stats']['hit_ratio']}")
```

## Migration Guide

### From Single Config Files

1. **Identify service boundaries** in your existing config
2. **Extract service-specific sections** into individual files
3. **Keep shared settings** in `base.json`
4. **Update code** to use new configuration keys
5. **Test thoroughly** with validation tools

This architecture ensures that the configuration system scales with your team and project growth while maintaining developer productivity and system reliability.
