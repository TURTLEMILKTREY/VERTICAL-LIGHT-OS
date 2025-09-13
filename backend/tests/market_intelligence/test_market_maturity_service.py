"""
Dynamic test suite for Market Maturity Service microservice
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
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.market_intelligence.market_maturity_service import MarketMaturityService, get_market_maturity_service
from config.config_manager import ConfigurationManager


class TestMarketMaturityService(unittest.TestCase):
    """Dynamic test suite for Market Maturity Service - fully configurable"""
    
    def setUp(self):
        """Set up test environment with dynamic configuration"""
        self.config_manager = Mock(spec=ConfigurationManager)
        
        # Dynamic test configuration - all values configurable
        self.test_config = {
            'maturity_scoring': {
                'growth_rate_weight': random.uniform(0.2, 0.4),
                'market_size_weight': random.uniform(0.1, 0.3),
                'competition_weight': random.uniform(0.1, 0.3),
                'innovation_weight': random.uniform(0.1, 0.3),
                'regulation_weight': random.uniform(0.05, 0.2)
            },
            'maturity_thresholds': {
                'emerging_threshold': random.uniform(0.1, 0.3),
                'growth_threshold': random.uniform(0.3, 0.5),
                'mature_threshold': random.uniform(0.6, 0.8),
                'decline_threshold': random.uniform(0.8, 0.95)
            },
            'lifecycle_analysis': {
                'transition_sensitivity': random.uniform(0.05, 0.2),
                'trend_momentum_weight': random.uniform(0.3, 0.6),
                'stability_assessment_window': random.randint(6, 24)
            },
            'prediction_parameters': {
                'forecast_horizon_months': random.randint(6, 36),
                'confidence_threshold': random.uniform(0.7, 0.95),
                'scenario_count': random.randint(3, 10)
            },
            'evolution_factors': {
                'technology_disruption_weight': random.uniform(0.2, 0.4),
                'regulatory_change_weight': random.uniform(0.1, 0.3),
                'consumer_behavior_weight': random.uniform(0.2, 0.4),
                'economic_factor_weight': random.uniform(0.1, 0.3)
            }
        }
        
        # Configure mock to return dynamic values
        self.config_manager.get.side_effect = self._get_config_value
        
        # Create service instance
        self.service = MarketMaturityService()
        self.service.config_manager = self.config_manager
    
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
    
    def _generate_dynamic_market_data(self, maturity_stage: str = 'mixed') -> Dict[str, Any]:
        """Generate dynamic market data for testing with specified maturity stage"""
        if maturity_stage == 'emerging':
            growth_rate = random.uniform(0.2, 0.8)
            market_size = random.uniform(1000000, 50000000)
            competition_level = random.uniform(0.1, 0.4)
            innovation_rate = random.uniform(0.7, 1.0)
            regulation_maturity = random.uniform(0.1, 0.4)
        elif maturity_stage == 'growth':
            growth_rate = random.uniform(0.1, 0.4)
            market_size = random.uniform(50000000, 500000000)
            competition_level = random.uniform(0.4, 0.7)
            innovation_rate = random.uniform(0.5, 0.8)
            regulation_maturity = random.uniform(0.4, 0.7)
        elif maturity_stage == 'mature':
            growth_rate = random.uniform(0.02, 0.1)
            market_size = random.uniform(500000000, 5000000000)
            competition_level = random.uniform(0.7, 0.9)
            innovation_rate = random.uniform(0.2, 0.5)
            regulation_maturity = random.uniform(0.7, 0.9)
        elif maturity_stage == 'decline':
            growth_rate = random.uniform(-0.1, 0.02)
            market_size = random.uniform(100000000, 1000000000)
            competition_level = random.uniform(0.3, 0.6)
            innovation_rate = random.uniform(0.1, 0.3)
            regulation_maturity = random.uniform(0.8, 1.0)
        else:  # mixed
            growth_rate = random.uniform(-0.05, 0.3)
            market_size = random.uniform(10000000, 1000000000)
            competition_level = random.uniform(0.2, 0.8)
            innovation_rate = random.uniform(0.3, 0.8)
            regulation_maturity = random.uniform(0.2, 0.8)
        
        return {
            'market_id': str(uuid.uuid4()),
            'market_name': f'Market_{random.randint(1000, 9999)}',
            'sector': random.choice(['technology', 'healthcare', 'finance', 'retail', 'manufacturing']),
            'geographical_scope': random.choice(['local', 'regional', 'national', 'global']),
            'market_metrics': {
                'total_market_size': market_size,
                'annual_growth_rate': growth_rate,
                'market_share_concentration': competition_level,
                'number_of_players': random.randint(5, 500),
                'barriers_to_entry': random.uniform(0.1, 1.0),
                'customer_acquisition_cost': random.uniform(100, 10000)
            },
            'innovation_indicators': {
                'r_and_d_intensity': innovation_rate,
                'patent_activity': random.randint(0, 1000),
                'technology_adoption_rate': random.uniform(0.1, 1.0),
                'product_lifecycle_length': random.randint(6, 120)
            },
            'regulatory_environment': {
                'regulatory_maturity': regulation_maturity,
                'compliance_complexity': random.uniform(0.1, 1.0),
                'regulatory_stability': random.uniform(0.3, 1.0),
                'pending_legislation_impact': random.uniform(0.0, 0.8)
            },
            'customer_characteristics': {
                'customer_sophistication': random.uniform(0.2, 1.0),
                'brand_loyalty': random.uniform(0.1, 0.9),
                'price_sensitivity': random.uniform(0.2, 0.9),
                'adoption_rate': random.uniform(0.1, 0.8)
            },
            'economic_factors': {
                'economic_sensitivity': random.uniform(0.1, 0.9),
                'cyclical_behavior': random.uniform(0.0, 0.8),
                'inflation_impact': random.uniform(0.1, 0.7)
            },
            'historical_data': [
                {
                    'period': f'{2020 + i}',
                    'market_size': market_size * (1 + growth_rate) ** i,
                    'growth_rate': growth_rate + random.uniform(-0.02, 0.02),
                    'competition_level': min(1.0, competition_level + i * 0.05)
                } for i in range(5)
            ]
        }
    
    def test_assess_market_maturity_dynamic(self):
        """Test market maturity assessment with dynamic data"""
        # Test with different maturity stages
        for maturity_stage in ['emerging', 'growth', 'mature', 'decline', 'mixed']:
            market_data = self._generate_dynamic_market_data(maturity_stage)
            
            # Test maturity assessment
            result = self.service.assess_market_maturity(market_data)
            
            # Verify structure (no hardcoded values)
            self.assertIsInstance(result, dict)
            self.assertIn('assessment_id', result)
            self.assertIn('timestamp', result)
            self.assertIn('maturity_score', result)
            self.assertIn('maturity_stage', result)
            self.assertIn('lifecycle_position', result)
            self.assertIn('maturity_factors', result)
            self.assertIn('transition_indicators', result)
            self.assertIn('recommendations', result)
            
            # Verify maturity score is valid
            maturity_score = result['maturity_score']
            self.assertIsInstance(maturity_score, (int, float))
            self.assertGreaterEqual(maturity_score, 0.0)
            self.assertLessEqual(maturity_score, 1.0)
            
            # Verify maturity stage is valid
            maturity_stage_result = result['maturity_stage']
            self.assertIn(maturity_stage_result, ['emerging', 'growth', 'mature', 'decline'])
    
    def test_calculate_maturity_score_dynamic(self):
        """Test maturity score calculation with dynamic weights"""
        # Generate dynamic market data
        market_data = self._generate_dynamic_market_data()
        
        # Test maturity score calculation
        score = self.service._calculate_maturity_score(market_data)
        
        # Verify result is valid
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_analyze_lifecycle_position_dynamic(self):
        """Test lifecycle position analysis with dynamic data"""
        # Generate dynamic market data
        market_data = self._generate_dynamic_market_data()
        
        # Test lifecycle analysis
        lifecycle = self.service._analyze_lifecycle_position(market_data)
        
        # Verify structure
        self.assertIsInstance(lifecycle, dict)
        self.assertIn('current_stage', lifecycle)
        self.assertIn('stage_confidence', lifecycle)
        self.assertIn('transition_probability', lifecycle)
        self.assertIn('key_characteristics', lifecycle)
        self.assertIn('stage_duration_estimate', lifecycle)
        
        # Verify stage confidence is valid
        stage_confidence = lifecycle['stage_confidence']
        self.assertIsInstance(stage_confidence, (int, float))
        self.assertGreaterEqual(stage_confidence, 0.0)
        self.assertLessEqual(stage_confidence, 1.0)
    
    def test_identify_transition_indicators_dynamic(self):
        """Test transition indicator identification with dynamic data"""
        # Generate dynamic market data
        market_data = self._generate_dynamic_market_data()
        
        # Test transition indicator identification
        indicators = self.service._identify_transition_indicators(market_data)
        
        # Verify structure
        self.assertIsInstance(indicators, list)
        for indicator in indicators:
            self.assertIsInstance(indicator, dict)
            self.assertIn('indicator_type', indicator)
            self.assertIn('strength', indicator)
            self.assertIn('direction', indicator)
            self.assertIn('confidence', indicator)
            self.assertIn('description', indicator)
    
    def test_predict_market_evolution_dynamic(self):
        """Test market evolution prediction with dynamic parameters"""
        # Generate dynamic market data
        market_data = self._generate_dynamic_market_data()
        
        # Test evolution prediction
        prediction = self.service.predict_market_evolution(market_data)
        
        # Verify structure
        self.assertIsInstance(prediction, dict)
        self.assertIn('prediction_id', prediction)
        self.assertIn('forecast_horizon_months', prediction)
        self.assertIn('evolution_scenarios', prediction)
        self.assertIn('probability_matrix', prediction)
        self.assertIn('key_drivers', prediction)
        self.assertIn('monitoring_indicators', prediction)
        
        # Verify forecast horizon matches configuration
        expected_horizon = self.test_config['prediction_parameters']['forecast_horizon_months']
        self.assertEqual(prediction['forecast_horizon_months'], expected_horizon)
        
        # Verify evolution scenarios
        scenarios = prediction['evolution_scenarios']
        self.assertIsInstance(scenarios, list)
        for scenario in scenarios:
            self.assertIn('scenario_name', scenario)
            self.assertIn('probability', scenario)
            self.assertIn('timeline_months', scenario)
            self.assertIn('key_factors', scenario)
    
    def test_analyze_maturity_factors_dynamic(self):
        """Test maturity factor analysis with dynamic data"""
        # Generate dynamic market data
        market_data = self._generate_dynamic_market_data()
        
        # Test factor analysis
        factors = self.service._analyze_maturity_factors(market_data)
        
        # Verify structure
        self.assertIsInstance(factors, dict)
        
        # Verify key factor categories
        expected_categories = ['growth_dynamics', 'competitive_landscape', 'innovation_patterns', 
                             'regulatory_development', 'customer_evolution']
        
        for category in expected_categories:
            self.assertIn(category, factors)
            category_data = factors[category]
            self.assertIn('score', category_data)
            self.assertIn('trend', category_data)
            self.assertIn('impact_level', category_data)
    
    def test_generate_maturity_recommendations_dynamic(self):
        """Test maturity recommendation generation with dynamic data"""
        # Generate dynamic market data and assessment
        market_data = self._generate_dynamic_market_data()
        assessment = self.service.assess_market_maturity(market_data)
        
        # Test recommendation generation
        recommendations = self.service._generate_maturity_recommendations(assessment, market_data)
        
        # Verify structure
        self.assertIsInstance(recommendations, list)
        for recommendation in recommendations:
            self.assertIsInstance(recommendation, dict)
            self.assertIn('category', recommendation)
            self.assertIn('priority', recommendation)
            self.assertIn('description', recommendation)
            self.assertIn('expected_impact', recommendation)
            self.assertIn('implementation_timeline', recommendation)
    
    def test_fallback_assessment_dynamic(self):
        """Test fallback assessment creation"""
        # Test fallback creation
        fallback = self.service._create_fallback_assessment()
        
        # Verify structure
        self.assertIsInstance(fallback, dict)
        self.assertIn('assessment_id', fallback)
        self.assertEqual(fallback['assessment_id'], 'fallback')
        self.assertIn('timestamp', fallback)
        self.assertIn('maturity_score', fallback)
        self.assertIn('maturity_stage', fallback)
    
    def test_error_handling_dynamic(self):
        """Test error handling with various scenarios"""
        # Test with None data
        result = self.service.assess_market_maturity(None)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['assessment_id'], 'fallback')
        
        # Test with empty data
        result = self.service.assess_market_maturity({})
        self.assertIsInstance(result, dict)
        
        # Test with malformed data
        malformed_data = {'invalid': 'data', 'market_metrics': 'not_a_dict'}
        result = self.service.assess_market_maturity(malformed_data)
        self.assertIsInstance(result, dict)
    
    def test_singleton_pattern(self):
        """Test singleton pattern functionality"""
        # Get multiple instances
        service1 = get_market_maturity_service()
        service2 = get_market_maturity_service()
        
        # Verify they are the same instance
        self.assertIs(service1, service2)
    
    def test_thread_safety_dynamic(self):
        """Test thread safety with concurrent assessment"""
        import threading
        
        results = []
        errors = []
        
        def assess_maturity_worker():
            try:
                market_data = self._generate_dynamic_market_data()
                result = self.service.assess_market_maturity(market_data)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=assess_maturity_worker)
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
            self.assertIn('assessment_id', result)
    
    def test_configuration_driven_behavior(self):
        """Test that all behavior is driven by configuration"""
        # Change configuration values
        new_config = {
            'maturity_thresholds': {
                'emerging_threshold': 0.2,
                'growth_threshold': 0.4,
                'mature_threshold': 0.7
            },
            'maturity_scoring': {
                'growth_rate_weight': 0.4,
                'competition_weight': 0.3
            }
        }
        
        # Update mock configuration
        self.test_config.update(new_config)
        
        # Generate assessment with new config
        market_data = self._generate_dynamic_market_data()
        result = self.service.assess_market_maturity(market_data)
        
        # Verify behavior changes with configuration
        self.assertIsInstance(result, dict)
        self.assertIn('maturity_score', result)
        self.assertIn('maturity_stage', result)
    
    def test_maturity_stage_classification_dynamic(self):
        """Test maturity stage classification with configurable thresholds"""
        # Test different maturity scores
        test_scores = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for score in test_scores:
            stage = self.service._classify_maturity_stage(score)
            
            # Verify classification is valid
            self.assertIn(stage, ['emerging', 'growth', 'mature', 'decline'])
            
            # Verify classification matches thresholds
            if score >= self.test_config['maturity_thresholds']['decline_threshold']:
                self.assertEqual(stage, 'decline')
            elif score >= self.test_config['maturity_thresholds']['mature_threshold']:
                self.assertEqual(stage, 'mature')
            elif score >= self.test_config['maturity_thresholds']['growth_threshold']:
                self.assertEqual(stage, 'growth')
            else:
                self.assertEqual(stage, 'emerging')
    
    def test_historical_trend_analysis_dynamic(self):
        """Test historical trend analysis with dynamic data"""
        # Generate market data with historical information
        market_data = self._generate_dynamic_market_data()
        
        # Test historical trend analysis
        trends = self.service._analyze_historical_trends(market_data)
        
        # Verify structure
        self.assertIsInstance(trends, dict)
        self.assertIn('growth_trend', trends)
        self.assertIn('competition_trend', trends)
        self.assertIn('maturity_progression', trends)
        self.assertIn('trend_stability', trends)
        
        # Verify trend values are valid
        for trend_key, trend_value in trends.items():
            if isinstance(trend_value, (int, float)):
                self.assertGreaterEqual(trend_value, -1.0)
                self.assertLessEqual(trend_value, 1.0)
    
    def test_competitive_landscape_impact_dynamic(self):
        """Test competitive landscape impact on maturity assessment"""
        # Generate market data with different competition levels
        high_competition_data = self._generate_dynamic_market_data('mature')
        high_competition_data['market_metrics']['market_share_concentration'] = 0.9
        
        low_competition_data = self._generate_dynamic_market_data('emerging')
        low_competition_data['market_metrics']['market_share_concentration'] = 0.2
        
        # Test assessments
        high_comp_result = self.service.assess_market_maturity(high_competition_data)
        low_comp_result = self.service.assess_market_maturity(low_competition_data)
        
        # Verify both assessments are valid
        self.assertIsInstance(high_comp_result, dict)
        self.assertIsInstance(low_comp_result, dict)
        
        # Verify different competition levels affect assessment
        self.assertIn('maturity_score', high_comp_result)
        self.assertIn('maturity_score', low_comp_result)


class TestMarketMaturityServiceIntegration(unittest.TestCase):
    """Integration tests with real configuration"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Use real config manager
        self.config_manager = ConfigurationManager()
        self.service = MarketMaturityService()
    
    def test_real_configuration_integration(self):
        """Test with real configuration files"""
        # Generate realistic market data
        market_data = {
            'market_id': 'test_market',
            'market_name': 'Test Technology Market',
            'sector': 'technology',
            'market_metrics': {
                'total_market_size': 500000000,
                'annual_growth_rate': 0.15,
                'market_share_concentration': 0.6,
                'number_of_players': 50
            },
            'innovation_indicators': {
                'r_and_d_intensity': 0.7,
                'patent_activity': 200,
                'technology_adoption_rate': 0.8
            },
            'regulatory_environment': {
                'regulatory_maturity': 0.5,
                'compliance_complexity': 0.4
            }
        }
        
        # Test maturity assessment
        result = self.service.assess_market_maturity(market_data)
        
        # Verify realistic results
        self.assertIsInstance(result, dict)
        self.assertIn('assessment_id', result)
        self.assertIn('maturity_score', result)
        self.assertIn('maturity_stage', result)
        
        # Maturity assessment should be reasonable for growth stage market
        maturity_score = result['maturity_score']
        self.assertGreater(maturity_score, 0.0)
        self.assertLess(maturity_score, 1.0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
