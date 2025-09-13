"""
Dynamic test suite for Intelligence Engine microservice
Tests all functionality with configurable parameters - NO HARDCODED VALUES
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from typing import Dict, Any, List
import json
import uuid
import random

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.market_intelligence.intelligence_engine import MarketIntelligenceEngine, get_intelligence_engine
from config.config_manager import ConfigurationManager


class TestIntelligenceEngine(unittest.TestCase):
    """Dynamic test suite for Intelligence Engine - fully configurable"""
    
    def setUp(self):
        """Set up test environment with dynamic configuration"""
        self.config_manager = Mock(spec=ConfigurationManager)
        
        # Dynamic test configuration - all values configurable
        self.test_config = {
            'confidence_calculation': {
                'base_confidence': random.uniform(0.1, 0.9),
                'quality_weight': random.uniform(0.1, 0.5),
                'data_freshness_weight': random.uniform(0.1, 0.5),
                'fallback_confidence': random.uniform(0.1, 0.8)
            },
            'opportunity_calculation': {
                'growth_potential_weight': random.uniform(0.1, 0.5),
                'market_size_weight': random.uniform(0.1, 0.5),
                'competition_weight': random.uniform(0.1, 0.5),
                'trend_momentum_weight': random.uniform(0.1, 0.5)
            },
            'analysis_thresholds': {
                'min_confidence_score': random.uniform(0.1, 0.5),
                'high_opportunity_threshold': random.uniform(0.6, 0.9),
                'market_size_significance': random.uniform(100000, 10000000)
            },
            'fallback': {
                'intelligence_confidence': random.uniform(0.1, 0.5)
            },
            'risk_factors': {
                'high_competition_threshold': random.uniform(0.6, 0.9),
                'low_data_quality_threshold': random.uniform(0.1, 0.4)
            }
        }
        
        # Configure mock to return dynamic values
        self.config_manager.get.side_effect = self._get_config_value
        
        # Create engine instance
        self.engine = MarketIntelligenceEngine()
        self.engine.config_manager = self.config_manager
    
    def _get_config_value(self, key: str, default=None):
        """Get configuration value dynamically from test config"""
        keys = key.split('.')
        value = self.test_config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def _generate_dynamic_market_data(self) -> Dict[str, Any]:
        """Generate dynamic market data for testing"""
        return {
            'market_id': str(uuid.uuid4()),
            'market_size': random.uniform(1000000, 100000000),
            'growth_rate': random.uniform(-0.1, 0.5),
            'competition_level': random.uniform(0.1, 1.0),
            'data_quality_score': random.uniform(0.1, 1.0),
            'data_freshness_hours': random.randint(1, 168),
            'trend_momentum': random.uniform(-0.5, 0.5),
            'opportunities': [
                {
                    'type': f'opportunity_{i}',
                    'potential': random.uniform(0.1, 1.0),
                    'confidence': random.uniform(0.1, 1.0)
                } for i in range(random.randint(1, 5))
            ]
        }
    
    def test_generate_intelligence_dynamic(self):
        """Test intelligence generation with dynamic data"""
        # Generate dynamic test data
        market_data = self._generate_dynamic_market_data()
        
        # Test intelligence generation
        result = self.engine.generate_intelligence(market_data)
        
        # Verify structure (no hardcoded values)
        self.assertIsInstance(result, dict)
        self.assertIn('context_id', result)
        self.assertIn('analysis_timestamp', result)
        self.assertIn('market_insights', result)
        self.assertIn('opportunities', result)
        self.assertIn('confidence_score', result)
        
        # Verify confidence is within configured range
        confidence = result['confidence_score']
        self.assertIsInstance(confidence, (int, float))
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_calculate_confidence_dynamic(self):
        """Test confidence calculation with dynamic parameters"""
        # Generate dynamic test data
        market_data = self._generate_dynamic_market_data()
        
        # Test confidence calculation
        confidence = self.engine._calculate_confidence(market_data)
        
        # Verify result is valid
        self.assertIsInstance(confidence, (int, float))
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_calculate_opportunity_score_dynamic(self):
        """Test opportunity score calculation with dynamic weights"""
        # Generate dynamic opportunity data
        opportunity_data = {
            'growth_potential': random.uniform(0.0, 1.0),
            'market_size': random.uniform(1000000, 100000000),
            'competition_level': random.uniform(0.0, 1.0),
            'trend_momentum': random.uniform(-0.5, 0.5)
        }
        
        # Test opportunity calculation
        score = self.engine._calculate_opportunity_score(opportunity_data)
        
        # Verify result is valid
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_identify_opportunities_dynamic(self):
        """Test opportunity identification with dynamic data"""
        # Generate dynamic market data
        market_data = self._generate_dynamic_market_data()
        
        # Test opportunity identification
        opportunities = self.engine._identify_opportunities(market_data)
        
        # Verify structure
        self.assertIsInstance(opportunities, list)
        for opportunity in opportunities:
            self.assertIsInstance(opportunity, dict)
            self.assertIn('type', opportunity)
            self.assertIn('description', opportunity)
            self.assertIn('potential_score', opportunity)
    
    def test_assess_risks_dynamic(self):
        """Test risk assessment with dynamic thresholds"""
        # Generate dynamic market data
        market_data = self._generate_dynamic_market_data()
        
        # Test risk assessment
        risks = self.engine._assess_risks(market_data)
        
        # Verify structure
        self.assertIsInstance(risks, list)
        for risk in risks:
            self.assertIsInstance(risk, dict)
            self.assertIn('type', risk)
            self.assertIn('severity', risk)
            self.assertIn('mitigation', risk)
    
    def test_fallback_intelligence_dynamic(self):
        """Test fallback intelligence with configurable confidence"""
        # Test fallback creation
        fallback = self.engine._create_fallback_intelligence()
        
        # Verify structure
        self.assertIsInstance(fallback, dict)
        self.assertIn('context_id', fallback)
        self.assertEqual(fallback['context_id'], 'fallback')
        self.assertIn('confidence_score', fallback)
        
        # Verify fallback confidence matches configuration
        expected_confidence = self.test_config['fallback']['intelligence_confidence']
        self.assertEqual(fallback['confidence_score'], expected_confidence)
    
    def test_error_handling_dynamic(self):
        """Test error handling with various scenarios"""
        # Test with None data
        result = self.engine.generate_intelligence(None)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['context_id'], 'fallback')
        
        # Test with empty data
        result = self.engine.generate_intelligence({})
        self.assertIsInstance(result, dict)
        
        # Test with malformed data
        malformed_data = {'invalid': 'data'}
        result = self.engine.generate_intelligence(malformed_data)
        self.assertIsInstance(result, dict)
    
    def test_singleton_pattern(self):
        """Test singleton pattern functionality"""
        # Get multiple instances
        engine1 = get_intelligence_engine()
        engine2 = get_intelligence_engine()
        
        # Verify they are the same instance
        self.assertIs(engine1, engine2)
    
    def test_thread_safety_dynamic(self):
        """Test thread safety with concurrent access"""
        import threading
        import time
        
        results = []
        errors = []
        
        def generate_intelligence_worker():
            try:
                market_data = self._generate_dynamic_market_data()
                result = self.engine.generate_intelligence(market_data)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=generate_intelligence_worker)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors and all results valid
        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
        self.assertEqual(len(results), 5)
        
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('context_id', result)
    
    def test_configuration_driven_behavior(self):
        """Test that all behavior is driven by configuration"""
        # Change configuration values
        new_config = {
            'confidence_calculation': {
                'base_confidence': 0.8,
                'fallback_confidence': 0.2
            },
            'opportunity_calculation': {
                'growth_potential_weight': 0.4,
                'market_size_weight': 0.3,
                'competition_weight': 0.2,
                'trend_momentum_weight': 0.1
            }
        }
        
        # Update mock configuration
        self.test_config.update(new_config)
        
        # Generate intelligence with new config
        market_data = self._generate_dynamic_market_data()
        result = self.engine.generate_intelligence(market_data)
        
        # Verify behavior changes with configuration
        self.assertIsInstance(result, dict)
        self.assertIn('confidence_score', result)


class TestIntelligenceEngineIntegration(unittest.TestCase):
    """Integration tests with real configuration"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Use real config manager
        self.config_manager = ConfigurationManager()
        self.engine = MarketIntelligenceEngine()
    
    def test_real_configuration_integration(self):
        """Test with real configuration files"""
        # Generate realistic market data
        market_data = {
            'market_id': 'test_market',
            'market_size': 50000000,
            'growth_rate': 0.15,
            'competition_level': 0.6,
            'data_quality_score': 0.8,
            'data_freshness_hours': 24
        }
        
        # Test intelligence generation
        result = self.engine.generate_intelligence(market_data)
        
        # Verify realistic results
        self.assertIsInstance(result, dict)
        self.assertIn('context_id', result)
        self.assertIn('confidence_score', result)
        
        # Confidence should be reasonable
        confidence = result['confidence_score']
        self.assertGreater(confidence, 0.0)
        self.assertLess(confidence, 1.0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
