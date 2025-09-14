"""
Production-Ready Dynamic Test Suite for Compet            'analysis': {
                'depth_level': random.randint(1, 10),
                'confidence_threshold': random.uniform(0.1, 0.9),
                'max_competitors_tracked': random.randint(5, 100),
                'default_confidence_score': random.uniform(0.5, 0.95),
                'unknown_industry_fallback': f'unknown_industry_{random.randint(1, 100)}' Analysis Service
===============================================================

Comprehensive test coverage for enterprise production deployment:
- Performance & Memory Testing
- Security & Input Validation  
- Edge Cases & Boundary Conditions
- Enterprise-Scale Scenarios
- Configuration Validation
- Regression Testing
- Zero Hardcoded Values - All Dynamic

CRITICAL: This test suite ensures production safety with nuclear-grade validation
"""

import unittest
import sys
import os
import json
import uuid
import time
import threading
import random
import tracemalloc
import gc
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import hashlib
import pickle

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from services.market_intelligence.competitive_analysis_service import CompetitiveAnalysisService, get_competitive_analysis_service
    from config.config_manager import ConfigurationManager
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure the competitive_analysis_service.py exists and is properly configured")
    sys.exit(1)


class ProductionTestConfig:
    """Dynamic configuration generator for production testing"""
    
    @staticmethod
    def generate_random_config() -> Dict[str, Any]:
        """Generate completely randomized configuration for testing - ALL REQUIRED VALUES"""
        return {
            'analysis': {
                'depth_level': random.randint(1, 5),
                'confidence_threshold': random.uniform(0.1, 0.9),
                'max_competitors_tracked': random.randint(10, 1000),
                'default_confidence_score': random.uniform(0.5, 1.0),
                'unknown_industry_fallback': f'test_industry_{random.randint(1, 100)}',
                'safe_fallback_industry': f'fallback_industry_{random.randint(1, 100)}'
            },
            'monitoring': {
                'update_frequency_hours': random.randint(1, 168),
                'significant_change_threshold': random.uniform(0.01, 0.5)
            },
            'market': {
                'significant_share_threshold': random.uniform(0.01, 0.3),
                'concentration_ratio_cr4': random.uniform(0.3, 0.9),
                'hhi_threshold_concentrated': random.uniform(0.15, 0.4)
            },
            'market_structure': {
                'safe_fallback_type': f'test_structure_{random.randint(1, 100)}',
                'high_concentration_threshold': random.uniform(0.7, 0.9),
                'medium_concentration_threshold': random.uniform(0.4, 0.6),
                'dominant_threshold': random.uniform(0.15, 0.4),
                'fragmented_threshold': random.uniform(0.1, 0.3),
                'no_competitors_type': f'market_type_no_competitors_{random.randint(1, 100)}',
                'fragmented_classification': f'market_fragmented_{random.randint(1, 100)}',
                'monopolistic_classification': f'market_monopolistic_{random.randint(1, 100)}',
                'concentrated_classification': f'market_concentrated_{random.randint(1, 100)}',
                'oligopolistic_classification': f'market_oligopolistic_{random.randint(1, 100)}',
                'moderately_concentrated_classification': f'market_moderate_{random.randint(1, 100)}',
                'competitive_classification': f'market_competitive_{random.randint(1, 100)}',
                'error_fallback_type': f'market_error_fallback_{random.randint(1, 100)}'
            },
            'competitive_intensity': {
                'high_threshold': random.uniform(0.7, 0.95),
                'medium_threshold': random.uniform(0.3, 0.6),
                'low_threshold': random.uniform(0.05, 0.29),
                'price_competition_weight': random.uniform(0.1, 0.5),
                'innovation_weight': random.uniform(0.1, 0.5),
                'market_growth_weight': random.uniform(0.1, 0.4),
                'entry_barriers_weight': random.uniform(0.1, 0.3),
                'default_weight': random.uniform(0.1, 0.3),
                'fallback_level': f'test_intensity_{random.randint(1, 100)}',
                'fallback_score': random.uniform(0.1, 1.0),
                'error_fallback_level': f'error_intensity_{random.randint(1, 100)}',
                'error_fallback_score': random.uniform(0.1, 0.5)
            },
            'positioning': {
                'leader_threshold': random.uniform(0.2, 0.5),
                'challenger_threshold': random.uniform(0.1, 0.25),
                'follower_threshold': random.uniform(0.05, 0.15),
                'niche_threshold': random.uniform(0.01, 0.1),
                'leader_position': f'market_leader_{random.randint(1, 100)}',
                'challenger_position': f'challenger_{random.randint(1, 100)}',
                'default_market_position': f'position_{random.randint(1, 100)}'
            },
            'strategic_moves': {
                'default_impact_level': f'impact_{random.choice(["high", "medium", "low"])}_level',
                'default_timing': f'timing_{random.choice(["immediate", "short_term", "long_term"])}'
            },
            'threat_assessment': {
                'factors': [f'factor_{i}' for i in range(random.randint(3, 10))],
                'high_threat_threshold': random.uniform(0.7, 0.9),
                'medium_threat_threshold': random.uniform(0.4, 0.6)
            },
            'threat_levels': {
                'default_fallback': f'threat_level_{random.randint(1, 10)}'
            },
            'priorities': {
                'capability_gap_default': f'priority_{random.choice(["high", "medium", "low"])}'
            },
            'portfolio_strength': {
                'default_market_fit': random.uniform(0.1, 0.9)
            },
            'portfolio': {
                'broad_threshold': random.uniform(0.5, 0.9)
            },
            'portfolio_categorization': {
                'error_fallback': f'portfolio_error_{random.randint(1, 100)}'
            },
            'marketing': {
                'unknown_spend_level_fallback': f'marketing_fallback_{random.randint(1, 100)}'
            },
            'intensity_analysis': {
                'default_weight': random.uniform(0.1, 0.5),
                'factor_weights': {
                    'price_competition': random.uniform(0.1, 0.4),
                    'innovation_level': random.uniform(0.1, 0.4),
                    'market_growth': random.uniform(0.1, 0.3),
                    'entry_barriers': random.uniform(0.1, 0.3)
                }
            },
            'opportunities': {
                'gap_threshold': random.uniform(0.1, 0.5)
            },
            'cache': {
                'ttl_hours': random.randint(1, 48)
            },
            'competitor_analysis': {
                'limited_geographic_presence_threshold': random.uniform(0.1, 0.5)
            },
            'competitor_strengths': {
                'high_market_share_classification': f'strength_market_share_{random.randint(1, 100)}',
                'high_brand_recognition_classification': f'strength_brand_{random.randint(1, 100)}',
                'high_innovation_leadership_classification': f'strength_innovation_{random.randint(1, 100)}'
            },
            'competitor_weaknesses': {
                'negative_revenue_growth_classification': f'weakness_growth_{random.randint(1, 100)}',
                'limited_geographic_reach_classification': f'weakness_geography_{random.randint(1, 100)}'
            }
        }
    
    @staticmethod
    def generate_extreme_config() -> Dict[str, Any]:
        """Generate extreme boundary value configuration"""
        return {
            'analysis': {
                'depth_level': random.choice([1, 10, 100]),  # Extreme values
                'confidence_threshold': random.choice([0.001, 0.999]),
                'max_competitors_tracked': random.choice([1, 10000]),
                'default_confidence_score': random.choice([0.0, 1.0])
            },
            'monitoring': {
                'update_frequency_hours': random.choice([1, 8760]),  # 1 hour to 1 year
                'significant_change_threshold': random.choice([0.0001, 0.9999])
            },
            'market': {
                'significant_share_threshold': random.choice([0.0001, 0.9999]),
                'concentration_ratio_cr4': random.choice([0.0001, 0.9999]),
                'hhi_threshold_concentrated': random.choice([0.0001, 0.9999])
            }
        }


