"""
HYBRID CONFIGURATION ARCHITECTURE - RECOMMENDED IMPLEMENTATION
=============================================================

This document outlines my recommended approach based on analysis of all options.
"""

# MY RECOMMENDATION: LAYERED HYBRID APPROACH
# ===========================================

"""
RECOMMENDED ARCHITECTURE: Four-Layer Configuration System

Layer 1: Schema-Driven Configuration (Foundation)
Layer 2: Property-Based Testing (Validation) 
Layer 3: External Configuration Files (User Control)
Layer 4: Graceful Degradation (Reliability)

WHY THIS COMBINATION WORKS BEST:
- Addresses all major concerns you raised
- Provides maximum user control without sacrificing reliability
- Eliminates hardcoded business assumptions completely
- Scales from simple to complex deployments
- Maintains performance while ensuring correctness
"""

import json
import os
from typing import Any, Dict, Optional, Type
from dataclasses import dataclass, field
from hypothesis import given, strategies as st
import pytest


# LAYER 1: SCHEMA-DRIVEN CONFIGURATION
# =====================================

@dataclass
class ConfigurationSchema:
 """Define configuration schema without default values"""

 # Market analysis parameters
 market_threshold: float = field(metadata={'min': 0.0, 'max': 1.0, 'required': False})
 intensity_weights: Dict[str, float] = field(default_factory=dict, metadata={'required': False})
 competitor_limit: int = field(metadata={'min': 1, 'max': 1000, 'required': False})

 # Analysis behavior parameters 
 analysis_depth: str = field(metadata={'options': ['minimal', 'standard', 'comprehensive'], 'required': False})
 update_frequency: int = field(metadata={'min': 1, 'max': 168, 'required': False}) # hours

 # Output format parameters
 output_format: str = field(metadata={'options': ['compact', 'detailed'], 'required': False})
 include_metadata: bool = field(metadata={'required': False})

 def validate_value(self, field_name: str, value: Any) -> bool:
 """Validate value against schema constraints"""
 field_info = self.__dataclass_fields__[field_name]
 metadata = field_info.metadata

 # Type validation
 expected_type = field_info.type
 if not isinstance(value, expected_type):
 try:
 # Try type conversion
 if expected_type == float:
 value = float(value)
 elif expected_type == int:
 value = int(value)
 elif expected_type == bool:
 value = bool(value)
 except (ValueError, TypeError):
 return False

 # Range validation
 if 'min' in metadata and value < metadata['min']:
 return False
 if 'max' in metadata and value > metadata['max']:
 return False

 # Options validation
 if 'options' in metadata and value not in metadata['options']:
 return False

 return True


# LAYER 2: PROPERTY-BASED TESTING INTEGRATION
# ============================================

class ConfigurationPropertyTesting:
 """Property-based testing for configuration system"""

 @staticmethod
 def generate_valid_config_strategy():
 """Generate hypothesis strategy for valid configurations"""
 return st.fixed_dictionaries({
 'market_threshold': st.floats(0.0, 1.0),
 'intensity_weights': st.dictionaries(
 st.text(min_size=1, max_size=20),
 st.floats(0.1, 10.0),
 min_size=1,
 max_size=5
 ),
 'competitor_limit': st.integers(1, 1000),
 'analysis_depth': st.sampled_from(['minimal', 'standard', 'comprehensive']),
 'update_frequency': st.integers(1, 168),
 'output_format': st.sampled_from(['compact', 'detailed']),
 'include_metadata': st.booleans()
 })

 @given(config=generate_valid_config_strategy())
 def test_service_with_any_valid_config(self, config):
 """Test service works with any schema-valid configuration"""
 service = CompetitiveAnalysisService(config)

 # Test with minimal data
 competitors = [{'competitor_id': 'test', 'market_share': 0.5}]
 result = service.analyze_competitive_landscape(competitors)

 # Properties that must always hold:
 assert isinstance(result, dict)
 assert 'analysis_id' in result
 assert len(str(result['analysis_id'])) > 0

 # Configuration should be respected
 if config.get('output_format') == 'compact':
 assert 'detailed_metrics' not in result
 if not config.get('include_metadata', True):
 assert 'metadata' not in result


# LAYER 3: EXTERNAL CONFIGURATION FILES
# ======================================

