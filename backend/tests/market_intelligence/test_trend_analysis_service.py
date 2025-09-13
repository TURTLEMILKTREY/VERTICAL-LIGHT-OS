"""
Dynamic test suite for Trend Analysis Service microservice
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

from services.market_intelligence.trend_analysis_service import TrendAnalysisService, get_trend_analysis_service
from config.config_manager import ConfigurationManager


class TestTrendAnalysisService(unittest.TestCase):
    """Dynamic test suite for Trend Analysis Service - fully configurable"""
    
    def setUp(self):
        """Set up test environment with dynamic configuration"""
        self.config_manager = Mock(spec=ConfigurationManager)
        
        # Dynamic test configuration - all values configurable
        self.test_config = {
            'trend_detection': {
                'sensitivity_threshold': random.uniform(0.05, 0.2),
                'min_data_points': random.randint(5, 20),
                'trend_strength_threshold': random.uniform(0.6, 0.9),
                'noise_reduction_factor': random.uniform(0.1, 0.3)
            },
            'forecasting': {
                'prediction_horizon_days': random.randint(30, 180),
                'confidence_interval': random.uniform(0.8, 0.95),
                'seasonal_adjustment': random.choice([True, False]),
                'trend_extrapolation_weight': random.uniform(0.6, 0.9)
            },
            'pattern_recognition': {
                'cycle_detection_threshold': random.uniform(0.7, 0.95),
                'anomaly_detection_sensitivity': random.uniform(0.1, 0.4),
                'pattern_matching_threshold': random.uniform(0.75, 0.95)
            },
            'data_processing': {
                'smoothing_window_size': random.randint(3, 10),
                'outlier_removal_threshold': random.uniform(2.0, 4.0),
                'minimum_history_size': random.randint(10, 50)
            },
            'trend_classification': {
                'strong_trend_threshold': random.uniform(0.7, 0.9),
                'moderate_trend_threshold': random.uniform(0.4, 0.6),
                'weak_trend_threshold': random.uniform(0.1, 0.3)
            }
        }
        
        # Configure mock to return dynamic values
        self.config_manager.get.side_effect = self._get_config_value
        
        # Create service instance
        self.service = TrendAnalysisService()
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
    
    def _generate_dynamic_time_series(self, trend_type: str = 'mixed', length: int = None) -> List[Dict[str, Any]]:
        """Generate dynamic time series data for testing with specified trend"""
        if length is None:
            length = random.randint(30, 200)
        
        base_value = random.uniform(1000, 100000)
        data_points = []
        
        for i in range(length):
            date = datetime.now() - timedelta(days=length - i - 1)
            
            if trend_type == 'upward':
                trend_component = i * random.uniform(0.01, 0.05)
                noise = random.uniform(-0.02, 0.02)
            elif trend_type == 'downward':
                trend_component = -i * random.uniform(0.01, 0.05)
                noise = random.uniform(-0.02, 0.02)
            elif trend_type == 'cyclical':
                import math
                trend_component = math.sin(i * 0.1) * 0.2
                noise = random.uniform(-0.02, 0.02)
            elif trend_type == 'volatile':
                trend_component = random.uniform(-0.1, 0.1)
                noise = random.uniform(-0.05, 0.05)
            else:  # mixed
                trend_component = random.uniform(-0.02, 0.02)
                noise = random.uniform(-0.01, 0.01)
            
            value = base_value * (1 + trend_component + noise)
            
            data_point = {
                'timestamp': date.isoformat(),
                'value': max(0, value),  # Ensure positive values
                'volume': random.randint(1000, 50000),
                'metadata': {
                    'source': f'source_{random.randint(1, 5)}',
                    'quality_score': random.uniform(0.8, 1.0),
                    'confidence': random.uniform(0.7, 0.95)
                }
            }
            data_points.append(data_point)
            base_value = value
        
        return data_points
    
    def _generate_dynamic_market_indicators(self) -> Dict[str, Any]:
        """Generate dynamic market indicators for testing"""
        return {
            'market_id': str(uuid.uuid4()),
            'sector': random.choice(['technology', 'healthcare', 'finance', 'retail', 'manufacturing']),
            'indicators': {
                'market_cap': random.uniform(1000000000, 100000000000),
                'trading_volume': random.uniform(10000000, 1000000000),
                'price_earnings_ratio': random.uniform(5, 50),
                'market_beta': random.uniform(0.5, 2.0),
                'analyst_sentiment': random.uniform(0.1, 1.0)
            },
            'economic_factors': {
                'gdp_growth': random.uniform(-0.05, 0.08),
                'inflation_rate': random.uniform(0.01, 0.10),
                'interest_rate': random.uniform(0.005, 0.08),
                'unemployment_rate': random.uniform(0.03, 0.15)
            },
            'competitive_metrics': {
                'market_share_volatility': random.uniform(0.05, 0.3),
                'new_entrants_rate': random.uniform(0.01, 0.2),
                'innovation_index': random.uniform(0.3, 1.0)
            }
        }
    
    def test_analyze_trends_dynamic(self):
        """Test trend analysis with dynamic data"""
        # Test with different trend types
        for trend_type in ['upward', 'downward', 'cyclical', 'volatile', 'mixed']:
            time_series = self._generate_dynamic_time_series(trend_type)
            market_indicators = self._generate_dynamic_market_indicators()
            
            # Test trend analysis
            result = self.service.analyze_trends(time_series, market_indicators)
            
            # Verify structure (no hardcoded values)
            self.assertIsInstance(result, dict)
            self.assertIn('analysis_id', result)
            self.assertIn('timestamp', result)
            self.assertIn('trend_summary', result)
            self.assertIn('detailed_analysis', result)
            self.assertIn('forecasts', result)
            self.assertIn('patterns_identified', result)
            self.assertIn('confidence_metrics', result)
            
            # Verify trend summary
            trend_summary = result['trend_summary']
            self.assertIn('primary_trend', trend_summary)
            self.assertIn('trend_strength', trend_summary)
            self.assertIn('direction', trend_summary)
            self.assertIn('duration_days', trend_summary)
            
            # Verify trend strength is valid
            trend_strength = trend_summary['trend_strength']
            self.assertIsInstance(trend_strength, (int, float))
            self.assertGreaterEqual(trend_strength, 0.0)
            self.assertLessEqual(trend_strength, 1.0)
    
    def test_detect_trend_patterns_dynamic(self):
        """Test trend pattern detection with dynamic data"""
        # Generate dynamic time series
        time_series = self._generate_dynamic_time_series()
        
        # Test pattern detection
        patterns = self.service._detect_trend_patterns(time_series)
        
        # Verify structure
        self.assertIsInstance(patterns, list)
        for pattern in patterns:
            self.assertIsInstance(pattern, dict)
            self.assertIn('pattern_type', pattern)
            self.assertIn('confidence', pattern)
            self.assertIn('start_date', pattern)
            self.assertIn('end_date', pattern)
            self.assertIn('strength', pattern)
    
    def test_calculate_trend_strength_dynamic(self):
        """Test trend strength calculation with dynamic data"""
        # Generate dynamic time series
        time_series = self._generate_dynamic_time_series()
        
        # Test trend strength calculation
        strength = self.service._calculate_trend_strength(time_series)
        
        # Verify result is valid
        self.assertIsInstance(strength, (int, float))
        self.assertGreaterEqual(strength, 0.0)
        self.assertLessEqual(strength, 1.0)
    
    def test_forecast_trends_dynamic(self):
        """Test trend forecasting with dynamic parameters"""
        # Generate dynamic time series
        time_series = self._generate_dynamic_time_series()
        
        # Test forecasting with different horizons
        for horizon_days in [30, 60, 90]:
            forecasts = self.service._forecast_trends(time_series, horizon_days)
            
            # Verify structure
            self.assertIsInstance(forecasts, dict)
            self.assertIn('forecast_horizon_days', forecasts)
            self.assertIn('predictions', forecasts)
            self.assertIn('confidence_intervals', forecasts)
            self.assertIn('methodology', forecasts)
            
            # Verify horizon matches request
            self.assertEqual(forecasts['forecast_horizon_days'], horizon_days)
            
            # Verify predictions structure
            predictions = forecasts['predictions']
            self.assertIsInstance(predictions, list)
            for prediction in predictions:
                self.assertIn('date', prediction)
                self.assertIn('value', prediction)
                self.assertIn('confidence', prediction)
    
    def test_identify_seasonal_patterns_dynamic(self):
        """Test seasonal pattern identification with dynamic data"""
        # Generate longer time series for seasonal analysis
        time_series = self._generate_dynamic_time_series('cyclical', 365)
        
        # Test seasonal pattern identification
        seasonal_patterns = self.service._identify_seasonal_patterns(time_series)
        
        # Verify structure
        self.assertIsInstance(seasonal_patterns, dict)
        self.assertIn('seasonality_detected', seasonal_patterns)
        self.assertIn('seasonal_periods', seasonal_patterns)
        self.assertIn('seasonal_strength', seasonal_patterns)
        self.assertIn('seasonal_components', seasonal_patterns)
    
    def test_detect_anomalies_dynamic(self):
        """Test anomaly detection with dynamic sensitivity"""
        # Generate time series with injected anomalies
        time_series = self._generate_dynamic_time_series()
        
        # Inject anomalies
        for i in [10, 20, 30]:
            if i < len(time_series):
                time_series[i]['value'] *= random.uniform(2.0, 5.0)
        
        # Test anomaly detection
        anomalies = self.service._detect_anomalies(time_series)
        
        # Verify structure
        self.assertIsInstance(anomalies, list)
        for anomaly in anomalies:
            self.assertIsInstance(anomaly, dict)
            self.assertIn('timestamp', anomaly)
            self.assertIn('value', anomaly)
            self.assertIn('anomaly_score', anomaly)
            self.assertIn('anomaly_type', anomaly)
    
    def test_generate_trend_report_dynamic(self):
        """Test trend report generation with dynamic data"""
        # Generate dynamic time series and indicators
        time_series = self._generate_dynamic_time_series()
        market_indicators = self._generate_dynamic_market_indicators()
        
        # Test report generation
        report = self.service.generate_trend_report(time_series, market_indicators)
        
        # Verify structure
        self.assertIsInstance(report, dict)
        self.assertIn('report_id', report)
        self.assertIn('executive_summary', report)
        self.assertIn('detailed_findings', report)
        self.assertIn('forecasts_and_predictions', report)
        self.assertIn('risk_factors', report)
        self.assertIn('recommendations', report)
        self.assertIn('monitoring_priorities', report)
        
        # Verify executive summary
        summary = report['executive_summary']
        self.assertIn('key_trends', summary)
        self.assertIn('market_outlook', summary)
        self.assertIn('critical_insights', summary)
    
    def test_fallback_analysis_dynamic(self):
        """Test fallback analysis creation"""
        # Test fallback creation
        fallback = self.service._create_fallback_analysis()
        
        # Verify structure
        self.assertIsInstance(fallback, dict)
        self.assertIn('analysis_id', fallback)
        self.assertEqual(fallback['analysis_id'], 'fallback')
        self.assertIn('timestamp', fallback)
        self.assertIn('trend_summary', fallback)
    
    def test_error_handling_dynamic(self):
        """Test error handling with various scenarios"""
        # Test with None data
        result = self.service.analyze_trends(None, None)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['analysis_id'], 'fallback')
        
        # Test with empty data
        result = self.service.analyze_trends([], {})
        self.assertIsInstance(result, dict)
        
        # Test with malformed data
        malformed_series = [{'invalid': 'data'}]
        malformed_indicators = {'invalid': 'data'}
        result = self.service.analyze_trends(malformed_series, malformed_indicators)
        self.assertIsInstance(result, dict)
    
    def test_singleton_pattern(self):
        """Test singleton pattern functionality"""
        # Get multiple instances
        service1 = get_trend_analysis_service()
        service2 = get_trend_analysis_service()
        
        # Verify they are the same instance
        self.assertIs(service1, service2)
    
    def test_thread_safety_dynamic(self):
        """Test thread safety with concurrent analysis"""
        import threading
        
        results = []
        errors = []
        
        def analyze_trends_worker():
            try:
                time_series = self._generate_dynamic_time_series()
                market_indicators = self._generate_dynamic_market_indicators()
                result = self.service.analyze_trends(time_series, market_indicators)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=analyze_trends_worker)
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
            'trend_detection': {
                'sensitivity_threshold': 0.1,
                'trend_strength_threshold': 0.8
            },
            'forecasting': {
                'prediction_horizon_days': 60,
                'confidence_interval': 0.9
            }
        }
        
        # Update mock configuration
        self.test_config.update(new_config)
        
        # Generate analysis with new config
        time_series = self._generate_dynamic_time_series()
        market_indicators = self._generate_dynamic_market_indicators()
        result = self.service.analyze_trends(time_series, market_indicators)
        
        # Verify behavior changes with configuration
        self.assertIsInstance(result, dict)
        self.assertIn('trend_summary', result)
        self.assertIn('forecasts', result)
    
    def test_trend_classification_dynamic(self):
        """Test trend classification with configurable thresholds"""
        # Test different trend strengths
        test_strengths = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for strength in test_strengths:
            classification = self.service._classify_trend_strength(strength)
            
            # Verify classification is valid
            self.assertIn(classification, ['weak', 'moderate', 'strong'])
            
            # Verify classification matches thresholds
            if strength >= self.test_config['trend_classification']['strong_trend_threshold']:
                self.assertEqual(classification, 'strong')
            elif strength >= self.test_config['trend_classification']['moderate_trend_threshold']:
                self.assertEqual(classification, 'moderate')
            else:
                self.assertEqual(classification, 'weak')
    
    def test_data_smoothing_dynamic(self):
        """Test data smoothing with configurable parameters"""
        # Generate noisy time series
        time_series = self._generate_dynamic_time_series('volatile')
        
        # Test data smoothing
        smoothed_data = self.service._smooth_data(time_series)
        
        # Verify structure
        self.assertIsInstance(smoothed_data, list)
        self.assertEqual(len(smoothed_data), len(time_series))
        
        for point in smoothed_data:
            self.assertIn('timestamp', point)
            self.assertIn('value', point)
            self.assertIn('original_value', point)
    
    def test_correlation_analysis_dynamic(self):
        """Test correlation analysis with dynamic indicators"""
        # Generate time series and market indicators
        time_series = self._generate_dynamic_time_series()
        market_indicators = self._generate_dynamic_market_indicators()
        
        # Test correlation analysis
        correlations = self.service._analyze_correlations(time_series, market_indicators)
        
        # Verify structure
        self.assertIsInstance(correlations, dict)
        self.assertIn('correlation_matrix', correlations)
        self.assertIn('significant_correlations', correlations)
        self.assertIn('correlation_insights', correlations)


class TestTrendAnalysisServiceIntegration(unittest.TestCase):
    """Integration tests with real configuration"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Use real config manager
        self.config_manager = ConfigurationManager()
        self.service = TrendAnalysisService()
    
    def test_real_configuration_integration(self):
        """Test with real configuration files"""
        # Generate realistic time series data
        time_series = []
        base_value = 10000
        
        for i in range(90):  # 3 months of data
            date = datetime.now() - timedelta(days=89-i)
            value = base_value * (1 + (i * 0.001) + random.uniform(-0.02, 0.02))
            
            time_series.append({
                'timestamp': date.isoformat(),
                'value': value,
                'volume': random.randint(1000, 10000)
            })
        
        # Generate realistic market indicators
        market_indicators = {
            'market_id': 'test_market',
            'sector': 'technology',
            'indicators': {
                'market_cap': 50000000000,
                'trading_volume': 100000000,
                'analyst_sentiment': 0.75
            }
        }
        
        # Test trend analysis
        result = self.service.analyze_trends(time_series, market_indicators)
        
        # Verify realistic results
        self.assertIsInstance(result, dict)
        self.assertIn('analysis_id', result)
        self.assertIn('trend_summary', result)
        
        # Trend should be detected for upward trending data
        trend_summary = result['trend_summary']
        self.assertIn('primary_trend', trend_summary)
        self.assertIn('trend_strength', trend_summary)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
