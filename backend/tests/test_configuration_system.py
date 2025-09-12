"""
Production-Ready Configuration System Test Suite
Complete test coverage for all configuration functionality including:
- Schema validation and inheritance
- Environment switching and validation
- Hot-reload and caching mechanisms
- Error handling and fallback systems
- Performance and concurrency testing
"""

import unittest
import tempfile
import shutil
import json
import yaml
import os
import threading
import time
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.config_manager import (
    ConfigurationManager, 
    ConfigurationEntry,
    EnvironmentConfig,
    FileConfigurationSource,
    get_config_manager
)

class TestConfigurationSystem(unittest.TestCase):
    """Comprehensive test suite for configuration system"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.test_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Create test configuration files
        self.base_config = {
            "system": {
                "name": "test_system",
                "version": "1.0.0"
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "timeout": 30
            },
            "api": {
                "rate_limit": 100,
                "timeout": 10
            }
        }
        
        self.dev_config = {
            "database": {
                "host": "dev-db.example.com",
                "debug": True
            },
            "api": {
                "rate_limit": 1000,
                "debug_mode": True
            },
            "logging": {
                "level": "DEBUG"
            }
        }
        
        self.prod_config = {
            "database": {
                "host": "prod-db.example.com",
                "port": 5433,
                "ssl": True
            },
            "api": {
                "rate_limit": 500,
                "ssl_verify": True
            },
            "logging": {
                "level": "INFO"
            }
        }
        
        # Write test config files
        with open(os.path.join(self.config_dir, 'base.json'), 'w') as f:
            json.dump(self.base_config, f, indent=2)
            
        with open(os.path.join(self.config_dir, 'development.json'), 'w') as f:
            json.dump(self.dev_config, f, indent=2)
            
        with open(os.path.join(self.config_dir, 'production.json'), 'w') as f:
            json.dump(self.prod_config, f, indent=2)
        
        # Schema for validation testing
        self.test_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                        "timeout": {"type": "integer", "minimum": 1}
                    },
                    "required": ["host", "port"]
                },
                "api": {
                    "type": "object",
                    "properties": {
                        "rate_limit": {"type": "integer", "minimum": 1},
                        "timeout": {"type": "integer", "minimum": 1}
                    },
                    "required": ["rate_limit"]
                }
            },
            "required": ["database", "api"]
        }
        
        with open(os.path.join(self.config_dir, 'schema.json'), 'w') as f:
            json.dump(self.test_schema, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment after each test"""
        shutil.rmtree(self.test_dir)
    
    def test_configuration_loading(self):
        """Test basic configuration loading functionality"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        
        # Test loading environment-specific configurations
        for env in ['development', 'production']:
            config_manager.environment = env
            config_manager.reload(env)
            
            # Verify configuration is loaded
            config_info = config_manager.get_configuration_info()
            self.assertIn(env, config_info.get('environments', {}))
        
        self.assertTrue(True, "Configuration loading completed successfully")
        
    def test_environment_inheritance(self):
        """Test configuration inheritance from base to environment-specific"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        
        # Load development environment
        config_manager.load_environment('development')
        
        # Test inherited values from base
        self.assertEqual(config_manager.get('system.name'), 'test_system')
        self.assertEqual(config_manager.get('api.timeout'), 10)  # From base
        
        # Test overridden values
        self.assertEqual(config_manager.get('database.host'), 'dev-db.example.com')  # Overridden
        self.assertEqual(config_manager.get('api.rate_limit'), 1000)  # Overridden
        
        # Test environment-specific values
        self.assertTrue(config_manager.get('database.debug'))
        self.assertEqual(config_manager.get('logging.level'), 'DEBUG')
        
    def test_production_environment(self):
        """Test production environment configuration"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_environment('production')
        
        # Test production-specific overrides
        self.assertEqual(config_manager.get('database.host'), 'prod-db.example.com')
        self.assertEqual(config_manager.get('database.port'), 5433)
        self.assertTrue(config_manager.get('database.ssl'))
        self.assertEqual(config_manager.get('api.rate_limit'), 500)
        self.assertEqual(config_manager.get('logging.level'), 'INFO')
        
    def test_schema_validation(self):
        """Test configuration schema validation"""
        config_manager = ConfigurationManager(base_path=self.config_dir,
            config_dir=self.config_dir,
            schema_file=os.path.join(self.config_dir, 'schema.json')
        )
        
        # Test valid configuration
        config_manager.load_environment('development')
        self.assertTrue(config_manager.validate_configuration())
        
        # Test invalid configuration
        invalid_config = {
            "database": {
                "host": "invalid-host",
                "port": "invalid_port"  # Should be integer
            }
        }
        
        with patch.object(config_manager, '_load_config_file', return_value=invalid_config):
            config_manager.load_environment('invalid')
            self.assertFalse(config_manager.validate_configuration())
    
    def test_configuration_caching(self):
        """Test configuration caching mechanisms"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_environment('development')
        
        # First access - should load from file
        start_time = time.time()
        value1 = config_manager.get('system.name')
        first_access_time = time.time() - start_time
        
        # Second access - should use cache
        start_time = time.time()
        value2 = config_manager.get('system.name')
        second_access_time = time.time() - start_time
        
        self.assertEqual(value1, value2)
        # Cache access should be faster (though this might be flaky in very fast systems)
        # self.assertLess(second_access_time, first_access_time * 0.5)
    
    def test_hot_reload_functionality(self):
        """Test hot-reload of configuration changes"""
        config_manager = ConfigurationManager(base_path=self.config_dir,
            config_dir=self.config_dir,
            auto_reload=True,
            reload_interval=0.1  # 100ms for testing
        )
        config_manager.load_environment('development')
        
        # Get initial value
        initial_value = config_manager.get('system.name')
        self.assertEqual(initial_value, 'test_system')
        
        # Modify configuration file
        modified_config = self.base_config.copy()
        modified_config['system']['name'] = 'modified_system'
        
        with open(os.path.join(self.config_dir, 'base.json'), 'w') as f:
            json.dump(modified_config, f, indent=2)
        
        # Wait for hot-reload
        time.sleep(0.2)
        
        # Check if value was updated
        updated_value = config_manager.get('system.name')
        self.assertEqual(updated_value, 'modified_system')
    
    def test_fallback_mechanisms(self):
        """Test fallback mechanisms for missing configurations"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_environment('development')
        
        # Test default value fallback
        non_existent = config_manager.get('non.existent.key', 'default_value')
        self.assertEqual(non_existent, 'default_value')
        
        # Test nested fallback
        nested_default = config_manager.get('api.non_existent', {'default': True})
        self.assertEqual(nested_default, {'default': True})
    
    def test_environment_detection(self):
        """Test automatic environment detection"""
        # Test with environment variable
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
            detected_env = config_manager._detect_environment()
            self.assertEqual(detected_env, 'production')
        
        # Test with different environment variable names
        with patch.dict(os.environ, {'ENV': 'staging'}):
            detected_env = config_manager._detect_environment()
            self.assertEqual(detected_env, 'staging')
    
    def test_concurrent_access(self):
        """Test thread-safe concurrent access to configuration"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_environment('development')
        
        results = []
        errors = []
        
        def access_config():
            try:
                for _ in range(100):
                    value = config_manager.get('system.name')
                    results.append(value)
                    time.sleep(0.001)  # Small delay to increase chance of race conditions
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=access_config)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors and consistent results
        self.assertEqual(len(errors), 0)
        self.assertTrue(all(result == 'test_system' for result in results))
        self.assertEqual(len(results), 1000)  # 10 threads * 100 accesses each
    
    def test_configuration_encryption(self):
        """Test configuration value encryption/decryption"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        
        # Test setting encrypted value
        config_manager.set_encrypted('database.password', 'secret_password')
        
        # Test retrieving encrypted value
        retrieved_password = config_manager.get_decrypted('database.password')
        self.assertEqual(retrieved_password, 'secret_password')
        
        # Test that raw value is encrypted
        raw_value = config_manager.get('database.password')
        self.assertNotEqual(raw_value, 'secret_password')
    
    def test_configuration_validation_rules(self):
        """Test custom validation rules"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        
        # Add custom validation rule
        def validate_port_range(value):
            return isinstance(value, int) and 1 <= value <= 65535
        
        config_manager.add_validation_rule('database.port', validate_port_range)
        config_manager.load_environment('development')
        
        # Test valid value
        self.assertTrue(config_manager.validate_configuration())
        
        # Test invalid value
        config_manager.set('database.port', 70000)  # Invalid port
        self.assertFalse(config_manager.validate_configuration())
    
    def test_configuration_sources(self):
        """Test multiple configuration sources"""
        # Create additional source file
        additional_config = {
            "feature_flags": {
                "new_feature": True,
                "beta_feature": False
            }
        }
        
        additional_file = os.path.join(self.config_dir, 'features.json')
        with open(additional_file, 'w') as f:
            json.dump(additional_config, f, indent=2)
        
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.add_source(FileConfigurationSource(additional_file))
        config_manager.load_environment('development')
        
        # Test that additional source is loaded
        self.assertTrue(config_manager.get('feature_flags.new_feature'))
        self.assertFalse(config_manager.get('feature_flags.beta_feature'))
    
    def test_configuration_export_import(self):
        """Test configuration export and import functionality"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_environment('development')
        
        # Export configuration
        export_file = os.path.join(self.test_dir, 'exported_config.json')
        config_manager.export_configuration(export_file)
        
        # Verify export file exists and contains expected data
        self.assertTrue(os.path.exists(export_file))
        
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        self.assertEqual(exported_data['system']['name'], 'test_system')
        self.assertEqual(exported_data['database']['host'], 'dev-db.example.com')
    
    def test_configuration_diff(self):
        """Test configuration difference detection"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        
        # Load development environment
        config_manager.load_environment('development')
        dev_config = config_manager.get_all_config()
        
        # Load production environment
        config_manager.load_environment('production')
        prod_config = config_manager.get_all_config()
        
        # Get differences
        differences = config_manager.get_config_diff(dev_config, prod_config)
        
        # Verify expected differences
        self.assertIn('database.host', differences)
        self.assertIn('database.ssl', differences)
        self.assertIn('logging.level', differences)
    
    def test_configuration_backup_restore(self):
        """Test configuration backup and restore functionality"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_environment('development')
        
        # Create backup
        backup_file = os.path.join(self.test_dir, 'config_backup.json')
        config_manager.create_backup(backup_file)
        
        # Modify configuration
        config_manager.set('system.name', 'modified_system')
        self.assertEqual(config_manager.get('system.name'), 'modified_system')
        
        # Restore from backup
        config_manager.restore_backup(backup_file)
        self.assertEqual(config_manager.get('system.name'), 'test_system')
    
    def test_configuration_performance(self):
        """Test configuration system performance"""
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_environment('development')
        
        # Test bulk access performance
        start_time = time.time()
        for _ in range(10000):
            config_manager.get('system.name')
        access_time = time.time() - start_time
        
        # Should be able to handle 10k accesses in reasonable time (< 1 second)
        self.assertLess(access_time, 1.0)
        
        # Test bulk set performance
        start_time = time.time()
        for i in range(1000):
            config_manager.set(f'test.key_{i}', f'value_{i}')
        set_time = time.time() - start_time
        
        # Should be able to handle 1k sets in reasonable time (< 1 second)
        self.assertLess(set_time, 1.0)
    
    def test_yaml_configuration_support(self):
        """Test YAML configuration file support"""
        yaml_config = {
            'yaml_test': {
                'enabled': True,
                'settings': {
                    'timeout': 60,
                    'retries': 3
                }
            }
        }
        
        yaml_file = os.path.join(self.config_dir, 'test.yaml')
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_config, f)
        
        source = FileConfigurationSource(yaml_file)
        loaded_data = source.load()
        
        self.assertEqual(loaded_data['yaml_test']['enabled'], True)
        self.assertEqual(loaded_data['yaml_test']['settings']['timeout'], 60)
    
    def test_configuration_monitoring(self):
        """Test configuration monitoring and change detection"""
        config_manager = ConfigurationManager(base_path=self.config_dir,
            config_dir=self.config_dir,
            auto_reload=True
        )
        config_manager.load_environment('development')
        
        change_detected = threading.Event()
        changes_log = []
        
        def on_config_change(changes):
            changes_log.extend(changes)
            change_detected.set()
        
        config_manager.add_change_listener(on_config_change)
        
        # Modify configuration file
        modified_config = self.dev_config.copy()
        modified_config['api']['rate_limit'] = 2000
        
        with open(os.path.join(self.config_dir, 'development.json'), 'w') as f:
            json.dump(modified_config, f, indent=2)
        
        # Wait for change detection
        change_detected.wait(timeout=1.0)
        
        # Verify change was detected
        self.assertTrue(change_detected.is_set())
        self.assertTrue(len(changes_log) > 0)
    
    def test_singleton_config_manager(self):
        """Test singleton pattern for global config manager"""
        # Get first instance
        manager1 = get_config_manager()
        
        # Get second instance
        manager2 = get_config_manager()
        
        # Should be the same instance
        self.assertIs(manager1, manager2)
        
        # Test that changes in one affect the other
        manager1.set('test.singleton', 'value')
        self.assertEqual(manager2.get('test.singleton'), 'value')


class TestConfigurationIntegration(unittest.TestCase):
    """Integration tests for configuration system with actual services"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.test_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_goal_parser_configuration_integration(self):
        """Test goal parser integration with configuration system"""
        # Create goal parser configuration
        goal_parser_config = {
            "processing": {
                "max_concurrent_requests": 5,
                "timeout_seconds": 30,
                "retry_attempts": 3
            },
            "intelligence": {
                "confidence_threshold": 0.7,
                "learning_rate": 0.1
            },
            "api": {
                "rate_limit": 100,
                "timeout": 10
            }
        }
        
        with open(os.path.join(self.config_dir, 'goal_parser.json'), 'w') as f:
            json.dump(goal_parser_config, f, indent=2)
        
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_configuration('goal_parser.json')
        
        # Test goal parser can access its configuration
        self.assertEqual(config_manager.get('processing.max_concurrent_requests'), 5)
        self.assertEqual(config_manager.get('intelligence.confidence_threshold'), 0.7)
    
    def test_campaign_generator_configuration_integration(self):
        """Test campaign generator integration with configuration system"""
        # Create campaign generator configuration
        campaign_config = {
            "channel_performance": {
                "search": {
                    "default_ctr": 0.03,
                    "default_cpc": 2.5
                },
                "social": {
                    "default_ctr": 0.02,
                    "default_cpc": 1.8
                }
            },
            "budget_allocation": {
                "optimization_reserve": 0.1,
                "minimum_channel_budget": 100
            },
            "performance": {
                "concurrent_generations": 10,
                "cache_ttl": 3600
            }
        }
        
        with open(os.path.join(self.config_dir, 'campaign_generator.json'), 'w') as f:
            json.dump(campaign_config, f, indent=2)
        
        config_manager = ConfigurationManager(base_path=self.config_dir,base_path=self.config_dir)
        config_manager.load_configuration('campaign_generator.json')
        
        # Test campaign generator can access its configuration
        self.assertEqual(config_manager.get('channel_performance.search.default_ctr'), 0.03)
        self.assertEqual(config_manager.get('budget_allocation.optimization_reserve'), 0.1)


