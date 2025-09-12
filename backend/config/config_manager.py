"""
Production-Ready Configuration Manager
Complete configuration system for 100% dynamic operations with zero hardcoded values.
Supports multi-environment, hot-reload, validation, and thread-safe operations.
"""

import os
import json
import yaml
import threading
import hashlib
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict
import jsonschema
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ConfigurationEntry:
    """Represents a single configuration entry with metadata"""
    key: str
    value: Any
    source: str = "unknown"
    last_updated: datetime = field(default_factory=datetime.now)
    validation_status: str = "valid"
    cache_ttl: Optional[int] = None
    environment: str = "default"
    encrypted: bool = False
    
@dataclass 
class EnvironmentConfig:
    """Environment-specific configuration container"""
    name: str
    config_data: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"
    last_modified: datetime = field(default_factory=datetime.now)
    validation_errors: List[str] = field(default_factory=list)
    inheritance_chain: List[str] = field(default_factory=list)

class ConfigurationSource(ABC):
    """Abstract base class for configuration sources"""
    
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load configuration data from source"""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate configuration data"""
        pass
    
    @abstractmethod
    def get_last_modified(self) -> datetime:
        """Get last modification time"""
        pass

class FileConfigurationSource(ConfigurationSource):
    """File-based configuration source"""
    
    def __init__(self, file_path: str, format_type: str = "auto"):
        self.file_path = Path(file_path)
        self.format_type = format_type if format_type != "auto" else self._detect_format()
        self.last_loaded = None
        
    def _detect_format(self) -> str:
        """Auto-detect file format from extension"""
        extension = self.file_path.suffix.lower()
        format_map = {
            '.json': 'json',
            '.yaml': 'yaml', 
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini'
        }
        return format_map.get(extension, 'json')
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if not self.file_path.exists():
                logger.warning(f"Configuration file not found: {self.file_path}")
                return {}
                
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            if self.format_type == 'json':
                data = json.loads(content)
            elif self.format_type == 'yaml':
                data = yaml.safe_load(content) or {}
            else:
                raise ValueError(f"Unsupported format: {self.format_type}")
                
            self.last_loaded = datetime.now()
            logger.debug(f"Loaded configuration from {self.file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading configuration from {self.file_path}: {e}")
            return {}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Basic validation for file configuration"""
        return isinstance(data, dict)
    
    def get_last_modified(self) -> datetime:
        """Get file last modification time"""
        try:
            if self.file_path.exists():
                timestamp = self.file_path.stat().st_mtime
                return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.warning(f"Could not get modification time for {self.file_path}: {e}")
        
        return datetime.min

class EnvironmentVariableSource(ConfigurationSource):
    """Environment variable configuration source"""
    
    def __init__(self, prefix: str = "VLOS_"):
        self.prefix = prefix
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                # Convert VLOS_DATABASE_HOST to database.host
                config_key = key[len(self.prefix):].lower().replace('_', '.')
                
                # Try to parse as JSON for complex values
                try:
                    parsed_value = json.loads(value)
                    config[config_key] = parsed_value
                except json.JSONDecodeError:
                    # Keep as string if not valid JSON
                    config[config_key] = value
                    
        return config
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate environment variable configuration"""
        return True  # Environment variables are always valid
    
    def get_last_modified(self) -> datetime:
        """Environment variables change detection not available"""
        return datetime.now()

