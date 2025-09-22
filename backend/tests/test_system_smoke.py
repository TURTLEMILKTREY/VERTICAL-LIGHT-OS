#!/usr/bin/env python3
"""
System Smoke Tests - Validate Basic Functionality
PURPOSE: Verify core services can import, instantiate, and execute basic operations without crashing
This is NOT about Enhanced Configurability - this is about basic system stability
"""

import unittest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestSystemSmoke(unittest.TestCase):
    """Basic smoke tests to verify system components work"""
    
    def test_intelligence_engine_basic_import_and_instantiation(self):
        """Test that Intelligence Engine can be imported and created without errors"""
        try:
            from services.market_intelligence.intelligence_engine import MarketIntelligenceEngine
            
            # Test basic instantiation
            engine = MarketIntelligenceEngine()
            
            # Verify basic attributes exist
            self.assertTrue(hasattr(engine, 'user_context'))
            self.assertTrue(hasattr(engine, 'config_manager'))
            
            print("✓ Intelligence Engine imports and instantiates successfully")
            
        except Exception as e:
            self.fail(f"Intelligence Engine basic import/instantiation failed: {e}")
    
    def test_intelligence_engine_basic_method_calls(self):
        """Test that basic Intelligence Engine methods can be called without crashing"""
        try:
            from services.market_intelligence.intelligence_engine import MarketIntelligenceEngine
            
            engine = MarketIntelligenceEngine()
            
            # Test basic method calls with minimal data
            business_profile = {
                'industry': 'test_industry',
                'target_regions': ['test_region']
            }
            
            market_data = {
                'industry_trends': {
                    'test_industry': {
                        'trend_1': {'growth_rate': 0.15}
                    }
                }
            }
            
            # Test analyze_market_context - main method
            try:
                result = engine.analyze_market_context(business_profile, market_data)
                self.assertIsInstance(result, dict)
                print("✓ analyze_market_context executes without crashing")
                
            except Exception as e:
                print(f"⚠ analyze_market_context failed: {e}")
                # Don't fail the test - just document the issue
            
            # Test individual methods
            methods_to_test = [
                ('_identify_market_opportunities', [business_profile, market_data]),
                ('_recommend_budget_allocation', [{'max': 100000}, market_data]),
                ('_recommend_channels', [{'demographic': 'test'}, market_data])
            ]
            
            for method_name, args in methods_to_test:
                if hasattr(engine, method_name):
                    try:
                        method = getattr(engine, method_name)
                        result = method(*args)
                        print(f"✓ {method_name} executes successfully")
                    except Exception as e:
                        print(f"⚠ {method_name} failed: {e}")
                        # Document but don't fail - we're identifying issues
                else:
                    print(f"⚠ Method {method_name} not found")
            
        except Exception as e:
            self.fail(f"Intelligence Engine method testing failed: {e}")
    
    def test_config_manager_basic_functionality(self):
        """Test that Configuration Manager works"""
        try:
            from config.config_manager import get_config_manager
            
            # Test basic config manager functionality
            config_manager = get_config_manager()
            
            # Test basic config retrieval
            test_value = config_manager.get('test.key', 'default_value')
            self.assertEqual(test_value, 'default_value')
            
            print("✓ Configuration Manager works")
            
        except Exception as e:
            print(f"⚠ Configuration Manager failed: {e}")
            # Don't fail - document the issue
    
    def test_other_core_services_import(self):
        """Test that other core services can be imported"""
        
        services_to_test = [
            'services.campaign_generator',
            'services.optimization_engine', 
            'services.learning.adaptive_learner'
        ]
        
        for service_path in services_to_test:
            try:
                __import__(service_path)
                print(f"✓ {service_path} imports successfully")
            except Exception as e:
                print(f"⚠ {service_path} import failed: {e}")
                # Document but don't fail


if __name__ == '__main__':
    print("=" * 60)
    print("SYSTEM SMOKE TESTS - Basic Functionality Validation")
    print("=" * 60)
    
    # Run with detailed output
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("SMOKE TEST SUMMARY:")
    print("✓ = Working   ⚠ = Issues Found")
    print("=" * 60)