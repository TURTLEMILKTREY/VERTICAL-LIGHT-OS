"""
Advanced configuration management system for Hospital AI Consulting OS.

This module provides comprehensive configuration management with validation,
environment-specific settings, secrets management, and runtime configuration updates.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Type
from dataclasses import dataclass, field
from enum import Enum
import logging
from contextlib import contextmanager

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
 """Application environment types."""
 DEVELOPMENT = "development"
 TESTING = "testing"
 STAGING = "staging"
 PRODUCTION = "production"


class LogLevel(str, Enum):
 """Logging level options."""
 DEBUG = "DEBUG"
 INFO = "INFO"
 WARNING = "WARNING"
 ERROR = "ERROR"
 CRITICAL = "CRITICAL"


@dataclass
class ConfigSource:
 """Configuration source metadata."""
 source_type: str # file, env, vault, etc.
 location: str
 priority: int
 last_updated: Optional[str] = None
 is_encrypted: bool = False


class DatabaseConfig(BaseModel):
 """Database configuration settings."""

 url: str = Field(..., description="Database connection URL")
 echo: bool = Field(default=False, description="Enable SQL query logging")
 pool_size: int = Field(default=10, description="Connection pool size")
 max_overflow: int = Field(default=20, description="Max pool overflow")
 pool_timeout: int = Field(default=30, description="Connection timeout")
 pool_recycle: int = Field(default=3600, description="Connection recycle time")

 @validator('pool_size')
 def validate_pool_size(cls, v):
 if v < 1 or v > 100:
 raise ValueError('Pool size must be between 1 and 100')
 return v

 @validator('url')
 def validate_url(cls, v):
 if not v.startswith(('postgresql://', 'sqlite://', 'mysql://')):
 raise ValueError('Invalid database URL scheme')
 return v


class RedisConfig(BaseModel):
 """Redis configuration settings."""

 url: str = Field(..., description="Redis connection URL")
 decode_responses: bool = Field(default=True)
 socket_timeout: int = Field(default=30)
 socket_connect_timeout: int = Field(default=30)
 socket_keepalive: bool = Field(default=True)
 socket_keepalive_options: Dict[str, int] = Field(default_factory=dict)
 max_connections: int = Field(default=50)

 @validator('max_connections')
 def validate_max_connections(cls, v):
 if v < 1 or v > 1000:
 raise ValueError('Max connections must be between 1 and 1000')
 return v


class APIConfig(BaseModel):
 """API server configuration settings."""

 host: str = Field(default="0.0.0.0", description="API server host")
 port: int = Field(default=8000, description="API server port")
 debug: bool = Field(default=False, description="Enable debug mode")
 reload: bool = Field(default=False, description="Enable auto-reload")
 workers: int = Field(default=1, description="Number of worker processes")
 max_request_size: int = Field(default=16777216, description="Max request size in bytes")
 timeout: int = Field(default=60, description="Request timeout in seconds")

 @validator('port')
 def validate_port(cls, v):
 if v < 1 or v > 65535:
 raise ValueError('Port must be between 1 and 65535')
 return v

 @validator('workers')
 def validate_workers(cls, v):
 if v < 1 or v > 32:
 raise ValueError('Workers must be between 1 and 32')
 return v


class SecurityConfig(BaseModel):
 """Security configuration settings."""

 secret_key: str = Field(..., description="Application secret key")
 algorithm: str = Field(default="HS256", description="JWT algorithm")
 access_token_expire_minutes: int = Field(default=30)
 refresh_token_expire_days: int = Field(default=7)
 password_hash_rounds: int = Field(default=12)
 max_login_attempts: int = Field(default=5)
 lockout_duration_minutes: int = Field(default=30)

 @validator('secret_key')
 def validate_secret_key(cls, v):
 if len(v) < 32:
 raise ValueError('Secret key must be at least 32 characters')
 return v

 @validator('password_hash_rounds')
 def validate_hash_rounds(cls, v):
 if v < 8 or v > 16:
 raise ValueError('Hash rounds must be between 8 and 16')
 return v


class MonitoringConfig(BaseModel):
 """Monitoring and observability configuration."""

 enabled: bool = Field(default=True)
 metrics_port: int = Field(default=9090)
 health_check_interval: int = Field(default=30)
 log_level: LogLevel = Field(default=LogLevel.INFO)
 structured_logging: bool = Field(default=True)
 trace_sampling_rate: float = Field(default=0.1)

 @validator('trace_sampling_rate')
 def validate_sampling_rate(cls, v):
 if v < 0.0 or v > 1.0:
 raise ValueError('Sampling rate must be between 0.0 and 1.0')
 return v


class HospitalConfig(BaseModel):
 """Hospital-specific configuration."""

 default_timezone: str = Field(default="Asia/Kolkata")
 currency: str = Field(default="INR")
 fiscal_year_start: str = Field(default="04-01") # April 1st
 business_hours_start: str = Field(default="06:00")
 business_hours_end: str = Field(default="22:00")
 emergency_contact: str = Field(...)

 @validator('fiscal_year_start')
 def validate_fiscal_year_start(cls, v):
 try:
 month, day = v.split('-')
 if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
 raise ValueError
 except (ValueError, AttributeError):
 raise ValueError('Fiscal year start must be in MM-DD format')
 return v


class PerformanceConfig(BaseModel):
 """Performance optimization configuration."""

 cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
 batch_size: int = Field(default=100, description="Default batch processing size")
 max_concurrent_requests: int = Field(default=100)
 request_rate_limit: int = Field(default=1000, description="Requests per minute")
 memory_limit_mb: int = Field(default=512)

 @validator('cache_ttl')
 def validate_cache_ttl(cls, v):
 if v < 0 or v > 86400: # Max 24 hours
 raise ValueError('Cache TTL must be between 0 and 86400 seconds')
 return v


class ApplicationConfig(BaseSettings):
 """Main application configuration."""

 # Environment settings
 environment: Environment = Field(default=Environment.DEVELOPMENT)
 debug: bool = Field(default=False)
 version: str = Field(default="0.1.0")

 # Component configurations
 database: DatabaseConfig
 redis: RedisConfig
 api: APIConfig
 security: SecurityConfig
 monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
 hospital: HospitalConfig
 performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

 # Feature flags
 feature_flags: Dict[str, bool] = Field(default_factory=dict)

 # Custom settings
 custom_settings: Dict[str, Any] = Field(default_factory=dict)

 class Config:
 env_file = ".env"
 env_file_encoding = "utf-8"
 env_nested_delimiter = "__"
 case_sensitive = False
 validate_assignment = True

 @validator('environment')
 def validate_environment(cls, v):
 if v == Environment.PRODUCTION and cls.debug:
 raise ValueError('Debug mode cannot be enabled in production')
 return v


class ConfigManager:
 """
 Advanced configuration manager with multiple source support.

 Features:
 - Multiple configuration sources (files, environment, secrets)
 - Environment-specific configurations
 - Runtime configuration updates
 - Configuration validation
 - Secrets management integration
 """

 def __init__(
 self,
 config_dir: Optional[Path] = None,
 environment: Optional[Environment] = None,
 enable_hot_reload: bool = False
 ):
 """
 Initialize configuration manager.

 Args:
 config_dir: Directory containing configuration files
 environment: Target environment
 enable_hot_reload: Enable hot reloading of configurations
 """
 self.config_dir = config_dir or Path(__file__).parent
 self.environment = environment or Environment.DEVELOPMENT
 self.enable_hot_reload = enable_hot_reload

 self._config: Optional[ApplicationConfig] = None
 self._sources: List[ConfigSource] = []
 self._logger = logging.getLogger(__name__)

 # Initialize configuration
 self._load_configuration()

 def _load_configuration(self) -> None:
 """Load configuration from multiple sources."""
 config_data = {}

 # Load base configuration
 base_config_path = self.config_dir / "base.json"
 if base_config_path.exists():
 config_data.update(self._load_json_file(base_config_path))
 self._sources.append(ConfigSource(
 source_type="file",
 location=str(base_config_path),
 priority=1
 ))

 # Load environment-specific configuration
 env_config_path = self.config_dir / f"{self.environment.value}.json"
 if env_config_path.exists():
 config_data.update(self._load_json_file(env_config_path))
 self._sources.append(ConfigSource(
 source_type="file",
 location=str(env_config_path),
 priority=2
 ))

 # Load local overrides
 local_config_path = self.config_dir / "local.json"
 if local_config_path.exists():
 config_data.update(self._load_json_file(local_config_path))
 self._sources.append(ConfigSource(
 source_type="file",
 location=str(local_config_path),
 priority=3
 ))

 # Override with environment variables
 env_overrides = self._load_environment_variables()
 if env_overrides:
 config_data.update(env_overrides)
 self._sources.append(ConfigSource(
 source_type="environment",
 location="env_vars",
 priority=4
 ))

 # Create configuration instance
 try:
 self._config = ApplicationConfig(**config_data)
 self._logger.info(
 f"Configuration loaded successfully for {self.environment.value} environment"
 )
 except Exception as e:
 self._logger.error(f"Failed to load configuration: {e}")
 raise

 def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
 """Load configuration from JSON file."""
 try:
 with open(file_path, 'r', encoding='utf-8') as f:
 return json.load(f)
 except Exception as e:
 self._logger.error(f"Failed to load config file {file_path}: {e}")
 return {}

 def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
 """Load configuration from YAML file."""
 try:
 with open(file_path, 'r', encoding='utf-8') as f:
 return yaml.safe_load(f) or {}
 except Exception as e:
 self._logger.error(f"Failed to load YAML config file {file_path}: {e}")
 return {}

 def _load_environment_variables(self) -> Dict[str, Any]:
 """Load configuration from environment variables."""
 env_vars = {}

 # Map environment variables to config structure
 env_mappings = {
 'DATABASE_URL': 'database.url',
 'REDIS_URL': 'redis.url',
 'SECRET_KEY': 'security.secret_key',
 'DEBUG': 'debug',
 'API_HOST': 'api.host',
 'API_PORT': 'api.port',
 'LOG_LEVEL': 'monitoring.log_level',
 }

 for env_var, config_path in env_mappings.items():
 if env_var in os.environ:
 self._set_nested_value(env_vars, config_path, os.environ[env_var])

 return env_vars

 def _set_nested_value(
 self, 
 dictionary: Dict[str, Any], 
 path: str, 
 value: str
 ) -> None:
 """Set nested dictionary value using dot notation."""
 keys = path.split('.')
 current = dictionary

 for key in keys[:-1]:
 if key not in current:
 current[key] = {}
 current = current[key]

 # Convert string values to appropriate types
 final_value = self._convert_env_value(value)
 current[keys[-1]] = final_value

 def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
 """Convert environment variable string to appropriate type."""
 # Boolean conversion
 if value.lower() in ('true', 'false'):
 return value.lower() == 'true'

 # Integer conversion
 try:
 return int(value)
 except ValueError:
 pass

 # Float conversion
 try:
 return float(value)
 except ValueError:
 pass

 # Return as string
 return value

 @property
 def config(self) -> ApplicationConfig:
 """Get current configuration."""
 if not self._config:
 raise RuntimeError("Configuration not loaded")
 return self._config

 def get_database_config(self) -> DatabaseConfig:
 """Get database configuration."""
 return self.config.database

 def get_redis_config(self) -> RedisConfig:
 """Get Redis configuration."""
 return self.config.redis

 def get_api_config(self) -> APIConfig:
 """Get API configuration."""
 return self.config.api

 def get_security_config(self) -> SecurityConfig:
 """Get security configuration."""
 return self.config.security

 def get_monitoring_config(self) -> MonitoringConfig:
 """Get monitoring configuration."""
 return self.config.monitoring

 def get_hospital_config(self) -> HospitalConfig:
 """Get hospital-specific configuration."""
 return self.config.hospital

 def get_performance_config(self) -> PerformanceConfig:
 """Get performance configuration."""
 return self.config.performance

 def is_feature_enabled(self, feature_name: str) -> bool:
 """Check if a feature flag is enabled."""
 return self.config.feature_flags.get(feature_name, False)

 def get_custom_setting(
 self, 
 setting_name: str, 
 default: Any = None
 ) -> Any:
 """Get custom setting value."""
 return self.config.custom_settings.get(setting_name, default)

 def update_feature_flag(self, feature_name: str, enabled: bool) -> None:
 """Update feature flag at runtime."""
 self.config.feature_flags[feature_name] = enabled
 self._logger.info(f"Feature '{feature_name}' {'enabled' if enabled else 'disabled'}")

 def reload_configuration(self) -> None:
 """Reload configuration from sources."""
 self._logger.info("Reloading configuration...")
 self._sources.clear()
 self._load_configuration()

 def validate_configuration(self) -> Dict[str, Any]:
 """Validate current configuration and return report."""
 validation_report = {
 'valid': True,
 'errors': [],
 'warnings': [],
 'environment': self.environment.value,
 'sources': len(self._sources)
 }

 try:
 # Validate configuration model
 self.config.model_validate(self.config.model_dump())

 # Environment-specific validations
 if self.config.environment == Environment.PRODUCTION:
 if self.config.debug:
 validation_report['errors'].append(
 "Debug mode should not be enabled in production"
 )

 if self.config.security.secret_key == "default-secret-key":
 validation_report['errors'].append(
 "Default secret key should not be used in production"
 )

 # Performance validations
 if self.config.performance.max_concurrent_requests > 1000:
 validation_report['warnings'].append(
 "High concurrent request limit may impact performance"
 )

 if validation_report['errors']:
 validation_report['valid'] = False

 except Exception as e:
 validation_report['valid'] = False
 validation_report['errors'].append(str(e))

 return validation_report

 def get_configuration_summary(self) -> Dict[str, Any]:
 """Get summary of current configuration."""
 return {
 'environment': self.config.environment.value,
 'version': self.config.version,
 'debug': self.config.debug,
 'sources': [
 {
 'type': source.source_type,
 'location': source.location,
 'priority': source.priority
 }
 for source in self._sources
 ],
 'feature_flags': dict(self.config.feature_flags),
 'database_url_scheme': self.config.database.url.split('://')[0],
 'api_endpoint': f"{self.config.api.host}:{self.config.api.port}",
 'log_level': self.config.monitoring.log_level.value
 }

 @contextmanager
 def temporary_config_override(self, **overrides):
 """Temporarily override configuration values."""
 original_values = {}

 try:
 # Store original values and apply overrides
 for key, value in overrides.items():
 if hasattr(self.config, key):
 original_values[key] = getattr(self.config, key)
 setattr(self.config, key, value)

 yield self.config

 finally:
 # Restore original values
 for key, value in original_values.items():
 setattr(self.config, key, value)


# Global configuration manager instance
config_manager: Optional[ConfigManager] = None


def get_config_manager(
 config_dir: Optional[Path] = None,
 environment: Optional[Environment] = None,
 force_reload: bool = False
) -> ConfigManager:
 """
 Get or create global configuration manager instance.

 Args:
 config_dir: Configuration directory
 environment: Target environment
 force_reload: Force reload of configuration

 Returns:
 Configuration manager instance
 """
 global config_manager

 if config_manager is None or force_reload:
 # Determine environment from env var if not provided
 if environment is None:
 env_name = os.getenv('ENVIRONMENT', 'development')
 try:
 environment = Environment(env_name)
 except ValueError:
 environment = Environment.DEVELOPMENT

 config_manager = ConfigManager(
 config_dir=config_dir,
 environment=environment,
 enable_hot_reload=os.getenv('CONFIG_HOT_RELOAD', 'false').lower() == 'true'
 )

 return config_manager


def get_config() -> ApplicationConfig:
 """Get current application configuration."""
 return get_config_manager().config


# Convenience functions for accessing specific configurations
def get_database_url() -> str:
 """Get database connection URL."""
 return get_config().database.url


def get_redis_url() -> str:
 """Get Redis connection URL."""
 return get_config().redis.url


def get_secret_key() -> str:
 """Get application secret key."""
 return get_config().security.secret_key


def is_debug_mode() -> bool:
 """Check if debug mode is enabled."""
 return get_config().debug


def get_log_level() -> str:
 """Get configured log level."""
 return get_config().monitoring.log_level.value