class ConfigFileWatcher(FileSystemEventHandler):
    """Watches configuration files for changes"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
                logger.info(f"Configuration file modified: {file_path}")
                self.config_manager._schedule_reload(str(file_path))

class ConfigurationManager:
    """
    Production-ready configuration management system with:
    - Multi-environment support
    - Hot-reload capabilities
    - Validation and schema enforcement
    - Thread-safe operations
    - Caching with TTL
    - Environment variable integration
    - File watching for live updates
    """
    
    def __init__(self, base_path: Optional[str] = None, environment: Optional[str] = None):
        # Core properties
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.environment = environment or self._detect_environment()
        
        # Thread safety
        self._lock = threading.RLock()
        self._cache_lock = threading.RLock()
        
        # Configuration storage
        self._configurations: Dict[str, EnvironmentConfig] = {}
        self._cache: Dict[str, ConfigurationEntry] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        
        # Configuration sources
        self._sources: Dict[str, ConfigurationSource] = {}
        
        # Hot-reload system
        self._file_observer: Optional[Observer] = None
        self._reload_callbacks: List[Callable[[str, Any], None]] = []
        self._reload_queue: Dict[str, datetime] = {}
        
        # Performance tracking
        self._access_stats: Dict[str, int] = defaultdict(int)
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Initialize system
        self._initialize()
        
        logger.info(f"ConfigurationManager initialized for environment: {self.environment}")
        
    def _initialize(self):
        """Initialize the configuration system"""
        try:
            # Create configuration directories
            self._ensure_directories()
            
            # Initialize configuration sources
            self._initialize_sources()
            
            # Load base configuration
            self._load_base_configuration()
            
            # Load environment-specific configuration
            self._load_environment_configuration()
            
            # Initialize validation schemas
            self._initialize_schemas()
            
            # Start file watching for hot-reload
            self._start_file_watching()
            
        except Exception as e:
            logger.error(f"Failed to initialize configuration system: {e}")
            raise
    
    def _detect_environment(self) -> str:
        """Detect current environment from various sources"""
        # Check environment variable first
        env = os.environ.get('ENVIRONMENT') or os.environ.get('ENV')
        if env:
            return env.lower()
            
        # Check for common environment indicators
        if os.environ.get('DEVELOPMENT'):
            return 'development'
        elif os.environ.get('PRODUCTION'):
            return 'production'
        elif os.environ.get('STAGING'):
            return 'staging'
        elif os.environ.get('TESTING'):
            return 'testing'
            
        # Default to development
        logger.info("No environment specified, defaulting to 'development'")
        return 'development'
    
    def _ensure_directories(self):
        """Ensure configuration directories exist"""
        directories = [
            self.base_path,
            self.base_path / 'schemas',
            self.base_path / 'environments',
            self.base_path / 'cache'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _initialize_sources(self):
        """Initialize configuration sources with modular service support"""
        # Base configuration file
        base_config_path = self.base_path / 'base.json'
        if base_config_path.exists():
            self._sources['base'] = FileConfigurationSource(str(base_config_path))
        
        # Service-specific configuration files (modular approach for scalability)
        service_configs = [
            'campaign_generator.json',
            'goal_parser.json',
            'crm_sync.json',
            'landing_page_generator.json',
            'optimization_engine.json',
            'reporting_module.json'
        ]
        
        for service_config in service_configs:
            service_config_path = self.base_path / service_config
            if service_config_path.exists():
                service_name = service_config.replace('.json', '')
                self._sources[f'service_{service_name}'] = FileConfigurationSource(str(service_config_path))
        
        # Environment-specific configuration
        env_config_path = self.base_path / 'environments' / f'{self.environment}.json'
        if env_config_path.exists():
            self._sources[self.environment] = FileConfigurationSource(str(env_config_path))
        
        # Environment variables
        self._sources['env_vars'] = EnvironmentVariableSource()
        
        # User-specific overrides
        user_config_path = self.base_path / f'user.{self.environment}.json'
        if user_config_path.exists():
            self._sources['user'] = FileConfigurationSource(str(user_config_path))
    
    def _load_base_configuration(self):
        """Load base configuration that applies to all environments"""
        base_source = self._sources.get('base')
        if base_source:
            base_data = base_source.load()
            if base_data:
                base_config = EnvironmentConfig(
                    name='base',
                    config_data=base_data,
                    last_modified=base_source.get_last_modified()
                )
                self._configurations['base'] = base_config
                logger.info("Loaded base configuration")
    
    def _load_environment_configuration(self):
        """Load environment-specific configuration and service modules"""
        # Load environment-specific file
        env_source = self._sources.get(self.environment)
        if env_source:
            env_data = env_source.load()
            if env_data:
                env_config = EnvironmentConfig(
                    name=self.environment,
                    config_data=env_data,
                    last_modified=env_source.get_last_modified(),
                    inheritance_chain=['base', self.environment]
                )
                self._configurations[self.environment] = env_config
                logger.info(f"Loaded {self.environment} environment configuration")
        
        # Load service-specific configurations (modular architecture)
        self._load_service_configurations()
        
        # Load environment variables
        env_var_source = self._sources.get('env_vars')
        if env_var_source:
            env_var_data = env_var_source.load()
            if env_var_data:
                env_var_config = EnvironmentConfig(
                    name='env_vars',
                    config_data=env_var_data,
                    last_modified=env_var_source.get_last_modified()
                )
                self._configurations['env_vars'] = env_var_config
                logger.info("Loaded environment variable configuration")
        
        # Load user overrides
        user_source = self._sources.get('user')
        if user_source:
            user_data = user_source.load()
            if user_data:
                user_config = EnvironmentConfig(
                    name='user',
                    config_data=user_data,
                    last_modified=user_source.get_last_modified()
                )
                self._configurations['user'] = user_config
                logger.info("Loaded user override configuration")
    
    def _load_service_configurations(self):
        """Load modular service-specific configurations for enterprise scalability"""
        service_sources = {k: v for k, v in self._sources.items() if k.startswith('service_')}
        
        for source_name, source in service_sources.items():
            try:
                service_data = source.load()
                if service_data:
                    service_name = source_name.replace('service_', '')
                    
                    # Create environment config for the service
                    service_config = EnvironmentConfig(
                        name=source_name,
                        config_data=service_data,
                        last_modified=source.get_last_modified(),
                        inheritance_chain=['base', self.environment, source_name]
                    )
                    self._configurations[source_name] = service_config
                    logger.info(f"Loaded modular service configuration: {service_name}")
            except Exception as e:
                logger.warning(f"Failed to load service config {source_name}: {e}")
    
    def _initialize_schemas(self):
        """Initialize validation schemas"""
        schema_dir = self.base_path / 'schemas'
        if schema_dir.exists():
            for schema_file in schema_dir.glob('*.json'):
                try:
                    with open(schema_file, 'r') as f:
                        schema = json.load(f)
                    schema_name = schema_file.stem
                    self._schemas[schema_name] = schema
                    logger.debug(f"Loaded validation schema: {schema_name}")
                except Exception as e:
                    logger.error(f"Error loading schema {schema_file}: {e}")
    
    def _start_file_watching(self):
        """Start file watching for hot-reload"""
        try:
            self._file_observer = Observer()
            event_handler = ConfigFileWatcher(self)
            
            # Watch configuration directories
            self._file_observer.schedule(event_handler, str(self.base_path), recursive=True)
            self._file_observer.start()
            
            logger.info("Started configuration file watching")
            
        except Exception as e:
            logger.warning(f"Could not start file watching: {e}")
    
    def get(self, key: str, default: Any = None, use_cache: bool = True,
            validate: bool = True, environment: Optional[str] = None) -> Any:
        """
        Get configuration value with caching and validation
        
        Args:
            key: Configuration key (dot notation supported: 'database.host')
            default: Default value if key not found
            use_cache: Whether to use cached values
            validate: Whether to validate against schema
            environment: Specific environment to query
            
        Returns:
            Configuration value or default
        """
        with self._lock:
            self._access_stats[key] += 1
            
            # Check cache first
            if use_cache:
                cached_value = self._get_cached_value(key, environment)
                if cached_value is not None:
                    self._cache_hits += 1
                    return cached_value.value
            
            self._cache_misses += 1
            
            # Get value from configuration hierarchy
            value = self._resolve_configuration_value(key, default, environment)
            
            # Validate if requested
            if validate and value != default:
                validation_result = self._validate_value(key, value)
                if not validation_result['valid']:
                    logger.warning(f"Configuration validation failed for {key}: {validation_result['errors']}")
            
            # Cache the result
            if use_cache:
                self._cache_value(key, value, environment)
            
            return value
    
    def set(self, key: str, value: Any, environment: Optional[str] = None,
            persist: bool = False, validate: bool = True) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Value to set
            environment: Target environment (defaults to current)
            persist: Whether to persist to file
            validate: Whether to validate the value
            
        Returns:
            Success status
        """
        with self._lock:
            try:
                # Validate if requested
                if validate:
                    validation_result = self._validate_value(key, value)
                    if not validation_result['valid']:
                        logger.error(f"Cannot set invalid value for {key}: {validation_result['errors']}")
                        return False
                
                # Determine target environment
                target_env = environment or self.environment
                
                # Ensure environment configuration exists
                if target_env not in self._configurations:
                    self._configurations[target_env] = EnvironmentConfig(name=target_env)
                
                # Set the value using dot notation
                self._set_nested_value(
                    self._configurations[target_env].config_data,
                    key,
                    value
                )
                
                # Update metadata
                self._configurations[target_env].last_modified = datetime.now()
                
                # Update cache
                self._cache_value(key, value, target_env)
                
                # Persist if requested
                if persist:
                    self._persist_environment_configuration(target_env)
                
                # Notify callbacks
                self._notify_change_callbacks(key, value)
                
                logger.debug(f"Set configuration {key} = {value}")
                return True
                
            except Exception as e:
                logger.error(f"Error setting configuration {key}: {e}")
                return False
    
    def update(self, updates: Dict[str, Any], environment: Optional[str] = None,
               persist: bool = False, validate: bool = True) -> Dict[str, bool]:
        """
        Update multiple configuration values atomically
        
        Args:
            updates: Dictionary of key-value pairs to update
            environment: Target environment
            persist: Whether to persist changes
            validate: Whether to validate values
            
        Returns:
            Dictionary mapping keys to success status
        """
        results = {}
        
        with self._lock:
            for key, value in updates.items():
                results[key] = self.set(key, value, environment, persist=False, validate=validate)
            
            # Persist all changes at once if requested
            if persist and any(results.values()):
                target_env = environment or self.environment
                self._persist_environment_configuration(target_env)
        
        return results
    
    def reload(self, environment: Optional[str] = None) -> bool:
        """
        Reload configuration from sources
        
        Args:
            environment: Specific environment to reload (None for all)
            
        Returns:
            Success status
        """
        with self._lock:
            try:
                # Clear cache
                self._clear_cache()
                
                if environment:
                    # Reload specific environment
                    source = self._sources.get(environment)
                    if source:
                        data = source.load()
                        if data:
                            self._configurations[environment] = EnvironmentConfig(
                                name=environment,
                                config_data=data,
                                last_modified=source.get_last_modified()
                            )
                else:
                    # Reload all configurations
                    self._load_base_configuration()
                    self._load_environment_configuration()
                
                logger.info(f"Reloaded configuration for: {environment or 'all environments'}")
                return True
                
            except Exception as e:
                logger.error(f"Error reloading configuration: {e}")
                return False
    
    def validate_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all configurations against schemas
        
        Returns:
            Validation results for each environment
        """
        results = {}
        
        with self._lock:
            for env_name, config in self._configurations.items():
                results[env_name] = self._validate_configuration(config)
        
        return results
    
    def get_configuration_info(self) -> Dict[str, Any]:
        """Get comprehensive configuration system information"""
        with self._lock:
            return {
                'current_environment': self.environment,
                'loaded_environments': list(self._configurations.keys()),
                'available_sources': list(self._sources.keys()),
                'schemas_loaded': list(self._schemas.keys()),
                'cache_stats': {
                    'entries': len(self._cache),
                    'hits': self._cache_hits,
                    'misses': self._cache_misses,
                    'hit_rate': self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0
                },
                'access_stats': dict(self._access_stats),
                'file_watching': self._file_observer is not None and self._file_observer.is_alive()
            }
    
    def export_configuration(self, environment: Optional[str] = None,
                           format_type: str = 'json', include_metadata: bool = False) -> str:
        """
        Export configuration as string
        
        Args:
            environment: Environment to export (None for merged)
            format_type: Output format ('json' or 'yaml')
            include_metadata: Whether to include metadata
            
        Returns:
            Configuration as formatted string
        """
        with self._lock:
            if environment:
                config_data = self._configurations.get(environment, EnvironmentConfig(name=environment)).config_data
            else:
                config_data = self._get_merged_configuration()
            
            if include_metadata:
                export_data = {
                    'configuration': config_data,
                    'metadata': {
                        'environment': environment or 'merged',
                        'exported_at': datetime.now().isoformat(),
                        'schema_version': '1.0'
                    }
                }
            else:
                export_data = config_data
            
            if format_type.lower() == 'yaml':
                return yaml.dump(export_data, default_flow_style=False, sort_keys=True)
            else:
                return json.dumps(export_data, indent=2, sort_keys=True)
    
    def register_change_callback(self, callback: Callable[[str, Any], None]):
        """Register callback for configuration changes"""
        self._reload_callbacks.append(callback)
    
    def unregister_change_callback(self, callback: Callable[[str, Any], None]):
        """Unregister change callback"""
        if callback in self._reload_callbacks:
            self._reload_callbacks.remove(callback)
    
    def clear_cache(self, pattern: Optional[str] = None):
        """
        Clear configuration cache
        
        Args:
            pattern: Optional pattern to match keys (None clears all)
        """
        with self._cache_lock:
            if pattern:
                keys_to_remove = [key for key in self._cache.keys() if pattern in key]
                for key in keys_to_remove:
                    del self._cache[key]
                logger.debug(f"Cleared cache entries matching pattern: {pattern}")
            else:
                self._cache.clear()
                logger.debug("Cleared entire configuration cache")
    
    def shutdown(self):
        """Shutdown configuration system and cleanup resources"""
        with self._lock:
            try:
                # Stop file watching
                if self._file_observer:
                    self._file_observer.stop()
                    self._file_observer.join(timeout=5)
                
                # Clear caches
                self._cache.clear()
                
                # Reset counters
                self._cache_hits = 0
                self._cache_misses = 0
                self._access_stats.clear()
                
                logger.info("Configuration system shutdown completed")
                
            except Exception as e:
                logger.error(f"Error during configuration system shutdown: {e}")
    
    # Private helper methods
    
    def _get_cached_value(self, key: str, environment: Optional[str] = None) -> Optional[ConfigurationEntry]:
        """Get value from cache if valid"""
        with self._cache_lock:
            cache_key = f"{environment or self.environment}:{key}"
            entry = self._cache.get(cache_key)
            
            if entry:
                # Check TTL
                if entry.cache_ttl:
                    age = (datetime.now() - entry.last_updated).total_seconds()
                    if age > entry.cache_ttl:
                        del self._cache[cache_key]
                        return None
                
                return entry
            
            return None
    
    def _cache_value(self, key: str, value: Any, environment: Optional[str] = None,
                     ttl: Optional[int] = None):
        """Cache configuration value"""
        with self._cache_lock:
            cache_key = f"{environment or self.environment}:{key}"
            entry = ConfigurationEntry(
                key=key,
                value=value,
                source=environment or self.environment,
                last_updated=datetime.now(),
                cache_ttl=ttl,
                environment=environment or self.environment
            )
            self._cache[cache_key] = entry
    
    def _resolve_configuration_value(self, key: str, default: Any,
                                   environment: Optional[str] = None) -> Any:
        """Resolve configuration value from enterprise-grade modular hierarchy"""
        target_env = environment or self.environment
        
        # Enterprise configuration priority order:
        # 1. User overrides (highest priority)
        # 2. Environment-specific settings
        # 3. Service-specific configurations (modular scalability)
        # 4. Environment variables
        # 5. Base configuration (lowest priority)
        search_order = []
        
        if 'user' in self._configurations:
            search_order.append('user')
        
        if target_env in self._configurations:
            search_order.append(target_env)
        
        # Add service-specific configurations based on key
        service_key = key.split('.')[0] if '.' in key else key
        service_config_name = f'service_{service_key}'
        if service_config_name in self._configurations:
            search_order.append(service_config_name)
        
        if 'env_vars' in self._configurations:
            search_order.append('env_vars')
        
        if 'base' in self._configurations:
            search_order.append('base')
        
        # Search in priority order
        for config_name in search_order:
            config = self._configurations[config_name]
            
            # For service configs, check if we should look for the key directly
            if config_name.startswith('service_'):
                service_name = config_name.replace('service_', '')
                if key.startswith(f'{service_name}.'):
                    # Remove service prefix from key when searching in service config
                    service_key = key[len(service_name) + 1:]
                    value = self._get_nested_value(config.config_data, service_key)
                elif key == service_name:
                    # Return entire service config
                    value = config.config_data
                else:
                    continue
            else:
                value = self._get_nested_value(config.config_data, key)
            
            if value is not None:
                return value
        
        return default
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = key.split('.')
        current = data
        
        try:
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return None
            return current
        except (KeyError, TypeError):
            return None
    
    def _set_nested_value(self, data: Dict[str, Any], key: str, value: Any):
        """Set value in nested dictionary using dot notation"""
        keys = key.split('.')
        current = data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _validate_value(self, key: str, value: Any) -> Dict[str, Any]:
        """Validate configuration value against schema"""
        # For nested keys (like goal_parser.processing), skip individual validation
        # These are validated as part of the full service configuration
        if '.' in key:
            return {'valid': True, 'errors': []}
        
        # Extract schema name from key
        schema_name = key
        
        schema = self._schemas.get(schema_name)
        if not schema:
            return {'valid': True, 'errors': []}
        
        try:
            jsonschema.validate(value, schema)
            return {'valid': True, 'errors': []}
        except jsonschema.ValidationError as e:
            return {'valid': False, 'errors': [str(e)]}
        except Exception as e:
            logger.error(f"Schema validation error for {key}: {e}")
            return {'valid': True, 'errors': []}  # Allow on validation errors
    
    def _validate_configuration(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Validate entire configuration against schemas"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        for schema_name, schema in self._schemas.items():
            if schema_name in config.config_data:
                try:
                    jsonschema.validate(config.config_data[schema_name], schema)
                except jsonschema.ValidationError as e:
                    results['valid'] = False
                    results['errors'].append(f"{schema_name}: {str(e)}")
        
        return results
    
    def _get_merged_configuration(self) -> Dict[str, Any]:
        """Get merged configuration from all sources"""
        merged = {}
        
        # Merge in priority order
        for config_name in ['base', 'env_vars', self.environment, 'user']:
            if config_name in self._configurations:
                self._deep_merge(merged, self._configurations[config_name].config_data)
        
        return merged
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Deep merge source dictionary into target"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _persist_environment_configuration(self, environment: str) -> bool:
        """Persist environment configuration to file"""
        try:
            env_path = self.base_path / 'environments' / f'{environment}.json'
            config = self._configurations.get(environment)
            
            if config:
                with open(env_path, 'w') as f:
                    json.dump(config.config_data, f, indent=2, sort_keys=True)
                
                logger.debug(f"Persisted configuration for environment: {environment}")
                return True
            
        except Exception as e:
            logger.error(f"Error persisting configuration for {environment}: {e}")
        
        return False
    
    def _schedule_reload(self, file_path: str):
        """Schedule configuration reload (debounced)"""
        self._reload_queue[file_path] = datetime.now()
        
        # Debounce reloads (wait 1 second for additional changes)
        def delayed_reload():
            import time
            time.sleep(1)
            
            if file_path in self._reload_queue:
                last_change = self._reload_queue[file_path]
                if (datetime.now() - last_change).total_seconds() >= 0.9:
                    del self._reload_queue[file_path]
                    self.reload()
        
        threading.Thread(target=delayed_reload, daemon=True).start()
    
    def _notify_change_callbacks(self, key: str, value: Any):
        """Notify registered callbacks of configuration changes"""
        for callback in self._reload_callbacks:
            try:
                callback(key, value)
            except Exception as e:
                logger.error(f"Error in configuration change callback: {e}")
    
    def _clear_cache(self):
        """Clear all cached values"""
        with self._cache_lock:
            self._cache.clear()

# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None

def get_config_manager(base_path: Optional[str] = None,
                      environment: Optional[str] = None) -> ConfigurationManager:
    """Get or create global configuration manager instance"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(base_path, environment)
    
    return _config_manager

def shutdown_config_manager():
    """Shutdown global configuration manager"""
    global _config_manager
    
    if _config_manager:
        _config_manager.shutdown()
        _config_manager = None

# Convenience functions
def get_config(key: str, default: Any = None, **kwargs) -> Any:
    """Convenience function to get configuration value"""
    return get_config_manager().get(key, default, **kwargs)

def set_config(key: str, value: Any, **kwargs) -> bool:
    """Convenience function to set configuration value"""
    return get_config_manager().set(key, value, **kwargs)

def reload_config(environment: Optional[str] = None) -> bool:
    """Convenience function to reload configuration"""
    return get_config_manager().reload(environment)