class ExternalConfigurationManager:
 """Manage external configuration files"""

 def __init__(self, config_dir: str = "config", environment: str = "development"):
 self.config_dir = config_dir
 self.environment = environment
 self.schema = ConfigurationSchema()

 def load_configuration(self) -> Dict[str, Any]:
 """Load configuration from external files with no hardcoded fallbacks"""
 config = {}

 # 1. Load base configuration (user's core settings)
 base_config_path = os.path.join(self.config_dir, "competitive_analysis.json")
 if os.path.exists(base_config_path):
 with open(base_config_path, 'r') as f:
 config.update(json.load(f))

 # 2. Load environment-specific overrides (user's env settings) 
 env_config_path = os.path.join(self.config_dir, "environments", f"{self.environment}.json")
 if os.path.exists(env_config_path):
 with open(env_config_path, 'r') as f:
 env_config = json.load(f)
 config.update(env_config)

 # 3. Load user-specific overrides (user's personal settings)
 user_config_path = os.path.join(self.config_dir, "user_overrides.json")
 if os.path.exists(user_config_path):
 with open(user_config_path, 'r') as f:
 user_config = json.load(f)
 config.update(user_config)

 # 4. Validate all loaded configuration
 validated_config = self._validate_loaded_config(config)

 return validated_config

 def _validate_loaded_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
 """Validate loaded configuration against schema"""
 validated = {}

 for field_name, value in config.items():
 if hasattr(self.schema, field_name):
 if self.schema.validate_value(field_name, value):
 validated[field_name] = value
 else:
 raise ConfigurationError(f"Invalid value for {field_name}: {value}")
 else:
 # Unknown configuration field - warn but include
 print(f"Warning: Unknown configuration field: {field_name}")
 validated[field_name] = value

 return validated

 def get_configuration_documentation(self) -> str:
 """Generate documentation for available configuration options"""
 docs = ["# Competitive Analysis Configuration\n"]

 for field_name, field_info in self.schema.__dataclass_fields__.items():
 docs.append(f"## {field_name}")
 docs.append(f"Type: {field_info.type.__name__}")

 metadata = field_info.metadata
 if 'min' in metadata:
 docs.append(f"Minimum: {metadata['min']}")
 if 'max' in metadata:
 docs.append(f"Maximum: {metadata['max']}")
 if 'options' in metadata:
 docs.append(f"Options: {', '.join(metadata['options'])}")
 if metadata.get('required', False):
 docs.append("**Required**")
 else:
 docs.append("*Optional*")
 docs.append("")

 return "\n".join(docs)


# LAYER 4: GRACEFUL DEGRADATION WITHOUT BUSINESS ASSUMPTIONS
# ==========================================================

class ConfigurationValueProvider:
 """Provide configuration values with graceful degradation"""

 def __init__(self, config: Dict[str, Any]):
 self.config = config
 self.schema = ConfigurationSchema()
 self.missing_config_log = []

 def get_value(self, key_path: str, value_type: Type = None) -> Any:
 """Get configuration value with schema-driven fallbacks"""

 # 1. Try to get from loaded configuration
 value = self._get_nested_value(self.config, key_path)
 if value is not None:
 return value

 # 2. Try to get from environment variables (user's runtime config)
 env_value = self._get_from_environment(key_path)
 if env_value is not None:
 return env_value

 # 3. Check if this field is required by schema
 field_name = key_path.split('.')[-1]
 if hasattr(self.schema, field_name):
 field_info = self.schema.__dataclass_fields__[field_name]
 if field_info.metadata.get('required', False):
 raise ConfigurationError(f"Required configuration missing: {key_path}")

 # 4. Log missing configuration for user awareness
 self.missing_config_log.append(key_path)

 # 5. Return schema-appropriate neutral value (NO BUSINESS ASSUMPTIONS)
 return self._get_schema_neutral_value(field_name, value_type)

 def _get_schema_neutral_value(self, field_name: str, value_type: Type) -> Any:
 """Get neutral value based on schema definition, not business assumptions"""

 if not hasattr(self.schema, field_name):
 # Unknown field - return type-appropriate neutral
 return self._get_type_neutral_value(value_type)

 field_info = self.schema.__dataclass_fields__[field_name]
 metadata = field_info.metadata

 # Use schema constraints to determine neutral value
 if 'options' in metadata:
 # For choice fields, return first option (most neutral)
 return metadata['options'][0]
 elif 'min' in metadata and 'max' in metadata:
 # For range fields, return midpoint
 return (metadata['min'] + metadata['max']) / 2
 elif field_info.type == bool:
 return False # Conservative default
 elif field_info.type == dict:
 return {}
 elif field_info.type == list:
 return []
 else:
 return self._get_type_neutral_value(field_info.type)

 def _get_type_neutral_value(self, value_type: Type) -> Any:
 """Get mathematically neutral value for unknown fields"""
 if value_type == float:
 return 0.5 # Mathematical neutral point
 elif value_type == int:
 return 1 # Minimal positive integer
 elif value_type == str:
 return 'unspecified'
 else:
 return None

 def get_missing_configuration_report(self) -> str:
 """Generate report of missing configuration for user"""
 if not self.missing_config_log:
 return "All configuration values provided by user."

 report = ["Missing Configuration Report:", ""]
 report.append("The following configuration values were not provided:")
 for key in set(self.missing_config_log):
 report.append(f" - {key}")
 report.append("")
 report.append("Using schema-appropriate neutral values.")
 report.append("Consider adding these to your configuration file for full control.")

 return "\n".join(report)


