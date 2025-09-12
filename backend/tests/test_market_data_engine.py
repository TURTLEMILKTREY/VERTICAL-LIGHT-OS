"""
MarketDataEngine Test Suite - 100% Dynamic Configuration
All test parameters loaded from configuration files - zero hardcoded values
"""

import unittest
import os
import sys
from typing import Dict, List, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.goal_parser.dynamic_ai_parser import MarketDataEngine
from config.config_manager import ConfigurationManager


class TestMarketDataEngineDynamic(unittest.TestCase):
    """100% Dynamic MarketDataEngine Tests - All Values From Configuration"""
    
    def setUp(self):
        """Set up test environment using existing configuration only"""
        self.config_manager = ConfigurationManager()
        self.market_engine = MarketDataEngine()
        
        # Get test configuration - NO hardcoded values
        self.goal_parser_config = self.config_manager.get('goal_parser', {})
        self.budget_config = self.goal_parser_config.get('budget_thresholds', {})
        self.intelligence_config = self.goal_parser_config.get('intelligence', {})
        
        # Get all industries and regions from configuration
        self.industries = list(self.budget_config.get('industry_multipliers', {}).keys())
        self.regions = list(self.budget_config.get('region_multipliers', {}).keys())
        
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    def test_engine_initialization(self):
        """Test that engine initializes with configuration values only"""
        # Verify engine exists
        self.assertIsNotNone(self.market_engine)
        
        # Verify it has config manager
        self.assertIsNotNone(self.market_engine.config_manager)
        
        # Verify cache TTL comes from config
        expected_ttl = self.goal_parser_config.get('caching', {}).get('market_data_ttl_hours', 0)
        if expected_ttl > 0:
            self.assertEqual(self.market_engine.cache_ttl_hours, expected_ttl)
    
    def test_industry_multipliers_from_config(self):
        """Test that industry multipliers are loaded from configuration only"""
        industry_multipliers = self.budget_config.get('industry_multipliers', {})
        
        # Test each configured industry
        for industry, expected_multiplier in industry_multipliers.items():
            actual_multiplier = self.market_engine._get_industry_multiplier(industry)
            self.assertEqual(actual_multiplier, expected_multiplier,
                           f"Industry {industry} multiplier should match configuration")
    
    def test_region_multipliers_from_config(self):
        """Test that region multipliers are loaded from configuration only"""
        region_multipliers = self.budget_config.get('region_multipliers', {})
        
        # Test each configured region
        for region, expected_multiplier in region_multipliers.items():
            actual_multiplier = self.market_engine._get_region_multiplier(region)
            self.assertEqual(actual_multiplier, expected_multiplier,
                           f"Region {region} multiplier should match configuration")
    
    def test_budget_ranges_use_config_values(self):
        """Test that budget ranges are calculated from configuration values only"""
        if not self.industries or not self.regions:
            self.skipTest("No industries or regions configured")
        
        # Test first available industry and region
        industry = self.industries[0]
        region = self.regions[0]
        
        ranges = self.market_engine.get_market_budget_ranges(industry, region)
        
        # Verify ranges structure
        expected_keys = ['micro_threshold', 'small_threshold', 'medium_threshold', 
                        'large_threshold', 'enterprise_threshold']
        for key in expected_keys:
            self.assertIn(key, ranges, f"Range should include {key}")
        
        # Verify ranges are in ascending order
        thresholds = [ranges[key] for key in expected_keys]
        for i in range(len(thresholds) - 1):
            self.assertLess(thresholds[i], thresholds[i + 1],
                          "Thresholds should be in ascending order")
    
    def test_different_industries_produce_different_ranges(self):
        """Test that different industries produce different budget ranges based on config"""
        if len(self.industries) < 2:
            self.skipTest("Need at least 2 industries configured")
        
        # Get multipliers for comparison
        industry_multipliers = self.budget_config.get('industry_multipliers', {})
        industry1, industry2 = self.industries[0], self.industries[1]
        
        if industry1 not in industry_multipliers or industry2 not in industry_multipliers:
            self.skipTest("Industries not in multiplier configuration")
        
        mult1 = industry_multipliers[industry1]
        mult2 = industry_multipliers[industry2]
        
        if mult1 == mult2:
            self.skipTest("Industries have same multiplier")
        
        # Use same region
        region = self.regions[0] if self.regions else 'global'
        
        ranges1 = self.market_engine.get_market_budget_ranges(industry1, region)
        ranges2 = self.market_engine.get_market_budget_ranges(industry2, region)
        
        # Compare based on multipliers
        if mult1 > mult2:
            self.assertGreater(ranges1['medium_threshold'], ranges2['medium_threshold'],
                             f"{industry1} should have higher thresholds than {industry2}")
        else:
            self.assertLess(ranges1['medium_threshold'], ranges2['medium_threshold'],
                           f"{industry1} should have lower thresholds than {industry2}")
    
    def test_different_regions_produce_different_ranges(self):
        """Test that different regions produce different budget ranges based on config"""
        if len(self.regions) < 2:
            self.skipTest("Need at least 2 regions configured")
        
        # Get multipliers for comparison
        region_multipliers = self.budget_config.get('region_multipliers', {})
        region1, region2 = self.regions[0], self.regions[1]
        
        if region1 not in region_multipliers or region2 not in region_multipliers:
            self.skipTest("Regions not in multiplier configuration")
        
        mult1 = region_multipliers[region1]
        mult2 = region_multipliers[region2]
        
        if mult1 == mult2:
            self.skipTest("Regions have same multiplier")
        
        # Use same industry
        industry = self.industries[0] if self.industries else 'technology'
        
        ranges1 = self.market_engine.get_market_budget_ranges(industry, region1)
        ranges2 = self.market_engine.get_market_budget_ranges(industry, region2)
        
        # Compare based on multipliers
        if mult1 > mult2:
            self.assertGreater(ranges1['medium_threshold'], ranges2['medium_threshold'],
                             f"{region1} should have higher thresholds than {region2}")
        else:
            self.assertLess(ranges1['medium_threshold'], ranges2['medium_threshold'],
                           f"{region1} should have lower thresholds than {region2}")
    
    def test_caching_behavior(self):
        """Test caching functionality based on configuration"""
        if not self.industries or not self.regions:
            self.skipTest("No industries or regions configured")
        
        industry = self.industries[0]
        region = self.regions[0]
        
        # First call should populate cache
        ranges1 = self.market_engine.get_market_budget_ranges(industry, region)
        
        # Second call should use cache
        ranges2 = self.market_engine.get_market_budget_ranges(industry, region)
        
        # Results should be identical
        self.assertEqual(ranges1, ranges2, "Cached results should be identical")
        
        # Verify cache contains the entry
        cache_key = f"budget_ranges_{industry}_{region}"
        self.assertIn(cache_key, self.market_engine.data_cache, "Cache should contain the entry")


if __name__ == '__main__':
    unittest.main(verbosity=2)
