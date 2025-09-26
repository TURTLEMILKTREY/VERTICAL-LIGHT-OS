"""
Configuration Schema Validator and Documentation Generator
Validates all configuration schemas and generates comprehensive documentation
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import jsonschema
from jsonschema import validate, ValidationError, Draft202012Validator

class ConfigurationSchemaValidator:
 """Validates configuration schemas and generates documentation"""

 def __init__(self, config_dir: str):
 self.config_dir = Path(config_dir)
 self.schemas_dir = self.config_dir / 'schemas'
 self.environments_dir = self.config_dir / 'environments'
 self.validation_results = []

 def validate_all_schemas(self) -> Dict[str, Any]:
 """Validate all configuration schemas and files"""
 results = {
 'schema_validation': [],
 'config_validation': [],
 'inheritance_validation': [],
 'overall_status': 'unknown'
 }

 # Validate schema files themselves
 schema_results = self._validate_schema_files()
 results['schema_validation'] = schema_results

 # Validate configuration files against schemas
 config_results = self._validate_config_files()
 results['config_validation'] = config_results

 # Validate inheritance chains
 inheritance_results = self._validate_inheritance()
 results['inheritance_validation'] = inheritance_results

 # Determine overall status
 all_passed = (
 all(r['valid'] for r in schema_results) and
 all(r['valid'] for r in config_results) and
 all(r['valid'] for r in inheritance_results)
 )
 results['overall_status'] = 'PASSED' if all_passed else 'FAILED'

 return results

 def _validate_schema_files(self) -> List[Dict[str, Any]]:
 """Validate schema files are valid JSON Schema documents"""
 results = []

 if not self.schemas_dir.exists():
 return [{'file': 'schemas directory', 'valid': False, 'error': 'Schemas directory not found'}]

 schema_files = list(self.schemas_dir.glob('*.json'))

 for schema_file in schema_files:
 result = {
 'file': schema_file.name,
 'valid': False,
 'error': None,
 'warnings': []
 }

 try:
 with open(schema_file, 'r') as f:
 schema_content = json.load(f)

 # Validate it's a valid JSON Schema
 Draft202012Validator.check_schema(schema_content)

 # Additional checks
 warnings = self._check_schema_quality(schema_content, schema_file.name)
 result['warnings'] = warnings
 result['valid'] = True

 except json.JSONDecodeError as e:
 result['error'] = f'Invalid JSON: {e}'
 except jsonschema.SchemaError as e:
 result['error'] = f'Invalid JSON Schema: {e}'
 except Exception as e:
 result['error'] = f'Unexpected error: {e}'

 results.append(result)

 return results

 def _check_schema_quality(self, schema: Dict[str, Any], filename: str) -> List[str]:
 """Check schema quality and best practices"""
 warnings = []

 # Check for required fields
 if 'title' not in schema:
 warnings.append('Missing title field')
 if 'description' not in schema:
 warnings.append('Missing description field')
 if '$schema' not in schema:
 warnings.append('Missing $schema field')

 # Check for default values
 if 'properties' in schema:
 self._check_defaults_recursive(schema['properties'], '', warnings)

 # Check for validation constraints
 if 'properties' in schema:
 self._check_validation_constraints(schema['properties'], '', warnings)

 return warnings

 def _check_defaults_recursive(self, properties: Dict[str, Any], path: str, warnings: List[str]):
 """Recursively check for default values in schema properties"""
 for prop_name, prop_def in properties.items():
 current_path = f"{path}.{prop_name}" if path else prop_name

 if isinstance(prop_def, dict):
 if prop_def.get('type') in ['string', 'number', 'integer', 'boolean']:
 if 'default' not in prop_def:
 warnings.append(f'Property {current_path} missing default value')

 if 'properties' in prop_def:
 self._check_defaults_recursive(prop_def['properties'], current_path, warnings)

 def _check_validation_constraints(self, properties: Dict[str, Any], path: str, warnings: List[str]):
 """Check for appropriate validation constraints"""
 for prop_name, prop_def in properties.items():
 current_path = f"{path}.{prop_name}" if path else prop_name

 if isinstance(prop_def, dict):
 prop_type = prop_def.get('type')

 if prop_type == 'integer':
 if 'minimum' not in prop_def and 'maximum' not in prop_def:
 warnings.append(f'Integer property {current_path} should have min/max constraints')

 if prop_type == 'string':
 if 'minLength' not in prop_def and 'pattern' not in prop_def:
 warnings.append(f'String property {current_path} should have length or pattern constraints')

 if 'properties' in prop_def:
 self._check_validation_constraints(prop_def['properties'], current_path, warnings)

 def _validate_config_files(self) -> List[Dict[str, Any]]:
 """Validate configuration files against their schemas"""
 results = []

 # Map of config files to their schemas
 config_schema_map = {
 'goal_parser.json': 'goal_parser_enhanced.json',
 'hospital_consulting_config.json': None, # Hospital config doesn't have a specific schema yet
 'base.json': None, # Base config doesn't have a specific schema
 }

 # Check environment configs
 if self.environments_dir.exists():
 for env_file in self.environments_dir.glob('*.json'):
 config_schema_map[f'environments/{env_file.name}'] = None

 for config_file, schema_file in config_schema_map.items():
 if schema_file is None:
 continue # Skip files without schemas

 config_path = self.config_dir / config_file
 schema_path = self.schemas_dir / schema_file

 result = {
 'config_file': config_file,
 'schema_file': schema_file,
 'valid': False,
 'error': None,
 'details': []
 }

 try:
 if not config_path.exists():
 result['error'] = f'Configuration file {config_file} not found'
 results.append(result)
 continue

 if not schema_path.exists():
 result['error'] = f'Schema file {schema_file} not found'
 results.append(result)
 continue

 with open(config_path, 'r') as f:
 config_data = json.load(f)

 with open(schema_path, 'r') as f:
 schema_data = json.load(f)

 # Validate configuration against schema
 validate(instance=config_data, schema=schema_data)
 result['valid'] = True
 result['details'].append('Configuration validates against schema')

 except json.JSONDecodeError as e:
 result['error'] = f'Invalid JSON in config file: {e}'
 except ValidationError as e:
 result['error'] = f'Validation error: {e.message}'
 result['details'].append(f'Failed at path: {".".join(str(p) for p in e.absolute_path)}')
 except Exception as e:
 result['error'] = f'Unexpected error: {e}'

 results.append(result)

 return results

 def _validate_inheritance(self) -> List[Dict[str, Any]]:
 """Validate configuration inheritance works correctly"""
 results = []

 if not self.environments_dir.exists():
 return [{'test': 'inheritance', 'valid': False, 'error': 'Environments directory not found'}]

 # Load base configuration
 base_path = self.config_dir / 'base.json'
 if not base_path.exists():
 return [{'test': 'inheritance', 'valid': False, 'error': 'Base configuration not found'}]

 try:
 with open(base_path, 'r') as f:
 base_config = json.load(f)
 except Exception as e:
 return [{'test': 'inheritance', 'valid': False, 'error': f'Cannot load base config: {e}'}]

 # Test each environment
 for env_file in self.environments_dir.glob('*.json'):
 env_name = env_file.stem
 result = {
 'environment': env_name,
 'valid': False,
 'error': None,
 'inherited_keys': [],
 'overridden_keys': [],
 'new_keys': []
 }

 try:
 with open(env_file, 'r') as f:
 env_config = json.load(f)

 # Simulate inheritance merge
 merged_config = self._merge_configs(base_config, env_config)

 # Analyze inheritance
 self._analyze_inheritance(base_config, env_config, merged_config, result)

 result['valid'] = True

 except Exception as e:
 result['error'] = f'Error processing environment {env_name}: {e}'

 results.append(result)

 return results

 def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
 """Merge configuration dictionaries with override precedence"""
 merged = base.copy()

 for key, value in override.items():
 if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
 merged[key] = self._merge_configs(merged[key], value)
 else:
 merged[key] = value

 return merged

 def _analyze_inheritance(self, base: Dict[str, Any], env: Dict[str, Any], 
 merged: Dict[str, Any], result: Dict[str, Any]):
 """Analyze inheritance patterns between base and environment configs"""
 self._analyze_inheritance_recursive(base, env, merged, result, '')

 def _analyze_inheritance_recursive(self, base: Dict[str, Any], env: Dict[str, Any], 
 merged: Dict[str, Any], result: Dict[str, Any], path: str):
 """Recursively analyze inheritance patterns"""
 # Check base keys
 for key, value in base.items():
 current_path = f"{path}.{key}" if path else key

 if key not in env:
 result['inherited_keys'].append(current_path)
 elif isinstance(value, dict) and isinstance(env.get(key), dict):
 self._analyze_inheritance_recursive(value, env[key], merged[key], result, current_path)
 else:
 result['overridden_keys'].append(current_path)

 # Check environment-specific keys
 for key in env:
 current_path = f"{path}.{key}" if path else key
 if key not in base:
 result['new_keys'].append(current_path)

 def generate_validation_report(self, results: Dict[str, Any]) -> str:
 """Generate a comprehensive validation report"""
 report = []
 report.append("=" * 80)
 report.append("CONFIGURATION SYSTEM VALIDATION REPORT")
 report.append("=" * 80)
 report.append(f"Generated: {os.path.basename(__file__)} at {Path.cwd()}")
 report.append(f"Overall Status: {results['overall_status']}")
 report.append("")

 # Schema validation results
 report.append("SCHEMA VALIDATION")
 report.append("-" * 40)
 for result in results['schema_validation']:
 status = "PASS" if result['valid'] else "ERROR: FAIL"
 report.append(f"{status} {result['file']}")
 if result.get('error'):
 report.append(f" Error: {result['error']}")
 if result.get('warnings'):
 for warning in result['warnings']:
 report.append(f" Warning: {warning}")
 report.append("")

 # Configuration validation results
 report.append("CONFIGURATION VALIDATION")
 report.append("-" * 40)
 for result in results['config_validation']:
 status = "PASS" if result['valid'] else "ERROR: FAIL"
 report.append(f"{status} {result['config_file']} -> {result['schema_file']}")
 if result.get('error'):
 report.append(f" Error: {result['error']}")
 for detail in result.get('details', []):
 report.append(f" Detail: {detail}")
 report.append("")

 # Inheritance validation results
 report.append("INHERITANCE VALIDATION")
 report.append("-" * 40)
 for result in results['inheritance_validation']:
 status = "PASS" if result['valid'] else "ERROR: FAIL"
 env_name = result.get('environment', 'unknown')
 report.append(f"{status} Environment: {env_name}")
 if result.get('error'):
 report.append(f" Error: {result['error']}")
 else:
 if result.get('inherited_keys'):
 report.append(f" Inherited: {len(result['inherited_keys'])} keys")
 if result.get('overridden_keys'):
 report.append(f" Overridden: {len(result['overridden_keys'])} keys")
 if result.get('new_keys'):
 report.append(f" New: {len(result['new_keys'])} keys")

 report.append("")
 report.append("=" * 80)

 return "\n".join(report)


def main():
 """Main validation function"""
 if len(sys.argv) > 1:
 config_dir = sys.argv[1]
 else:
 # Default to backend/config directory
 config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')

 if not os.path.exists(config_dir):
 print(f"Configuration directory not found: {config_dir}")
 sys.exit(1)

 print(f"Validating configuration system at: {config_dir}")
 print("=" * 60)

 validator = ConfigurationSchemaValidator(config_dir)
 results = validator.validate_all_schemas()

 report = validator.generate_validation_report(results)
 print(report)

 # Save report to file
 report_file = os.path.join(config_dir, 'validation_report.txt')
 with open(report_file, 'w') as f:
 f.write(report)

 print(f"\nValidation report saved to: {report_file}")

 # Exit with appropriate code
 exit_code = 0 if results['overall_status'] == 'PASSED' else 1
 sys.exit(exit_code)


if __name__ == '__main__':
 main()