# INTEGRATION EXAMPLE
# ===================

class TrulyConfigurableAnalysisService:
 """Example of service using the hybrid configuration approach"""

 def __init__(self, config_dir: str = "config", environment: str = "development"):
 # Load external configuration
 self.config_manager = ExternalConfigurationManager(config_dir, environment)
 self.config = self.config_manager.load_configuration()

 # Set up value provider with graceful degradation
 self.value_provider = ConfigurationValueProvider(self.config)

 # Generate documentation for users
 self.config_docs = self.config_manager.get_configuration_documentation()

 def analyze_competitive_landscape(self, competitors, market_data=None):
 """Analyze competitive landscape using user's configuration"""

 # Get configuration values (no hardcoded assumptions anywhere)
 threshold = self.value_provider.get_value('market_threshold', float)
 weights = self.value_provider.get_value('intensity_weights', dict)
 limit = self.value_provider.get_value('competitor_limit', int)

 # Use configuration values in analysis
 filtered_competitors = competitors[:limit]

 # Analysis logic uses configuration values without interpreting their meaning
 analysis_result = {
 'analysis_id': f'analysis_{hash(str(self.config))}',
 'config_used': {
 'threshold': threshold,
 'weights': weights, 
 'limit': limit
 },
 'competitors_analyzed': len(filtered_competitors),
 'market_structure': self._analyze_structure(filtered_competitors, threshold),
 'configuration_report': self.value_provider.get_missing_configuration_report()
 }

 return analysis_result

 def get_configuration_documentation(self) -> str:
 """Provide users with configuration documentation"""
 return self.config_docs


# TESTING THE HYBRID APPROACH
# ============================

class TestHybridConfigurationApproach(unittest.TestCase):
 """Test the complete hybrid configuration system"""

 def test_external_config_loading(self):
 """Test loading actual external configuration files"""
 # Create test config file
 test_config = {
 'market_threshold': 0.12,
 'intensity_weights': {'market_share': 2.0, 'innovation': 1.5},
 'analysis_depth': 'comprehensive'
 }

 config_dir = 'test_config'
 os.makedirs(config_dir, exist_ok=True)

 config_file = os.path.join(config_dir, 'competitive_analysis.json')
 with open(config_file, 'w') as f:
 json.dump(test_config, f)

 try:
 # Service should use exactly the user's values
 service = TrulyConfigurableAnalysisService(config_dir)

 # Verify user's configuration is loaded exactly
 threshold = service.value_provider.get_value('market_threshold', float)
 self.assertEqual(threshold, 0.12) # User's exact value

 weights = service.value_provider.get_value('intensity_weights', dict)
 self.assertEqual(weights['market_share'], 2.0) # User's exact value

 finally:
 # Cleanup
 os.remove(config_file)
 os.rmdir(config_dir)

 @given(ConfigurationPropertyTesting.generate_valid_config_strategy())
 def test_property_based_validation(self, config):
 """Test service works with any schema-valid configuration"""
 # Service should work with any valid configuration
 service = TrulyConfigurableAnalysisService()
 service.config = config
 service.value_provider = ConfigurationValueProvider(config)

 result = service.analyze_competitive_landscape([
 {'competitor_id': 'test', 'market_share': 0.5}
 ])

 # Should always return valid structure
 self.assertIsInstance(result, dict)
 self.assertIn('analysis_id', result)

 # Should use user's exact configuration values
 self.assertEqual(result['config_used']['threshold'], config.get('market_threshold'))

 def test_graceful_degradation(self):
 """Test behavior when configuration is missing"""
 # Service with minimal configuration
 service = TrulyConfigurableAnalysisService()
 service.config = {} # No configuration provided
 service.value_provider = ConfigurationValueProvider({})

 result = service.analyze_competitive_landscape([
 {'competitor_id': 'test', 'market_share': 0.5}
 ])

 # Should still work and provide report of missing config
 self.assertIsInstance(result, dict)
 self.assertIn('configuration_report', result)
 self.assertIn('Missing Configuration Report', result['configuration_report'])


if __name__ == '__main__':
 # Example usage
 service = TrulyConfigurableAnalysisService()
 print("Configuration Documentation:")
 print(service.get_configuration_documentation())