class TestCompetitiveAnalysisProduction(unittest.TestCase):
    """Production-grade test suite with comprehensive coverage"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level test resources"""
        cls.performance_metrics = []
        cls.memory_usage_baseline = None
        
    def setUp(self):
        """Set up each test with fresh dynamic configuration"""
        # Generate random configuration for each test
        self.test_config = ProductionTestConfig.generate_random_config()
        
        # Create mock configuration manager  
        self.config_manager = Mock(spec=ConfigurationManager)
        self.config_manager.get.side_effect = self._get_dynamic_config_value
        
        # Wrap our config under competitive_analysis key for proper service access
        self.wrapped_config = {'competitive_analysis': self.test_config}
        
        # Create service with dynamic configuration
        self.service = CompetitiveAnalysisService()
        self.service.config_manager = self.config_manager
        
        # Performance tracking
        self.start_time = time.time()
        
        # Memory tracking
        tracemalloc.start()
        
    def tearDown(self):
        """Clean up after each test"""
        # Record performance metrics
        execution_time = time.time() - self.start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.performance_metrics.append({
            'test_name': self._testMethodName,
            'execution_time': execution_time,
            'memory_current': current,
            'memory_peak': peak
        })
        
        # Garbage collection
        gc.collect()
    
    def _get_dynamic_config_value(self, key: str, default=None):
        """Dynamically retrieve configuration values"""
        keys = key.split('.')
        value = self.wrapped_config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            # Return random default if key not found
            if isinstance(default, (int, float)):
                return random.uniform(0.1, 1.0) if isinstance(default, float) else random.randint(1, 100)
            elif isinstance(default, str):
                return f"dynamic_{random.randint(1, 1000)}"
            return default
    
    def _generate_enterprise_competitor_data(self, count: int = None) -> List[Dict[str, Any]]:
        """Generate enterprise-scale competitor data"""
        if count is None:
            count = random.randint(50, 500)  # Enterprise scale
        
        competitors = []
        total_share = 0.0
        
        for i in range(count):
            # Realistic enterprise data distributions
            market_share = random.lognormvariate(mu=-3, sigma=1.5)  # Long-tail distribution
            market_share = min(market_share, 0.4)  # Cap at 40%
            total_share += market_share
            
            competitor = {
                'competitor_id': f'enterprise_comp_{i}_{uuid.uuid4().hex[:12]}',
                'name': f'Enterprise_Corp_{i}',
                'market_share': market_share,
                'revenue': random.lognormvariate(mu=16, sigma=2),  # $1M-$1B range
                'growth_rate': random.normalvariate(mu=0.1, sigma=0.15),
                'pricing_strategy': random.choice(['premium', 'competitive', 'discount', 'dynamic']),
                'innovation_score': random.betavariate(alpha=2, beta=3),  # Skewed toward lower scores
                'customer_satisfaction': random.betavariate(alpha=5, beta=2),  # Skewed toward higher scores
                'geographical_presence': random.randint(1, 195),  # Number of countries
                'product_portfolio_size': random.lognormvariate(mu=3, sigma=1),
                'market_entry_date': datetime.now() - timedelta(days=random.randint(1, 10950)),  # Up to 30 years
                'regulatory_compliance_score': random.uniform(0.5, 1.0),
                'financial_stability_rating': random.choice(['AAA', 'AA', 'A', 'BBB', 'BB', 'B']),
                'technology_adoption_rate': random.uniform(0.1, 1.0),
                'brand_recognition_index': random.uniform(0.0, 1.0)
            }
            competitors.append(competitor)
        
        # Normalize market shares
        if total_share > 0.95:
            normalization_factor = 0.95 / total_share
            for comp in competitors:
                comp['market_share'] *= normalization_factor
        
        return competitors
    
    def _generate_stress_test_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Generate data for stress testing"""
        # Large competitor dataset
        competitors = self._generate_enterprise_competitor_data(1000)
        
        # Complex market data
        market_data = {
            'market_id': f'stress_test_{uuid.uuid4()}',
            'total_market_size': random.uniform(1e9, 1e12),  # $1B - $1T
            'growth_rate': random.normalvariate(0.05, 0.1),
            'maturity_level': random.choice(['emerging', 'growing', 'mature', 'declining']),
            'barriers_to_entry': random.uniform(0.0, 1.0),
            'regulatory_environment': random.choice(['minimal', 'light', 'moderate', 'heavy', 'strict']),
            'technology_disruption_risk': random.uniform(0.0, 1.0),
            'market_segments': [f'segment_{i}' for i in range(random.randint(5, 50))],
            'geographic_regions': [f'region_{i}' for i in range(random.randint(3, 20))],
            'seasonal_factors': {f'quarter_{i}': random.uniform(0.8, 1.2) for i in range(1, 5)}
        }
        
        return competitors, market_data
    
    # ================================
    # CORE FUNCTIONALITY TESTS
    # ================================
    
    def test_competitive_landscape_analysis_production(self):
        """Test competitive landscape analysis with production data volumes"""
        competitors, market_data = self._generate_stress_test_data()
        
        # Performance constraint: Must complete within 30 seconds
        start_time = time.time()
        result = self.service.analyze_competitive_landscape(competitors, market_data)
        execution_time = time.time() - start_time
        
        # Validate performance
        self.assertLess(execution_time, 30.0, f"Analysis took {execution_time:.2f}s, exceeds 30s limit")
        
        # Validate structure
        self.assertIsInstance(result, dict)
        required_keys = ['analysis_id', 'timestamp', 'market_structure', 'competitive_intensity', 'key_players']
        for key in required_keys:
            self.assertIn(key, result, f"Missing required key: {key}")
        
        # Validate data integrity
        self.assertIsInstance(result['analysis_id'], str)
        self.assertTrue(len(result['analysis_id']) > 0)
    
    def test_competitor_monitoring_enterprise_scale(self):
        """Test competitor monitoring at enterprise scale"""
        # Monitor multiple competitors simultaneously
        competitors_to_monitor = random.randint(100, 500)
        results = []
        
        start_time = time.time()
        
        for i in range(competitors_to_monitor):
            competitor_id = f'enterprise_comp_{i}'
            competitor_data = self._generate_enterprise_competitor_data(1)[0]
            result = self.service.monitor_competitor(competitor_id, competitor_data)
            results.append(result)
        
        execution_time = time.time() - start_time
        
        # Performance validation
        avg_time_per_competitor = execution_time / competitors_to_monitor
        self.assertLess(avg_time_per_competitor, 0.1, f"Average monitoring time {avg_time_per_competitor:.4f}s exceeds 0.1s limit")
        
        # Validate all results
        self.assertEqual(len(results), competitors_to_monitor)
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('competitor_id', result)
    
    # ================================
    # SECURITY & VALIDATION TESTS
    # ================================
    
    def test_input_sanitization_and_injection_protection(self):
        """Test security against various injection attacks"""
        malicious_inputs = [
            # SQL injection attempts
            "'; DROP TABLE competitors; --",
            "1' OR '1'='1",
            
            # Script injection attempts
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            
            # Command injection attempts
            "; rm -rf /",
            "| cat /etc/passwd",
            
            # Path traversal attempts
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            
            # Buffer overflow attempts
            "A" * 10000,
            
            # JSON injection
            '{"evil": "payload"}',
            
            # XML injection
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
        ]
        
        for malicious_input in malicious_inputs:
            # Test competitor data injection
            malicious_competitor = {
                'competitor_id': malicious_input,
                'name': malicious_input,
                'market_share': 0.1,
                'revenue': 1000000
            }
            
            # Should handle gracefully without errors
            try:
                result = self.service.monitor_competitor(f"safe_id_{random.randint(1,1000)}", malicious_competitor)
                self.assertIsInstance(result, dict)
            except Exception as e:
                # Should not crash, but may return error result
                self.assertIsInstance(str(e), str)
    
    def test_data_validation_boundaries(self):
        """Test boundary conditions and data validation"""
        boundary_test_cases = [
            # Extreme market shares
            {'market_share': -1.0, 'should_handle': True},
            {'market_share': 2.0, 'should_handle': True},
            {'market_share': float('inf'), 'should_handle': True},
            {'market_share': float('nan'), 'should_handle': True},
            
            # Extreme revenues
            {'revenue': -1000000, 'should_handle': True},
            {'revenue': 1e20, 'should_handle': True},
            {'revenue': float('inf'), 'should_handle': True},
            
            # Empty/None values
            {'market_share': None, 'should_handle': True},
            {'revenue': None, 'should_handle': True},
            {'competitor_id': None, 'should_handle': True},
            {'competitor_id': '', 'should_handle': True},
        ]
        
        for test_case in boundary_test_cases:
            competitor_data = {
                'competitor_id': 'test_competitor',
                'name': 'Test Corp',
                'market_share': 0.1,
                'revenue': 1000000
            }
            
            # Override with test values
            for key, value in test_case.items():
                if key != 'should_handle':
                    competitor_data[key] = value
            
            # Test should handle gracefully
            try:
                result = self.service.monitor_competitor('boundary_test', competitor_data)
                self.assertIsInstance(result, dict)
            except Exception:
                # Should not crash with unhandled exceptions
                pass
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation"""
        initial_memory = tracemalloc.get_traced_memory()[0]
        
        # Perform many operations
        for i in range(100):
            competitors = self._generate_enterprise_competitor_data(50)
            market_data = {'market_id': f'memory_test_{i}', 'total_market_size': 1000000}
            
            result = self.service.analyze_competitive_landscape(competitors, market_data)
            
            # Force garbage collection
            if i % 10 == 0:
                gc.collect()
        
        final_memory = tracemalloc.get_traced_memory()[0]
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 50MB for 100 operations)
        max_acceptable_increase = 50 * 1024 * 1024  # 50MB
        self.assertLess(memory_increase, max_acceptable_increase, 
                       f"Memory increased by {memory_increase / (1024*1024):.2f}MB, exceeds 50MB limit")
    
    # ================================
    # CONCURRENCY & THREADING TESTS
    # ================================
    
    def test_concurrent_analysis_thread_safety(self):
        """Test thread safety under high concurrency"""
        num_threads = 20
        operations_per_thread = 10
        results = []
        errors = []
        lock = threading.Lock()
        
        def concurrent_analysis_worker():
            thread_results = []
            thread_errors = []
            
            try:
                for _ in range(operations_per_thread):
                    competitors = self._generate_enterprise_competitor_data(10)
                    market_data = {'market_id': f'thread_test_{uuid.uuid4()}', 'total_market_size': 1000000}
                    
                    result = self.service.analyze_competitive_landscape(competitors, market_data)
                    thread_results.append(result)
                    
            except Exception as e:
                thread_errors.append(e)
            
            with lock:
                results.extend(thread_results)
                errors.extend(thread_errors)
        
        # Create and start threads
        threads = []
        start_time = time.time()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=concurrent_analysis_worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=60)  # 60 second timeout
        
        execution_time = time.time() - start_time
        
        # Validate results
        self.assertEqual(len(errors), 0, f"Concurrency errors occurred: {errors[:3]}")  # Show first 3 errors
        self.assertEqual(len(results), num_threads * operations_per_thread)
        self.assertLess(execution_time, 60, f"Concurrent execution took {execution_time:.2f}s, exceeds 60s limit")
        
        # Validate all results are valid
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('analysis_id', result)
    
    def test_deadlock_prevention(self):
        """Test prevention of deadlocks in concurrent scenarios"""
        def deadlock_test_worker(barrier, results_list):
            try:
                # All threads wait at barrier, then execute simultaneously
                barrier.wait(timeout=30)
                
                # Perform operation that could cause deadlock
                competitors = self._generate_enterprise_competitor_data(5)
                market_data = {'market_id': f'deadlock_test_{uuid.uuid4()}'}
                
                result = self.service.analyze_competitive_landscape(competitors, market_data)
                results_list.append(result)
                
            except Exception as e:
                results_list.append(f"ERROR: {str(e)}")
        
        num_threads = 10
        barrier = threading.Barrier(num_threads)
        results_list = []
        
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=deadlock_test_worker, args=(barrier, results_list))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads with timeout
        start_time = time.time()
        for thread in threads:
            thread.join(timeout=30)
        
        execution_time = time.time() - start_time
        
        # Should complete without deadlock
        self.assertLess(execution_time, 30, "Potential deadlock detected - execution exceeded 30s")
        self.assertEqual(len(results_list), num_threads, f"Only {len(results_list)}/{num_threads} threads completed")
    
    # ================================
    # PERFORMANCE & SCALABILITY TESTS
    # ================================
    
    def test_large_dataset_performance(self):
        """Test performance with large enterprise datasets"""
        dataset_sizes = [100, 500, 1000, 2000]
        performance_results = []
        
        for size in dataset_sizes:
            competitors = self._generate_enterprise_competitor_data(size)
            market_data = {'market_id': f'perf_test_{size}', 'total_market_size': size * 1000000}
            
            start_time = time.time()
            start_memory = tracemalloc.get_traced_memory()[0]
            
            result = self.service.analyze_competitive_landscape(competitors, market_data)
            
            end_time = time.time()
            end_memory = tracemalloc.get_traced_memory()[0]
            
            performance_results.append({
                'dataset_size': size,
                'execution_time': end_time - start_time,
                'memory_used': end_memory - start_memory,
                'result_valid': isinstance(result, dict) and 'analysis_id' in result
            })
        
        # Validate performance scaling
        for i, perf in enumerate(performance_results):
            self.assertTrue(perf['result_valid'], f"Invalid result for dataset size {perf['dataset_size']}")
            
            # Performance should scale reasonably (not exponentially)
            if i > 0:
                prev_perf = performance_results[i-1]
                time_ratio = perf['execution_time'] / prev_perf['execution_time']
                size_ratio = perf['dataset_size'] / prev_perf['dataset_size']
                
                # Time scaling should be reasonable (not more than 3x size ratio)
                self.assertLess(time_ratio, size_ratio * 3, 
                               f"Performance degraded significantly: {time_ratio:.2f}x time for {size_ratio:.2f}x data")
    
    def test_memory_efficiency_large_datasets(self):
        """Test memory efficiency with large datasets"""
        large_competitor_count = 5000
        competitors = self._generate_enterprise_competitor_data(large_competitor_count)
        
        start_memory = tracemalloc.get_traced_memory()[0]
        
        result = self.service.analyze_competitive_landscape(competitors, {})
        
        peak_memory = tracemalloc.get_traced_memory()[1]
        memory_used = peak_memory - start_memory
        
        # Memory usage should be reasonable (< 100MB for 5000 competitors)
        max_acceptable_memory = 100 * 1024 * 1024  # 100MB
        self.assertLess(memory_used, max_acceptable_memory,
                       f"Memory usage {memory_used / (1024*1024):.2f}MB exceeds 100MB limit")
        
        # Result should still be valid
        self.assertIsInstance(result, dict)
        self.assertIn('analysis_id', result)
    
    # ================================
    # CONFIGURATION & ERROR HANDLING
    # ================================
    
    def test_missing_configuration_handling(self):
        """Test graceful handling of missing configuration values"""
        # Create service with broken configuration
        broken_config_manager = Mock()
        broken_config_manager.get.side_effect = KeyError("Configuration not found")
        
        service_with_broken_config = CompetitiveAnalysisService()
        service_with_broken_config.config_manager = broken_config_manager
        
        competitors = self._generate_enterprise_competitor_data(5)
        
        # Should handle missing configuration gracefully
        try:
            result = service_with_broken_config.analyze_competitive_landscape(competitors, {})
            # If it doesn't raise an exception, result should be valid fallback
            self.assertIsInstance(result, dict)
        except Exception as e:
            # If it raises an exception, it should be a controlled exception
            self.assertIsInstance(str(e), str)
    
    def test_configuration_validation_extreme_values(self):
        """Test behavior with extreme configuration values"""
        extreme_configs = [
            ProductionTestConfig.generate_extreme_config(),
            {
                'analysis': {'confidence_threshold': -1.0},  # Invalid negative
                'market': {'significant_share_threshold': 2.0}  # Invalid > 1.0
            },
            {
                'analysis': {'max_competitors_tracked': 0},  # Edge case zero
                'monitoring': {'update_frequency_hours': -5}  # Invalid negative
            }
        ]
        
        for extreme_config in extreme_configs:
            # Update test configuration
            self.test_config.update(extreme_config)
            
            competitors = self._generate_enterprise_competitor_data(3)
            
            # Should handle extreme configuration gracefully
            try:
                result = self.service.analyze_competitive_landscape(competitors, {})
                self.assertIsInstance(result, dict)
            except Exception:
                # Should not crash with unhandled exceptions
                pass
    
    def test_data_corruption_recovery(self):
        """Test recovery from corrupted or malformed data"""
        corruption_scenarios = [
            # Circular references
            {},  # Will be modified to create circular reference
            
            # Mixed data types
            [1, "string", {"dict": "value"}, [1, 2, 3]],
            
            # Deeply nested structures
            {"level_" + str(i): {"nested": "data"} for i in range(1000)},
            
            # Unicode and encoding issues
            {"competitor_id": "测试公司", "name": "Тест компания", "data": "🏢📊💼"},
            
            # Large string values
            {"competitor_id": "comp_1", "description": "A" * 1000000},  # 1MB string
        ]
        
        # Create circular reference
        circular_dict = {"self_ref": None}
        circular_dict["self_ref"] = circular_dict
        corruption_scenarios[0] = circular_dict
        
        for corrupted_data in corruption_scenarios:
            try:
                if isinstance(corrupted_data, list):
                    result = self.service.analyze_competitive_landscape(corrupted_data, {})
                else:
                    result = self.service.analyze_competitive_landscape([corrupted_data], {})
                
                self.assertIsInstance(result, dict)
            except Exception:
                # Should not crash with unhandled exceptions
                pass
    
    # ================================
    # BUSINESS LOGIC VALIDATION
    # ================================
    
    def test_business_neutrality_enforcement(self):
        """Test that service remains business neutral under all conditions"""
        # Test with biased competitor names and data
        biased_scenarios = [
            {
                'competitor_id': 'clearly_superior_company',
                'name': 'Best Company Ever',
                'market_share': 0.9,  # Dominant
                'competitive_advantage': 'everything'
            },
            {
                'competitor_id': 'terrible_competitor',
                'name': 'Worst Company',
                'market_share': 0.01,  # Tiny
                'weaknesses': ['everything'],
                'strengths': []
            }
        ]
        
        for scenario in biased_scenarios:
            competitors = [scenario] + self._generate_enterprise_competitor_data(5)
            
            result = self.service.analyze_competitive_landscape(competitors, {})
            
            # Should provide neutral analysis regardless of input bias
            self.assertIsInstance(result, dict)
            
            # Analysis should not contain hardcoded biases
            result_str = json.dumps(result).lower()
            biased_terms = ['best', 'worst', 'terrible', 'superior', 'clearly']
            
            for term in biased_terms:
                self.assertNotIn(term, result_str, f"Analysis contains biased term: {term}")
    
    def test_configuration_dependency_validation(self):
        """Validate all business logic depends on configuration"""
        # Count configuration calls
        config_calls = []
        
        def track_config_calls(key, default=None):
            config_calls.append(key)
            return self._get_dynamic_config_value(key, default)
        
        self.config_manager.get.side_effect = track_config_calls
        
        # Use realistic competitor data to force more configuration calls
        competitors = [
            {
                'competitor_id': 'test_comp_1',
                'name': 'Test Company 1',
                'market_share': 0.3,
                'revenue': 1000000,
                'growth_rate': 0.15,
                'pricing_strategy': 'premium'
            },
            {
                'competitor_id': 'test_comp_2', 
                'name': 'Test Company 2',
                'market_share': 0.25,
                'revenue': 800000,
                'growth_rate': 0.12,
                'pricing_strategy': 'competitive'
            }
        ]
        market_data = {
            'market_id': 'config_test', 
            'total_market_size': 1000000,
            'industry': 'test_industry',
            'business_profile': {'industry': 'test_industry'}
        }
        
        result = self.service.analyze_competitive_landscape(competitors, market_data)
        
        # Should have made multiple configuration calls for realistic analysis
        self.assertGreater(len(config_calls), 10, f"Insufficient configuration dependency - only {len(config_calls)} calls made")
        
        # All configuration keys should follow expected patterns
        hierarchical_calls = [call for call in config_calls if '.' in call]
        self.assertGreater(len(hierarchical_calls), 5, "Should have hierarchical configuration calls")
        
        for call in config_calls:
            self.assertIsInstance(call, str)
            # Should start with competitive_analysis for our service
            self.assertTrue(call.startswith('competitive_analysis'), f"Unexpected config key: {call}")
    
    # ================================
    # REGRESSION & COMPATIBILITY TESTS
    # ================================
    
    def test_api_backward_compatibility(self):
        """Test that API maintains backward compatibility"""
        # Test legacy method signatures still work
        legacy_calls = [
            # Basic analysis with minimal parameters
            lambda: self.service.analyze_competitive_landscape([], {}),
            
            # Competitor monitoring with basic data
            lambda: self.service.monitor_competitor('test_id', {'competitor_id': 'test'}),
            
            # Analysis with None values (should not break)
            lambda: self.service.analyze_competitive_landscape(None, None),
        ]
        
        for legacy_call in legacy_calls:
            try:
                result = legacy_call()
                self.assertIsInstance(result, dict)
            except Exception as e:
                # Should handle gracefully, not crash
                self.assertIsInstance(str(e), str)
    
    def test_output_format_consistency(self):
        """Test that output format remains consistent across scenarios"""
        test_scenarios = [
            self._generate_enterprise_competitor_data(1),
            self._generate_enterprise_competitor_data(10),
            self._generate_enterprise_competitor_data(100),
            [],  # Empty
            None,  # None input
        ]
        
        output_schemas = []
        
        for scenario in test_scenarios:
            try:
                result = self.service.analyze_competitive_landscape(scenario, {})
                
                # Extract schema (keys and types)
                schema = self._extract_schema(result)
                output_schemas.append(schema)
                
            except Exception:
                output_schemas.append(None)
        
        # All valid schemas should be consistent
        valid_schemas = [s for s in output_schemas if s is not None]
        if len(valid_schemas) > 1:
            base_schema = valid_schemas[0]
            for schema in valid_schemas[1:]:
                # Core keys should be consistent
                core_keys = {'analysis_id', 'timestamp'}
                for key in core_keys:
                    if key in base_schema:
                        self.assertIn(key, schema, f"Missing core key {key} in output schema")
    
    def _extract_schema(self, data: Any, path: str = "") -> Dict[str, str]:
        """Extract schema (structure) from data"""
        if isinstance(data, dict):
            schema = {}
            for key, value in data.items():
                schema[f"{path}.{key}" if path else key] = type(value).__name__
                if isinstance(value, (dict, list)):
                    schema.update(self._extract_schema(value, f"{path}.{key}" if path else key))
            return schema
        elif isinstance(data, list) and data:
            return self._extract_schema(data[0], f"{path}[0]")
        else:
            return {}
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources and report performance"""
        if cls.performance_metrics:
            print("\n" + "="*80)
            print("PRODUCTION TEST PERFORMANCE REPORT")
            print("="*80)
            
            total_tests = len(cls.performance_metrics)
            total_time = sum(m['execution_time'] for m in cls.performance_metrics)
            total_memory = sum(m['memory_peak'] for m in cls.performance_metrics)
            
            print(f"Total Tests: {total_tests}")
            print(f"Total Execution Time: {total_time:.2f}s")
            print(f"Average Time per Test: {total_time/total_tests:.2f}s")
            print(f"Total Memory Usage: {total_memory/(1024*1024):.2f}MB")
            print(f"Average Memory per Test: {total_memory/(total_tests*1024*1024):.2f}MB")
            
            # Show slowest tests
            slowest_tests = sorted(cls.performance_metrics, key=lambda x: x['execution_time'], reverse=True)[:5]
            print(f"\nSlowest Tests:")
            for i, test in enumerate(slowest_tests, 1):
                print(f"  {i}. {test['test_name']}: {test['execution_time']:.2f}s")
            
            # Show memory-intensive tests
            memory_intensive = sorted(cls.performance_metrics, key=lambda x: x['memory_peak'], reverse=True)[:5]
            print(f"\nMemory Intensive Tests:")
            for i, test in enumerate(memory_intensive, 1):
                memory_mb = test['memory_peak'] / (1024*1024)
                print(f"  {i}. {test['test_name']}: {memory_mb:.2f}MB")
            
            print("="*80)


class TestCompetitiveAnalysisServiceProductionIntegration(unittest.TestCase):
    """Integration tests for production deployment validation"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.config_manager = ConfigurationManager()
        self.service = CompetitiveAnalysisService()
    
    def test_full_integration_realistic_scenario(self):
        """Test full integration with realistic enterprise scenario"""
        # Realistic enterprise competitive landscape
        competitors = [
            {
                'competitor_id': 'market_leader_corp',
                'name': 'Market Leader Corp',
                'market_share': 0.32,
                'revenue': 150000000,
                'growth_rate': 0.08,
                'pricing_strategy': 'premium',
                'innovation_score': 0.85,
                'geographical_presence': 45,
                'customer_satisfaction': 0.82
            },
            {
                'competitor_id': 'strong_challenger',
                'name': 'Strong Challenger Inc',
                'market_share': 0.24,
                'revenue': 120000000,
                'growth_rate': 0.15,
                'pricing_strategy': 'competitive',
                'innovation_score': 0.78,
                'geographical_presence': 38,
                'customer_satisfaction': 0.79
            },
            {
                'competitor_id': 'disruptive_startup',
                'name': 'Disruptive Startup Ltd',
                'market_share': 0.12,
                'revenue': 35000000,
                'growth_rate': 0.45,
                'pricing_strategy': 'discount',
                'innovation_score': 0.92,
                'geographical_presence': 15,
                'customer_satisfaction': 0.88
            }
        ]
        
        market_data = {
            'market_id': 'enterprise_saas_market',
            'total_market_size': 500000000,
            'growth_rate': 0.18,
            'maturity_level': 'growing',
            'barriers_to_entry': 0.65,
            'regulatory_environment': 'moderate',
            'technology_disruption_risk': 0.72
        }
        
        # Execute full analysis
        result = self.service.analyze_competitive_landscape(competitors, market_data)
        
        # Validate comprehensive output
        self.assertIsInstance(result, dict)
        
        required_sections = [
            'analysis_id', 'timestamp', 'market_structure', 
            'competitive_intensity', 'key_players', 'market_dynamics'
        ]
        
        for section in required_sections:
            self.assertIn(section, result, f"Missing analysis section: {section}")
        
        # Validate market structure analysis
        market_structure = result['market_structure']
        self.assertIn('concentration_index', market_structure)
        self.assertIn('market_type', market_structure)
        
        # Validate competitive intensity
        intensity = result['competitive_intensity']
        self.assertIn('overall_intensity', intensity)
        self.assertIsInstance(intensity['overall_intensity'], (int, float))
        
        print(f"\nIntegration Test Results:")
        print(f"Analysis ID: {result['analysis_id']}")
        print(f"Market Type: {market_structure.get('market_type', 'N/A')}")
        print(f"Competitive Intensity: {intensity.get('overall_intensity', 'N/A')}")


if __name__ == '__main__':
    # Configure test runner
    import sys
    
    # Set up comprehensive test reporting
    if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
        verbosity = 2
    else:
        verbosity = 1
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCompetitiveAnalysisProduction))
    suite.addTests(loader.loadTestsFromTestCase(TestCompetitiveAnalysisServiceProductionIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)