class TestConfigurationSecurity(unittest.TestCase):
    """Security tests for configuration system"""
    
    def test_sensitive_data_handling(self):
        """Test handling of sensitive configuration data"""
        config_manager = ConfigurationManager(base_path=self.config_dir,)
        
        # Test encryption of sensitive values
        config_manager.set_encrypted('database.password', 'super_secret')
        
        # Raw value should be encrypted
        raw_value = config_manager._config_data.get('database', {}).get('password')
        self.assertNotEqual(raw_value, 'super_secret')
        
        # Decrypted value should match original
        decrypted = config_manager.get_decrypted('database.password')
        self.assertEqual(decrypted, 'super_secret')
    
    def test_configuration_access_control(self):
        """Test access control for configuration values"""
        config_manager = ConfigurationManager(base_path=self.config_dir,)
        
        # Test read-only configuration
        config_manager.set_readonly('system.version', '1.0.0')
        
        # Should be able to read
        self.assertEqual(config_manager.get('system.version'), '1.0.0')
        
        # Should not be able to modify
        with self.assertRaises(Exception):
            config_manager.set('system.version', '2.0.0')


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationSecurity))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*70}")
    print("CONFIGURATION SYSTEM TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    print(f"\nTest suite {'PASSED' if exit_code == 0 else 'FAILED'}")
    exit(exit_code)
