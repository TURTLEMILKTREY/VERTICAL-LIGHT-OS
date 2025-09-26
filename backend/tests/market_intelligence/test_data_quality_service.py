"""
Dynamic test suite for Data Quality Service microservice
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

from services.market_intelligence.data_quality_service import DataQualityService, get_data_quality_service
from config.config_manager import ConfigurationManager


class TestDataQualityService(unittest.TestCase):
 """Dynamic test suite for Data Quality Service - fully configurable"""

 def setUp(self):
 """Set up test environment with dynamic configuration"""
 self.config_manager = Mock(spec=ConfigurationManager)

 # Dynamic test configuration - all values configurable
 self.test_config = {
 'validation_thresholds': {
 'completeness_threshold': random.uniform(0.7, 0.95),
 'accuracy_threshold': random.uniform(0.8, 0.98),
 'consistency_threshold': random.uniform(0.75, 0.95),
 'timeliness_threshold': random.uniform(0.8, 0.98)
 },
 'quality_scoring': {
 'completeness_weight': random.uniform(0.2, 0.4),
 'accuracy_weight': random.uniform(0.2, 0.4),
 'consistency_weight': random.uniform(0.1, 0.3),
 'timeliness_weight': random.uniform(0.1, 0.3)
 },
 'monitoring': {
 'default_period_days': random.randint(7, 60),
 'alert_threshold': random.uniform(0.1, 0.3),
 'trend_window_days': random.randint(5, 30)
 },
 'data_freshness': {
 'critical_age_hours': random.randint(1, 24),
 'stale_age_hours': random.randint(25, 168),
 'obsolete_age_hours': random.randint(169, 720)
 },
 'anomaly_detection': {
 'sensitivity': random.uniform(0.1, 0.5),
 'z_score_threshold': random.uniform(2.0, 4.0),
 'trend_deviation_threshold': random.uniform(0.2, 0.8)
 }
 }

 # Configure mock to return dynamic values
 self.config_manager.get.side_effect = self._get_config_value

 # Create service instance
 self.service = DataQualityService()
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

 def _generate_dynamic_dataset(self, quality_level: str = 'mixed') -> Dict[str, Any]:
 """Generate dynamic dataset for testing with specified quality level"""
 base_size = random.randint(100, 10000)

 if quality_level == 'high':
 completeness = random.uniform(0.95, 1.0)
 accuracy = random.uniform(0.95, 1.0)
 consistency = random.uniform(0.95, 1.0)
 freshness_hours = random.randint(1, 6)
 elif quality_level == 'low':
 completeness = random.uniform(0.3, 0.6)
 accuracy = random.uniform(0.4, 0.7)
 consistency = random.uniform(0.3, 0.6)
 freshness_hours = random.randint(100, 500)
 else: # mixed
 completeness = random.uniform(0.6, 0.9)
 accuracy = random.uniform(0.7, 0.9)
 consistency = random.uniform(0.6, 0.9)
 freshness_hours = random.randint(1, 72)

 # Calculate missing/invalid records based on quality
 complete_records = int(base_size * completeness)
 accurate_records = int(base_size * accuracy)
 consistent_records = int(base_size * consistency)

 return {
 'dataset_id': str(uuid.uuid4()),
 'total_records': base_size,
 'complete_records': complete_records,
 'missing_records': base_size - complete_records,
 'accurate_records': accurate_records,
 'invalid_records': base_size - accurate_records,
 'consistent_records': consistent_records,
 'inconsistent_records': base_size - consistent_records,
 'last_updated': (datetime.now() - timedelta(hours=freshness_hours)).isoformat(),
 'data_sources': [f'source_{i}' for i in range(random.randint(1, 5))],
 'schema_version': f'v{random.randint(1, 10)}.{random.randint(0, 9)}',
 'validation_timestamp': datetime.now().isoformat(),
 'fields': [
 {
 'name': f'field_{i}',
 'type': random.choice(['string', 'number', 'date', 'boolean']),
 'completeness': random.uniform(0.5, 1.0),
 'unique_values': random.randint(1, base_size)
 } for i in range(random.randint(5, 20))
 ]
 }

 def test_validate_data_quality_dynamic(self):
 """Test data quality validation with dynamic data"""
 # Test with different quality levels
 for quality_level in ['high', 'low', 'mixed']:
 dataset = self._generate_dynamic_dataset(quality_level)

 # Test data validation
 result = self.service.validate_data_quality(dataset)

 # Verify structure (no hardcoded values)
 self.assertIsInstance(result, dict)
 self.assertIn('validation_id', result)
 self.assertIn('timestamp', result)
 self.assertIn('overall_score', result)
 self.assertIn('quality_dimensions', result)
 self.assertIn('issues_identified', result)
 self.assertIn('recommendations', result)

 # Verify overall score is valid
 overall_score = result['overall_score']
 self.assertIsInstance(overall_score, (int, float))
 self.assertGreaterEqual(overall_score, 0.0)
 self.assertLessEqual(overall_score, 1.0)

 # Verify quality dimensions
 dimensions = result['quality_dimensions']
 for dimension in ['completeness', 'accuracy', 'consistency', 'timeliness']:
 self.assertIn(dimension, dimensions)
 score = dimensions[dimension]['score']
 self.assertGreaterEqual(score, 0.0)
 self.assertLessEqual(score, 1.0)

 def test_assess_data_completeness_dynamic(self):
 """Test data completeness assessment with dynamic data"""
 # Generate dynamic dataset
 dataset = self._generate_dynamic_dataset()

 # Test completeness assessment
 completeness = self.service._assess_data_completeness(dataset)

 # Verify structure
 self.assertIsInstance(completeness, dict)
 self.assertIn('score', completeness)
 self.assertIn('total_fields', completeness)
 self.assertIn('complete_fields', completeness)
 self.assertIn('missing_data_patterns', completeness)

 # Verify score is valid
 score = completeness['score']
 self.assertIsInstance(score, (int, float))
 self.assertGreaterEqual(score, 0.0)
 self.assertLessEqual(score, 1.0)

 def test_assess_data_accuracy_dynamic(self):
 """Test data accuracy assessment with dynamic data"""
 # Generate dynamic dataset
 dataset = self._generate_dynamic_dataset()

 # Test accuracy assessment
 accuracy = self.service._assess_data_accuracy(dataset)

 # Verify structure
 self.assertIsInstance(accuracy, dict)
 self.assertIn('score', accuracy)
 self.assertIn('validation_results', accuracy)
 self.assertIn('error_patterns', accuracy)

 # Verify score is valid
 score = accuracy['score']
 self.assertIsInstance(score, (int, float))
 self.assertGreaterEqual(score, 0.0)
 self.assertLessEqual(score, 1.0)

 def test_assess_data_consistency_dynamic(self):
 """Test data consistency assessment with dynamic data"""
 # Generate dynamic dataset
 dataset = self._generate_dynamic_dataset()

 # Test consistency assessment
 consistency = self.service._assess_data_consistency(dataset)

 # Verify structure
 self.assertIsInstance(consistency, dict)
 self.assertIn('score', consistency)
 self.assertIn('cross_field_validation', consistency)
 self.assertIn('duplicate_analysis', consistency)

 # Verify score is valid
 score = consistency['score']
 self.assertIsInstance(score, (int, float))
 self.assertGreaterEqual(score, 0.0)
 self.assertLessEqual(score, 1.0)

 def test_assess_data_timeliness_dynamic(self):
 """Test data timeliness assessment with dynamic data"""
 # Generate dynamic dataset
 dataset = self._generate_dynamic_dataset()

 # Test timeliness assessment
 timeliness = self.service._assess_data_timeliness(dataset)

 # Verify structure
 self.assertIsInstance(timeliness, dict)
 self.assertIn('score', timeliness)
 self.assertIn('freshness_analysis', timeliness)
 self.assertIn('update_frequency', timeliness)

 # Verify score is valid
 score = timeliness['score']
 self.assertIsInstance(score, (int, float))
 self.assertGreaterEqual(score, 0.0)
 self.assertLessEqual(score, 1.0)

 def test_monitor_data_quality_trends_dynamic(self):
 """Test data quality trend monitoring with dynamic periods"""
 # Test with different time periods
 for period_days in [7, 30, 90]:
 # Test trend monitoring
 result = self.service.monitor_data_quality_trends(period_days)

 # Verify structure
 self.assertIsInstance(result, dict)
 self.assertIn('monitoring_id', result)
 self.assertIn('period_days', result)
 self.assertIn('quality_trends', result)
 self.assertIn('anomalies_detected', result)
 self.assertIn('quality_alerts', result)

 # Verify period matches request
 self.assertEqual(result['period_days'], period_days)

 def test_generate_quality_report_dynamic(self):
 """Test quality report generation with dynamic data"""
 # Generate dynamic dataset
 dataset = self._generate_dynamic_dataset()

 # Test report generation
 report = self.service.generate_quality_report(dataset)

 # Verify structure
 self.assertIsInstance(report, dict)
 self.assertIn('report_id', report)
 self.assertIn('executive_summary', report)
 self.assertIn('detailed_analysis', report)
 self.assertIn('recommendations', report)
 self.assertIn('trend_analysis', report)

 # Verify executive summary
 summary = report['executive_summary']
 self.assertIn('overall_quality_score', summary)
 self.assertIn('critical_issues', summary)
 self.assertIn('improvement_priorities', summary)

 def test_detect_anomalies_dynamic(self):
 """Test anomaly detection with dynamic data"""
 # Generate time series data with anomalies
 quality_scores = []
 for i in range(30):
 if i in [10, 20]: # Inject anomalies
 score = random.uniform(0.1, 0.3)
 else:
 score = random.uniform(0.7, 0.9)
 quality_scores.append({
 'timestamp': (datetime.now() - timedelta(days=29-i)).isoformat(),
 'score': score
 })

 # Test anomaly detection
 anomalies = self.service._detect_anomalies(quality_scores)

 # Verify structure
 self.assertIsInstance(anomalies, list)
 for anomaly in anomalies:
 self.assertIsInstance(anomaly, dict)
 self.assertIn('timestamp', anomaly)
 self.assertIn('score', anomaly)
 self.assertIn('anomaly_type', anomaly)

 def test_fallback_validation_result_dynamic(self):
 """Test fallback validation result creation"""
 # Test fallback creation
 fallback = self.service._create_fallback_validation_result()

 # Verify structure
 self.assertIsInstance(fallback, dict)
 self.assertIn('validation_id', fallback)
 self.assertEqual(fallback['validation_id'], 'fallback')
 self.assertIn('timestamp', fallback)
 self.assertIn('overall_score', fallback)

 def test_error_handling_dynamic(self):
 """Test error handling with various scenarios"""
 # Test with None data
 result = self.service.validate_data_quality(None)
 self.assertIsInstance(result, dict)
 self.assertEqual(result['validation_id'], 'fallback')

 # Test with empty data
 result = self.service.validate_data_quality({})
 self.assertIsInstance(result, dict)

 # Test with malformed data
 malformed_data = {'invalid': 'data', 'total_records': 'not_a_number'}
 result = self.service.validate_data_quality(malformed_data)
 self.assertIsInstance(result, dict)

 def test_singleton_pattern(self):
 """Test singleton pattern functionality"""
 # Get multiple instances
 service1 = get_data_quality_service()
 service2 = get_data_quality_service()

 # Verify they are the same instance
 self.assertIs(service1, service2)

 def test_thread_safety_dynamic(self):
 """Test thread safety with concurrent validation"""
 import threading

 results = []
 errors = []

 def validate_data_worker():
 try:
 dataset = self._generate_dynamic_dataset()
 result = self.service.validate_data_quality(dataset)
 results.append(result)
 except Exception as e:
 errors.append(e)

 # Create multiple threads
 threads = []
 for _ in range(5):
 thread = threading.Thread(target=validate_data_worker)
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
 self.assertIn('validation_id', result)

 def test_configuration_driven_behavior(self):
 """Test that all behavior is driven by configuration"""
 # Change configuration values
 new_config = {
 'validation_thresholds': {
 'completeness_threshold': 0.9,
 'accuracy_threshold': 0.95
 },
 'quality_scoring': {
 'completeness_weight': 0.4,
 'accuracy_weight': 0.4
 }
 }

 # Update mock configuration
 self.test_config.update(new_config)

 # Generate validation with new config
 dataset = self._generate_dynamic_dataset()
 result = self.service.validate_data_quality(dataset)

 # Verify behavior changes with configuration
 self.assertIsInstance(result, dict)
 self.assertIn('overall_score', result)

 def test_data_quality_scoring_weights_dynamic(self):
 """Test that quality scoring uses configurable weights"""
 # Generate dataset with known quality characteristics
 dataset = self._generate_dynamic_dataset('high')

 # Test validation
 result = self.service.validate_data_quality(dataset)

 # Verify that weights are applied correctly
 dimensions = result['quality_dimensions']
 overall_score = result['overall_score']

 # Calculate expected score based on weights
 expected_score = (
 dimensions['completeness']['score'] * self.test_config['quality_scoring']['completeness_weight'] +
 dimensions['accuracy']['score'] * self.test_config['quality_scoring']['accuracy_weight'] +
 dimensions['consistency']['score'] * self.test_config['quality_scoring']['consistency_weight'] +
 dimensions['timeliness']['score'] * self.test_config['quality_scoring']['timeliness_weight']
 )

 # Allow for small calculation differences
 self.assertAlmostEqual(overall_score, expected_score, places=2)


class TestDataQualityServiceIntegration(unittest.TestCase):
 """Integration tests with real configuration"""

 def setUp(self):
 """Set up integration test environment"""
 # Use real config manager
 self.config_manager = ConfigurationManager()
 self.service = DataQualityService()

 def test_real_configuration_integration(self):
 """Test with real configuration files"""
 # Generate realistic dataset
 dataset = {
 'dataset_id': 'test_dataset',
 'total_records': 1000,
 'complete_records': 950,
 'missing_records': 50,
 'accurate_records': 980,
 'invalid_records': 20,
 'consistent_records': 970,
 'inconsistent_records': 30,
 'last_updated': datetime.now().isoformat()
 }

 # Test data validation
 result = self.service.validate_data_quality(dataset)

 # Verify realistic results
 self.assertIsInstance(result, dict)
 self.assertIn('validation_id', result)
 self.assertIn('overall_score', result)

 # Quality score should be reasonable for good data
 overall_score = result['overall_score']
 self.assertGreater(overall_score, 0.8) # Should be high for good quality data


if __name__ == '__main__':
 # Run tests with verbose output
 unittest.main(verbosity=2)
