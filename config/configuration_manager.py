 """
Configuration Management System for Vertical Light OS
Handles loading, validation, and management of environment-specific configurations.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError
from collections import defaultdict
import threading
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ConfigurationValidationResult:
 """Result of configuration validation"""
 is_valid: bool
 errors: List[str] = field(default_factory=list)
 warnings: List[str] = field(default_factory=list)
 validated_config: Optional[Dict[str, Any]] = None

class ConfigurationError(Exception):
 """Raised when configuration loading or validation fails"""
 pass

class ConfigurationManager:
 """
 Manages environment-specific configurations with validation and hot-reloading.

 Features:
 - Environment-based configuration loading
 - JSON schema validation
 - Configuration inheritance (base -> environment)
 - Hot-reloading capabilities
 - Thread-safe configuration access
 - Environment variable substitution
 """

 def __init__(self, 
 config_dir: str = "config",
 environment: Optional[str] = None,
 enable_hot_reload: bool = False):
 """
 Initialize configuration manager

 Args:
 config_dir: Directory containing configuration files
 environment: Target environment (auto-detected if None)
 enable_hot_reload: Enable automatic config reloading on file changes
 """
 self.config_dir = Path(config_dir)
 self.environment = environment or self._detect_environment()
 self.enable_hot_reload = enable_hot_reload

 # Thread-safe configuration storage
 self._config_lock = threading.RLock()
 self._config_cache: Dict[str, Any] = {}
 self._config_loaded_at: Optional[datetime] = None
 self._file_timestamps: Dict[str, float] = {}

 # Load schema for validation
 self._schema = self._load_schema()

 # Load initial configuration
 self._load_configuration()

 logger.info(f"ConfigurationManager initialized for environment: {self.environment}")

 def _detect_environment(self) -> str:
 """Auto-detect environment from various sources"""
 # Check environment variable
 env = os.getenv('ENVIRONMENT', os.getenv('ENV'))
 if env:
 return env.lower()

 # Check for common environment indicators
 if os.getenv('DEVELOPMENT') or os.getenv('DEBUG'):
 return 'development'
 elif os.getenv('STAGING'):
 return 'staging'
 elif os.getenv('PRODUCTION') or os.getenv('PROD'):
 return 'production'

 # Default to development
 logger.warning("Could not detect environment, defaulting to 'development'")
 return 'development'

 def _load_schema(self) -> Dict[str, Any]:
 """Load and parse JSON schema for validation"""
 schema_path = self.config_dir / "schema.json"

 if not schema_path.exists():
 logger.warning(f"Schema file not found at {schema_path}")
 return {}

 try:
 with open(schema_path, 'r') as f:
 return json.load(f)
 except Exception as e:
 logger.error(f"Failed to load schema: {e}")
 return {}

 def _load_configuration(self):
 """Load and merge configuration files"""
 with self._config_lock:
 try:
 # Load base configuration
 base_config = self._load_config_file("base.json")

 # Load environment-specific configuration
 env_config_path = f"environments/{self.environment}.json"
 env_config = self._load_config_file(env_config_path)

 # Merge configurations (environment overrides base)
 merged_config = self._merge_configs(base_config, env_config)

 # Substitute environment variables
 resolved_config = self._substitute_environment_variables(merged_config)

 # Validate configuration
 validation_result = self._validate_configuration(resolved_config)
 if not validation_result.is_valid:
 raise ConfigurationError(f"Configuration validation failed: {validation_result.errors}")

 # Update cache
 self._config_cache = validation_result.validated_config
 self._config_loaded_at = datetime.now()

 logger.info(f"Configuration loaded successfully for environment: {self.environment}")

 except Exception as e:
 logger.error(f"Failed to load configuration: {e}")
 raise ConfigurationError(f"Configuration loading failed: {e}")

 def _load_config_file(self, relative_path: str) -> Dict[str, Any]:
 """Load a single configuration file"""
 config_path = self.config_dir / relative_path

 if not config_path.exists():
 if "base.json" in relative_path:
 raise ConfigurationError(f"Base configuration file not found: {config_path}")
 logger.warning(f"Configuration file not found: {config_path}")
 return {}

 try:
 # Track file timestamp for hot-reloading
 self._file_timestamps[str(config_path)] = config_path.stat().st_mtime

 with open(config_path, 'r') as f:
 config = json.load(f)

 logger.debug(f"Loaded configuration file: {config_path}")
 return config

 except json.JSONDecodeError as e:
 raise ConfigurationError(f"Invalid JSON in {config_path}: {e}")
 except Exception as e:
 raise ConfigurationError(f"Failed to load {config_path}: {e}")

 def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
 """
 Deep merge configuration dictionaries.
 Override values take precedence over base values.
 """
 result = base.copy()

 for key, value in override.items():
 if key in result and isinstance(result[key], dict) and isinstance(value, dict):
 result[key] = self._merge_configs(result[key], value)
 else:
 result[key] = value

 return result

 def _substitute_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
 """
 Recursively substitute environment variables in configuration values.
 Supports ${VARIABLE_NAME} and ${VARIABLE_NAME:default_value} syntax.
 """
 if isinstance(config, dict):
 return {k: self._substitute_environment_variables(v) for k, v in config.items()}
 elif isinstance(config, list):
 return [self._substitute_environment_variables(item) for item in config]
 elif isinstance(config, str):
 return self._substitute_env_vars_in_string(config)
 else:
 return config

 def _substitute_env_vars_in_string(self, value: str) -> str:
 """Substitute environment variables in a string value"""
 import re

 # Pattern matches ${VAR_NAME} or ${VAR_NAME:default_value}
 pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

 def replace_var(match):
 var_name = match.group(1)
 default_value = match.group(2) if match.group(2) is not None else ''

 env_value = os.getenv(var_name)
 if env_value is not None:
 return env_value
 elif default_value:
 return default_value
 else:
 logger.warning(f"Environment variable {var_name} not found and no default provided")
 return match.group(0) # Return original string if no value found

 return re.sub(pattern, replace_var, value)

 def _validate_configuration(self, config: Dict[str, Any]) -> ConfigurationValidationResult:
 """Validate configuration against JSON schema"""
 result = ConfigurationValidationResult(is_valid=True)

 if not self._schema:
 result.warnings.append("No schema available for validation")
 result.validated_config = config
 return result

 try:
 # Validate against schema
 validate(instance=config, schema=self._schema)
 result.validated_config = config

 # Additional business logic validations
 self._validate_business_logic(config, result)

 except ValidationError as e:
 result.is_valid = False
 result.errors.append(f"Schema validation error: {e.message}")
 logger.error(f"Configuration validation failed: {e.message}")

 except Exception as e:
 result.is_valid = False
 result.errors.append(f"Validation error: {str(e)}")
 logger.error(f"Configuration validation failed: {e}")

 return result

 def _validate_business_logic(self, config: Dict[str, Any], result: ConfigurationValidationResult):
 """Additional business logic validations"""

 # Validate learning weights sum to 1.0
 learning_system = config.get('learning_system', {})
 learning_weights = learning_system.get('learning_weights', {})

 recent_weight = learning_weights.get('recent_data_weight', 0)
 historical_weight = learning_weights.get('historical_data_weight', 0)

 if abs((recent_weight + historical_weight) - 1.0) > 0.01:
 result.warnings.append(
 f"Learning weights don't sum to 1.0: recent={recent_weight}, "
 f"historical={historical_weight}"
 )

 # Validate source weights in dynamic_values
 for section_name, section_config in config.get('dynamic_values', {}).items():
 sources = section_config.get('sources', [])
 if sources:
 total_weight = sum(source.get('weight', 0) for source in sources)
 if abs(total_weight - 1.0) > 0.01:
 result.warnings.append(
 f"Source weights in {section_name} don't sum to 1.0: total={total_weight}"
 )

 # Validate cache TTL relationships
 cache_config = config.get('cache', {})
 default_ttl = cache_config.get('default_ttl', 0)
 performance_ttl = cache_config.get('performance_ttl', 0)

 if performance_ttl > default_ttl:
 result.warnings.append(
 "Performance TTL is greater than default TTL, which may cause inefficient caching"
 )

 def get(self, key: str, default: Any = None) -> Any:
 """
 Get configuration value by dot-notation key.

 Args:
 key: Configuration key (e.g., 'api_integration.timeout_seconds')
 default: Default value if key not found

 Returns:
 Configuration value or default
 """
 with self._config_lock:
 # Check for hot-reload if enabled
 if self.enable_hot_reload and self._should_reload():
 self._load_configuration()

 # Navigate nested configuration
 current = self._config_cache
 for key_part in key.split('.'):
 if isinstance(current, dict) and key_part in current:
 current = current[key_part]
 else:
 return default

 return current

 def get_section(self, section: str) -> Dict[str, Any]:
 """Get entire configuration section"""
 return self.get(section, {})

 def get_all(self) -> Dict[str, Any]:
 """Get complete configuration"""
 with self._config_lock:
 return self._config_cache.copy()

 def _should_reload(self) -> bool:
 """Check if configuration files have been modified"""
 try:
 for file_path, last_mtime in self._file_timestamps.items():
 current_mtime = Path(file_path).stat().st_mtime
 if current_mtime > last_mtime:
 logger.info(f"Configuration file modified: {file_path}")
 return True
 return False
 except Exception as e:
 logger.error(f"Error checking file modifications: {e}")
 return False

 def reload(self):
 """Manually reload configuration"""
 logger.info("Manually reloading configuration")
 self._load_configuration()

 def validate_current_config(self) -> ConfigurationValidationResult:
 """Validate current loaded configuration"""
 with self._config_lock:
 return self._validate_configuration(self._config_cache)

 @property
 def environment_name(self) -> str:
 """Get current environment name"""
 return self.environment

 @property
 def config_loaded_at(self) -> Optional[datetime]:
 """Get timestamp when configuration was last loaded"""
 return self._config_loaded_at

 def is_development(self) -> bool:
 """Check if running in development environment"""
 return self.environment == 'development'

 def is_staging(self) -> bool:
 """Check if running in staging environment"""
 return self.environment == 'staging'

 def is_production(self) -> bool:
 """Check if running in production environment"""
 return self.environment == 'production'

# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None

def get_config_manager(config_dir: str = "config", 
 environment: Optional[str] = None) -> ConfigurationManager:
 """Get or create global configuration manager instance"""
 global _config_manager

 if _config_manager is None:
 _config_manager = ConfigurationManager(
 config_dir=config_dir, 
 environment=environment,
 enable_hot_reload=os.getenv('CONFIG_HOT_RELOAD', '').lower() == 'true'
 )

 return _config_manager

def get_config(key: str, default: Any = None) -> Any:
 """Convenience function to get configuration value"""
 return get_config_manager().get(key, default)

def get_config_section(section: str) -> Dict[str, Any]:
 """Convenience function to get configuration section"""
 return get_config_manager().get_section(section)

# Example usage and testing functions
if __name__ == "__main__":
 # Example usage
 logging.basicConfig(level=logging.DEBUG)

 try:
 # Initialize configuration manager
 config_manager = ConfigurationManager(
 config_dir="config",
 environment="development"
 )

 # Test configuration access
 print(f"Environment: {config_manager.environment_name}")
 print(f"Cache TTL: {config_manager.get('cache.default_ttl')}")
 print(f"API Timeout: {config_manager.get('api_integration.timeout_seconds')}")
 print(f"Learning System Enabled: {config_manager.get('learning_system.enabled')}")

 # Validate current configuration
 validation_result = config_manager.validate_current_config()
 print(f"Configuration Valid: {validation_result.is_valid}")
 if validation_result.warnings:
 print(f"Warnings: {validation_result.warnings}")

 except ConfigurationError as e:
 print(f"Configuration Error: {e}")
 except Exception as e:
 print(f"Unexpected Error: {e}")
