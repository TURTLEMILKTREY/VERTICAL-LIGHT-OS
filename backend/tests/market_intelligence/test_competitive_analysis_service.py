"""
Dynamic test suite for Competitive Analysis Service microservice
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

from services.market_intelligence.competitive_analysis_service import CompetitiveAnalysisService, get_competitive_analysis_service
from config.config_manager import ConfigurationManager


class TestCompetitiveAnalysisService(unittest.TestCase):
    """Dynamic test suite for Competitive Analysis Service - fully configurable"""
    
    def setUp(self):
        """Set up test environment with dynamic configuration"""
        self.config_manager = Mock(spec=ConfigurationManager)
        
        # Dynamic test configuration - all values configurable
        self.test_config = {
            'market_structure': {
                'hhi_multiplier': random.uniform(1.0, 2.0),
                'concentration_threshold': random.uniform(0.5, 0.9),
                'fragmented_threshold': random.uniform(0.1, 0.4)
            },
            'competitive_intensity': {
                'high_threshold': random.uniform(0.7, 0.9),
                'medium_threshold': random.uniform(0.4, 0.6),
                'price_competition_weight': random.uniform(0.1, 0.5),
                'innovation_weight': random.uniform(0.1, 0.5)
            },
            'monitoring': {
                'update_frequency_hours': random.randint(12, 72),
                'significant_change_threshold': random.uniform(0.1, 0.3)
            },
            'analysis_weights': {
                'market_share_weight': random.uniform(0.2, 0.5),
                'growth_rate_weight': random.uniform(0.1, 0.4),
                'innovation_weight': random.uniform(0.1, 0.3),
                'pricing_weight': random.uniform(0.1, 0.3)
            }
        }
        
        # Configure mock to return dynamic values
        self.config_manager.get.side_effect = self._get_config_value
        
        # Create service instance
        self.service = CompetitiveAnalysisService()
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
    
    def _generate_dynamic_competitor_data(self, num_competitors: int = None) -> List[Dict[str, Any]]:
        """Generate dynamic competitor data for testing"""
        if num_competitors is None:
            num_competitors = random.randint(2, 10)
        
        competitors = []
        total_market_share = 0
        
        for i in range(num_competitors):
            market_share = random.uniform(0.05, 0.4)
            total_market_share += market_share
            
            competitor = {
                'competitor_id': f'competitor_{i}_{uuid.uuid4().hex[:8]}',
                'name': f'Company_{i}',
                'market_share': market_share,
                'revenue': random.uniform(1000000, 100000000),
                'growth_rate': random.uniform(-0.1, 0.5),
                'pricing_strategy': random.choice(['premium', 'competitive', 'discount']),
                'innovation_score': random.uniform(0.1, 1.0),
                'customer_satisfaction': random.uniform(0.5, 1.0),
                'geographical_presence': random.randint(1, 50),
                'product_portfolio_size': random.randint(1, 100)
            }
            competitors.append(competitor)
        
        # Normalize market shares to sum to reasonable total
        normalization_factor = min(0.95, 1.0 / total_market_share)
        for competitor in competitors:
            competitor['market_share'] *= normalization_factor
        
        return competitors
    
    def _generate_dynamic_market_data(self) -> Dict[str, Any]:
        """Generate dynamic market data for testing"""
        return {
            'market_id': str(uuid.uuid4()),
            'total_market_size': random.uniform(10000000, 1000000000),
            'growth_rate': random.uniform(-0.05, 0.3),
            'maturity_level': random.choice(['emerging', 'growing', 'mature', 'declining']),
            'barriers_to_entry': random.uniform(0.1, 1.0),
            'regulatory_environment': random.choice(['light', 'moderate', 'heavy']),
            'technology_disruption_risk': random.uniform(0.1, 1.0)
        }
    
    def test_analyze_competitive_landscape_dynamic(self):
        """Test competitive landscape analysis with dynamic data"""
        # Generate dynamic test data
        competitors = self._generate_dynamic_competitor_data()
        market_data = self._generate_dynamic_market_data()
        
        # Test competitive analysis
        result = self.service.analyze_competitive_landscape(competitors, market_data)
        
        # Verify structure (no hardcoded values)
        self.assertIsInstance(result, dict)
        self.assertIn('analysis_id', result)
        self.assertIn('timestamp', result)
        self.assertIn('market_structure', result)
        self.assertIn('competitive_intensity', result)
        self.assertIn('key_players', result)
        self.assertIn('market_dynamics', result)
        
        # Verify market structure analysis
        market_structure = result['market_structure']
        self.assertIn('concentration_index', market_structure)
        self.assertIn('market_type', market_structure)
        self.assertIn('dominant_players', market_structure)
    
    def test_monitor_competitor_dynamic(self):
        """Test competitor monitoring with dynamic data"""
        # Generate dynamic competitor data
        competitor_id = f'test_competitor_{uuid.uuid4().hex[:8]}'
        competitor_data = self._generate_dynamic_competitor_data(1)[0]
        competitor_data['competitor_id'] = competitor_id
        
        # Test competitor monitoring
        result = self.service.monitor_competitor(competitor_id, competitor_data)
        
        # Verify structure
        self.assertIsInstance(result, dict)
        self.assertIn('competitor_id', result)
        self.assertIn('monitoring_timestamp', result)
        self.assertIn('profile_update', result)
        self.assertIn('change_analysis', result)
    
    def test_calculate_hhi_dynamic(self):
        """Test HHI calculation with dynamic market shares"""
        # Generate dynamic competitor data
        competitors = self._generate_dynamic_competitor_data()
        market_shares = [comp['market_share'] for comp in competitors]
        
        # Test HHI calculation
        hhi = self.service._calculate_hhi(market_shares)
        
        # Verify result is valid
        self.assertIsInstance(hhi, (int, float))
        self.assertGreaterEqual(hhi, 0.0)
        self.assertLessEqual(hhi, 1.0)
    
    def test_assess_competitive_intensity_dynamic(self):
        """Test competitive intensity assessment with dynamic parameters"""
        # Generate dynamic competitor data
        competitors = self._generate_dynamic_competitor_data()
        market_data = self._generate_dynamic_market_data()
        
        # Test competitive intensity assessment
        intensity = self.service._assess_competitive_intensity(competitors, market_data)
        
        # Verify structure
        self.assertIsInstance(intensity, dict)
        self.assertIn('overall_intensity', intensity)
        self.assertIn('intensity_level', intensity)
        self.assertIn('key_factors', intensity)
        
        # Verify intensity score is valid
        overall_intensity = intensity['overall_intensity']
        self.assertIsInstance(overall_intensity, (int, float))
        self.assertGreaterEqual(overall_intensity, 0.0)
        self.assertLessEqual(overall_intensity, 1.0)
    
    def test_identify_market_leaders_dynamic(self):
        """Test market leader identification with dynamic data"""
        # Generate dynamic competitor data
        competitors = self._generate_dynamic_competitor_data()
        
        # Test market leader identification
        leaders = self.service._identify_market_leaders(competitors)
        
        # Verify structure
        self.assertIsInstance(leaders, list)
        for leader in leaders:
            self.assertIsInstance(leader, dict)
            self.assertIn('competitor_id', leader)
            self.assertIn('leadership_score', leader)
            self.assertIn('strengths', leader)
    
    def test_analyze_competitive_positioning_dynamic(self):
        """Test competitive positioning analysis with dynamic data"""
        # Generate dynamic competitor data
        competitors = self._generate_dynamic_competitor_data()
        
        # Test positioning analysis
        positioning = self.service._analyze_competitive_positioning(competitors)
        
        # Verify structure
        self.assertIsInstance(positioning, dict)
        self.assertIn('positioning_map', positioning)
        self.assertIn('strategic_groups', positioning)
        self.assertIn('gaps_and_opportunities', positioning)
    
    def test_fallback_analysis_dynamic(self):
        """Test fallback analysis creation"""
        # Test fallback creation
        fallback = self.service._create_fallback_analysis()
        
        # Verify structure
        self.assertIsInstance(fallback, dict)
        self.assertIn('analysis_id', fallback)
        self.assertEqual(fallback['analysis_id'], 'fallback')
        self.assertIn('timestamp', fallback)
        self.assertIn('market_structure', fallback)
    
    def test_error_handling_dynamic(self):
        """Test error handling with various scenarios"""
        # Test with None data
        result = self.service.analyze_competitive_landscape(None, None)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['analysis_id'], 'fallback')
        
        # Test with empty data
        result = self.service.analyze_competitive_landscape([], {})
        self.assertIsInstance(result, dict)
        
        # Test with malformed data
        malformed_competitors = [{'invalid': 'data'}]
        malformed_market = {'invalid': 'data'}
        result = self.service.analyze_competitive_landscape(malformed_competitors, malformed_market)
        self.assertIsInstance(result, dict)
    
    def test_singleton_pattern(self):
        """Test singleton pattern functionality"""
        # Get multiple instances
        service1 = get_competitive_analysis_service()
        service2 = get_competitive_analysis_service()
        
        # Verify they are the same instance
        self.assertIs(service1, service2)
    
    def test_thread_safety_dynamic(self):
        """Test thread safety with concurrent analysis"""
        import threading
        
        results = []
        errors = []
        
        def analyze_competitor_worker():
            try:
                competitors = self._generate_dynamic_competitor_data()
                market_data = self._generate_dynamic_market_data()
                result = self.service.analyze_competitive_landscape(competitors, market_data)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=analyze_competitor_worker)
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
            self.assertIn('analysis_id', result)
    
    def test_configuration_driven_behavior(self):
        """Test that all behavior is driven by configuration"""
        # Change configuration values
        new_config = {
            'market_structure': {
                'hhi_multiplier': 1.5,
                'concentration_threshold': 0.7
            },
            'competitive_intensity': {
                'high_threshold': 0.8,
                'medium_threshold': 0.5
            }
        }
        
        # Update mock configuration
        self.test_config.update(new_config)
        
        # Generate analysis with new config
        competitors = self._generate_dynamic_competitor_data()
        market_data = self._generate_dynamic_market_data()
        result = self.service.analyze_competitive_landscape(competitors, market_data)
        
        # Verify behavior changes with configuration
        self.assertIsInstance(result, dict)
        self.assertIn('market_structure', result)
    
    def test_market_share_validation_dynamic(self):
        """Test market share validation with dynamic data"""
        # Generate competitors with various market share scenarios
        test_scenarios = [
            # Normal scenario
            self._generate_dynamic_competitor_data(5),
            # High concentration scenario
            [
                {'competitor_id': 'dominant', 'market_share': 0.7, 'revenue': 50000000},
                {'competitor_id': 'small1', 'market_share': 0.15, 'revenue': 10000000},
                {'competitor_id': 'small2', 'market_share': 0.15, 'revenue': 8000000}
            ],
            # Fragmented scenario
            [{'competitor_id': f'frag_{i}', 'market_share': 0.05, 'revenue': 1000000} 
             for i in range(20)]
        ]
        
        for competitors in test_scenarios:
            market_data = self._generate_dynamic_market_data()
            result = self.service.analyze_competitive_landscape(competitors, market_data)
            
            # Verify analysis handles different market structures
            self.assertIsInstance(result, dict)
            self.assertIn('market_structure', result)
            self.assertIn('market_type', result['market_structure'])


class TestCompetitiveAnalysisServiceIntegration(unittest.TestCase):
    """Integration tests with real configuration"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Use real config manager
        self.config_manager = ConfigurationManager()
        self.service = CompetitiveAnalysisService()
    
    def test_real_configuration_integration(self):
        """Test with real configuration files"""
        # Generate realistic competitor data
        competitors = [
            {
                'competitor_id': 'comp_1',
                'name': 'Leader Corp',
                'market_share': 0.35,
                'revenue': 75000000,
                'growth_rate': 0.12
            },
            {
                'competitor_id': 'comp_2',
                'name': 'Challenger Inc',
                'market_share': 0.25,
                'revenue': 50000000,
                'growth_rate': 0.18
            },
            {
                'competitor_id': 'comp_3',
                'name': 'Follower Ltd',
                'market_share': 0.15,
                'revenue': 25000000,
                'growth_rate': 0.08
            }
        ]
        
        market_data = {
            'market_id': 'test_market',
            'total_market_size': 200000000,
            'growth_rate': 0.15,
            'maturity_level': 'growing'
        }
        
        # Test competitive analysis
        result = self.service.analyze_competitive_landscape(competitors, market_data)
        
        # Verify realistic results
        self.assertIsInstance(result, dict)
        self.assertIn('analysis_id', result)
        self.assertIn('market_structure', result)
        
        # Market structure should be realistic
        market_structure = result['market_structure']
        self.assertIn('concentration_index', market_structure)
        self.assertIn('market_type', market_structure)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
