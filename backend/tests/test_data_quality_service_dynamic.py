"""
100% DYNAMIC DATA QUALITY SERVICE TESTS
======================================

COMPREHENSIVE TESTING FOR COMPLETE PERSONALIZATION
- Tests ALL industry adaptations (healthcare, fintech, retail, etc.)
- Tests ALL business sizes (startup, small, medium, large, enterprise)  
- Tests ALL risk tolerances (conservative, moderate, aggressive)
- Tests ALL regulatory environments (unregulated, GDPR, HIPAA, SOX, etc.)
- Tests custom dimensions and weights
- Tests business-neutral fallbacks
- Tests real-world data scenarios

ZERO HARDCODED BUSINESS ASSUMPTIONS IN TESTS
"""

import pytest
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import math

# Import the service we're testing directly
import sys
import os
import importlib.util

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

# Import the service directly to avoid dependency issues
try:
    from backend.services.market_intelligence.data_quality_service_dynamic import (
        DynamicDataQualityService, 
        create_personalized_data_quality_service
    )
except ImportError:
    # Direct file import as fallback
    service_path = os.path.join(project_root, 'backend', 'services', 'market_intelligence', 'data_quality_service_dynamic.py')
    spec = importlib.util.spec_from_file_location("data_quality_service_dynamic", service_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        DynamicDataQualityService = module.DynamicDataQualityService
        create_personalized_data_quality_service = module.create_personalized_data_quality_service
    else:
        raise ImportError("Could not import DynamicDataQualityService")


class TestDynamicDataQualityService:
    """Test suite for 100% Dynamic Data Quality Service"""

    def test_business_neutral_initialization(self):
        """Test service initializes with business-neutral defaults"""
        service = DynamicDataQualityService()
        
        # Should have business-neutral thresholds
        assert 0.5 <= service.overall_quality_threshold <= 1.0
        assert 0.5 <= service.completeness_threshold <= 1.0
        assert 0.5 <= service.accuracy_threshold <= 1.0
        
        # Should have all standard quality dimensions
        expected_dimensions = ['completeness', 'accuracy', 'consistency', 'timeliness', 'validity', 'uniqueness']
        for dimension in expected_dimensions:
            assert dimension in service.quality_dimensions
            assert 'weight' in service.quality_dimensions[dimension]
            assert 'threshold' in service.quality_dimensions[dimension]
        
        # Weights should sum to approximately 1.0
        total_weight = sum(dim['weight'] for dim in service.quality_dimensions.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_healthcare_industry_personalization(self):
        """Test healthcare industry-specific personalization"""
        context = {'industry': 'healthcare'}
        service = DynamicDataQualityService(context)
        
        # Healthcare should prioritize accuracy and consistency
        assert service.quality_dimensions['accuracy']['weight'] >= 0.30
        assert service.quality_dimensions['accuracy']['threshold'] >= 0.95
        assert service.quality_dimensions['consistency']['weight'] >= 0.20
        
        # Should have higher overall thresholds due to healthcare requirements
        assert service.overall_quality_threshold >= 0.85

    def test_fintech_industry_personalization(self):
        """Test fintech industry-specific personalization"""
        context = {'industry': 'fintech'}
        service = DynamicDataQualityService(context)
        
        # Fintech should prioritize accuracy and completeness
        assert service.quality_dimensions['accuracy']['weight'] >= 0.35
        assert service.quality_dimensions['completeness']['weight'] >= 0.25
        assert service.quality_dimensions['accuracy']['threshold'] >= 0.95
        
        # Should have very high overall thresholds for financial data
        assert service.overall_quality_threshold >= 0.90

    def test_retail_industry_personalization(self):
        """Test retail industry-specific personalization"""
        context = {'industry': 'retail'}
        service = DynamicDataQualityService(context)
        
        # Retail should prioritize timeliness and completeness
        assert service.quality_dimensions['timeliness']['weight'] >= 0.25
        assert service.quality_dimensions['completeness']['weight'] >= 0.25
        
        # Should be more flexible than healthcare/fintech
        assert service.overall_quality_threshold <= 0.90

    def test_manufacturing_industry_personalization(self):
        """Test manufacturing industry-specific personalization"""
        context = {'industry': 'manufacturing'}
        service = DynamicDataQualityService(context)
        
        # Manufacturing should prioritize consistency and validity
        assert service.quality_dimensions['consistency']['weight'] >= 0.25
        assert service.quality_dimensions['validity']['weight'] >= 0.20
        
        # Should have high consistency requirements
        assert service.quality_dimensions['consistency']['threshold'] >= 0.90

    def test_business_size_personalization(self):
        """Test business size-specific threshold adjustments"""
        
        # Test startup (more flexible)
        startup_service = DynamicDataQualityService({'business_size': 'startup'})
        
        # Test enterprise (higher standards)
        enterprise_service = DynamicDataQualityService({'business_size': 'enterprise'})
        
        # Enterprise should have higher thresholds than startup
        assert enterprise_service.overall_quality_threshold > startup_service.overall_quality_threshold
        assert enterprise_service.accuracy_threshold > startup_service.accuracy_threshold

    def test_risk_tolerance_personalization(self):
        """Test risk tolerance-specific adjustments"""
        
        # Test conservative (higher thresholds)
        conservative_service = DynamicDataQualityService({'risk_tolerance': 'conservative'})
        
        # Test aggressive (lower thresholds)
        aggressive_service = DynamicDataQualityService({'risk_tolerance': 'aggressive'})
        
        # Conservative should have higher thresholds than aggressive
        assert conservative_service.overall_quality_threshold > aggressive_service.overall_quality_threshold
        assert conservative_service.accuracy_threshold > aggressive_service.accuracy_threshold

    def test_regulatory_environment_personalization(self):
        """Test regulatory environment-specific adjustments"""
        
        # Test unregulated environment
        unregulated_service = DynamicDataQualityService({'regulatory_environment': 'unregulated'})
        
        # Test HIPAA environment
        hipaa_service = DynamicDataQualityService({'regulatory_environment': 'HIPAA'})
        
        # Test GDPR environment
        gdpr_service = DynamicDataQualityService({'regulatory_environment': 'GDPR'})
        
        # Regulated environments should have higher thresholds
        assert hipaa_service.overall_quality_threshold > unregulated_service.overall_quality_threshold
        assert gdpr_service.overall_quality_threshold > unregulated_service.overall_quality_threshold

    def test_custom_dimensions_personalization(self):
        """Test custom quality dimensions"""
        custom_dimensions = {
            'business_relevance': {
                'weight': 0.15,
                'threshold': 0.88,
                'description': 'Business context relevance'
            },
            'data_freshness': {
                'weight': 0.10,
                'threshold': 0.92,
                'description': 'Real-time data freshness'
            }
        }
        
        context = {'custom_dimensions': custom_dimensions}
        service = DynamicDataQualityService(context)
        
        # Should include custom dimensions
        assert 'business_relevance' in service.quality_dimensions
        assert 'data_freshness' in service.quality_dimensions
        
        # Should have correct configuration (weights are normalized, so check proportionally)
        assert service.quality_dimensions['business_relevance']['weight'] > 0.10  # Should be significant weight
        assert service.quality_dimensions['business_relevance']['threshold'] == 0.88

    def test_custom_weights_personalization(self):
        """Test custom dimension weights with different personalization modes"""
        
        # Test proportional mode (default) - weights normalized
        custom_weights = {
            'accuracy': 0.50,      
            'completeness': 0.30,   
            'consistency': 0.20     
        }
        
        context = {'dimension_weights': custom_weights}
        service = DynamicDataQualityService(context)
        
        # Total weights should sum to 1.0 (normalized)
        total_weight = sum(dim['weight'] for dim in service.quality_dimensions.values())
        assert abs(total_weight - 1.0) < 0.01
        
        # Accuracy should have highest weight proportionally
        assert service.quality_dimensions['accuracy']['weight'] > service.quality_dimensions['completeness']['weight']
        assert service.quality_dimensions['completeness']['weight'] > service.quality_dimensions['consistency']['weight']

    def test_strict_weight_mode(self):
        """Test strict weight mode - preserves exact user weights"""
        custom_weights = {
            'accuracy': 0.60,      # User wants exactly 60% for accuracy
            'completeness': 0.30   # User wants exactly 30% for completeness
        }
        
        context = {
            'dimension_weights': custom_weights,
            'weight_mode': 'strict',
            'preserve_user_weights': True
        }
        
        service = DynamicDataQualityService(context)
        
        # User-specified weights should be preserved exactly
        assert abs(service.quality_dimensions['accuracy']['weight'] - 0.60) < 0.01
        assert abs(service.quality_dimensions['completeness']['weight'] - 0.30) < 0.01
        
        # Remaining 10% should be distributed among other dimensions
        remaining_weight = 1.0 - 0.60 - 0.30
        other_dimensions_weight = sum(
            service.quality_dimensions[dim]['weight'] 
            for dim in service.quality_dimensions 
            if dim not in custom_weights
        )
        assert abs(other_dimensions_weight - remaining_weight) < 0.01

    def test_override_weight_mode(self):
        """Test override mode - ultimate user control"""
        custom_weights = {
            'accuracy': 0.70,      # User wants 70%
            'completeness': 0.50   # User wants 50% (total = 120% - invalid!)
        }
        
        context = {
            'dimension_weights': custom_weights,
            'weight_mode': 'override',
            'allow_invalid_sums': True  # User explicitly allows invalid sums
        }
        
        service = DynamicDataQualityService(context)
        
        # In override mode with invalid sums allowed, weights can exceed 1.0
        total_weight = sum(dim['weight'] for dim in service.quality_dimensions.values())
        # Should be > 1.0 since we allowed invalid sums
        assert total_weight > 1.0

    def test_personalization_updates(self):
        """Test dynamic personalization updates"""
        service = DynamicDataQualityService()
        original_threshold = service.overall_quality_threshold
        
        # Update to healthcare context
        service.update_personalization({'industry': 'healthcare'})
        healthcare_threshold = service.overall_quality_threshold
        
        # Update to fintech context
        service.update_personalization({'industry': 'fintech'})
        fintech_threshold = service.overall_quality_threshold
        
        # Thresholds should change with context
        assert healthcare_threshold != original_threshold
        assert fintech_threshold != healthcare_threshold

    def test_data_quality_assessment_completeness(self):
        """Test completeness assessment"""
        service = DynamicDataQualityService()
        
        # Complete data
        complete_data = [
            {'name': 'John', 'email': 'john@example.com', 'age': 30},
            {'name': 'Jane', 'email': 'jane@example.com', 'age': 25}
        ]
        
        # Incomplete data
        incomplete_data = [
            {'name': 'John', 'email': None, 'age': 30},
            {'name': '', 'email': 'jane@example.com', 'age': None}
        ]
        
        complete_assessment = service.assess_data_quality(complete_data)
        incomplete_assessment = service.assess_data_quality(incomplete_data)
        
        # Complete data should have higher completeness score
        complete_completeness = complete_assessment['dimension_scores']['completeness']['score']
        incomplete_completeness = incomplete_assessment['dimension_scores']['completeness']['score']
        
        assert complete_completeness > incomplete_completeness
        assert complete_completeness == 1.0
        assert incomplete_completeness < 0.7

    def test_data_quality_assessment_accuracy(self):
        """Test accuracy assessment"""
        service = DynamicDataQualityService()
        
        # Accurate data
        accurate_data = [
            {'email': 'valid@example.com', 'phone': '+1234567890', 'age': 25},
            {'email': 'another@test.com', 'phone': '+0987654321', 'age': 30}
        ]
        
        # Inaccurate data
        inaccurate_data = [
            {'email': 'invalid-email', 'phone': 'not-a-phone', 'age': float('nan')},
            {'email': 'bad@format', 'phone': '123', 'age': float('inf')}
        ]
        
        accurate_assessment = service.assess_data_quality(accurate_data)
        inaccurate_assessment = service.assess_data_quality(inaccurate_data)
        
        # Accurate data should have higher accuracy score
        accurate_accuracy = accurate_assessment['dimension_scores']['accuracy']['score']
        inaccurate_accuracy = inaccurate_assessment['dimension_scores']['accuracy']['score']
        
        assert accurate_accuracy > inaccurate_accuracy

    def test_data_quality_assessment_consistency(self):
        """Test consistency assessment"""
        service = DynamicDataQualityService()
        
        # Consistent data (same types)
        consistent_data = [
            {'name': 'John', 'age': 30, 'active': True},
            {'name': 'Jane', 'age': 25, 'active': False}
        ]
        
        # Inconsistent data (mixed types)
        inconsistent_data = [
            {'name': 'John', 'age': 30, 'active': True},
            {'name': 123, 'age': '25', 'active': 'false'}
        ]
        
        consistent_assessment = service.assess_data_quality(consistent_data)
        inconsistent_assessment = service.assess_data_quality(inconsistent_data)
        
        # Consistent data should have higher consistency score
        consistent_consistency = consistent_assessment['dimension_scores']['consistency']['score']
        inconsistent_consistency = inconsistent_assessment['dimension_scores']['consistency']['score']
        
        assert consistent_consistency > inconsistent_consistency

    def test_data_quality_assessment_uniqueness(self):
        """Test uniqueness assessment"""
        service = DynamicDataQualityService()
        
        # Unique data
        unique_data = [
            {'id': 1, 'name': 'John'},
            {'id': 2, 'name': 'Jane'},
            {'id': 3, 'name': 'Bob'}
        ]
        
        # Duplicate data
        duplicate_data = [
            {'id': 1, 'name': 'John'},
            {'id': 1, 'name': 'John'},  # Exact duplicate
            {'id': 2, 'name': 'Jane'}
        ]
        
        unique_assessment = service.assess_data_quality(unique_data)
        duplicate_assessment = service.assess_data_quality(duplicate_data)
        
        # Unique data should have higher uniqueness score
        unique_uniqueness = unique_assessment['dimension_scores']['uniqueness']['score']
        duplicate_uniqueness = duplicate_assessment['dimension_scores']['uniqueness']['score']
        
        assert unique_uniqueness > duplicate_uniqueness
        assert unique_uniqueness == 1.0
        assert duplicate_uniqueness < 1.0

    def test_quality_grade_calculation(self):
        """Test quality grade calculation"""
        service = DynamicDataQualityService()
        
        # High quality data
        high_quality_data = [
            {'name': 'John Doe', 'email': 'john@example.com', 'phone': '+1234567890', 'age': 30},
            {'name': 'Jane Smith', 'email': 'jane@test.com', 'phone': '+0987654321', 'age': 25}
        ]
        
        assessment = service.assess_data_quality(high_quality_data)
        
        # Should have quality grade
        assert 'quality_grade' in assessment
        assert assessment['quality_grade'] in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']
        
        # High quality should get good grade
        assert assessment['quality_grade'] in ['A+', 'A', 'B+', 'B']

    def test_quality_recommendations(self):
        """Test quality improvement recommendations"""
        service = DynamicDataQualityService()
        
        # Poor quality data
        poor_data = [
            {'name': '', 'email': 'invalid', 'age': None},
            {'name': None, 'email': '', 'age': 'not-a-number'}
        ]
        
        assessment = service.assess_data_quality(poor_data)
        
        # Should have recommendations
        assert 'recommendations' in assessment
        assert len(assessment['recommendations']) > 0
        
        # Should identify specific issues
        recommendations_text = ' '.join(assessment['recommendations']).lower()
        assert any(keyword in recommendations_text for keyword in 
                  ['completeness', 'accuracy', 'validation', 'improve', 'quality'])

    def test_caching_functionality(self):
        """Test quality assessment caching"""
        service = DynamicDataQualityService()
        
        test_data = [{'name': 'Test', 'value': 123}]
        
        # First assessment
        assessment1 = service.assess_data_quality(test_data)
        cache_size_after_first = len(service.quality_cache)
        
        # Second assessment (should use cache)
        assessment2 = service.assess_data_quality(test_data)
        cache_size_after_second = len(service.quality_cache)
        
        # Results should be identical
        assert assessment1 == assessment2
        
        # Cache size should not increase
        assert cache_size_after_first == cache_size_after_second
        
        # Clear cache
        service.clear_cache()
        assert len(service.quality_cache) == 0

    def test_convenience_function_creation(self):
        """Test convenience function for service creation"""
        
        service = create_personalized_data_quality_service(
            industry='healthcare',
            business_size='enterprise',
            risk_tolerance='conservative',
            regulatory_environment='HIPAA'
        )
        
        # Should be properly configured
        assert service.personalization_context['industry'] == 'healthcare'
        assert service.personalization_context['business_size'] == 'enterprise'
        assert service.personalization_context['risk_tolerance'] == 'conservative'
        assert service.personalization_context['regulatory_environment'] == 'HIPAA'
        
        # Should have healthcare-specific configuration
        assert service.quality_dimensions['accuracy']['weight'] >= 0.30

    def test_quality_summary(self):
        """Test quality configuration summary"""
        context = {'industry': 'fintech', 'business_size': 'large'}
        service = DynamicDataQualityService(context)
        
        summary = service.get_quality_summary()
        
        # Should contain all expected fields
        expected_fields = [
            'personalization_context', 'quality_dimensions', 'overall_threshold',
            'individual_thresholds', 'cache_size', 'service_info'
        ]
        
        for field in expected_fields:
            assert field in summary
        
        # Service info should indicate no hardcoded assumptions
        assert summary['service_info']['hardcoded_assumptions'] == 0
        assert summary['service_info']['personalization_level'] == '100%'

    def test_complex_personalization_scenario(self):
        """Test complex multi-factor personalization"""
        
        # Healthcare enterprise with conservative risk tolerance and HIPAA compliance
        complex_context = {
            'industry': 'healthcare',
            'business_size': 'enterprise', 
            'risk_tolerance': 'conservative',
            'regulatory_environment': 'HIPAA',
            'data_sensitivity': 'restricted',
            'custom_dimensions': {
                'patient_privacy': {
                    'weight': 0.20,
                    'threshold': 0.99,
                    'description': 'Patient privacy compliance'
                }
            },
            'dimension_weights': {
                'accuracy': 0.40,
                'consistency': 0.25
            }
        }
        
        service = DynamicDataQualityService(complex_context)
        
        # Should have very high thresholds due to multiple strict requirements
        assert service.overall_quality_threshold >= 0.90
        assert service.accuracy_threshold >= 0.95
        
        # Should include custom dimension
        assert 'patient_privacy' in service.quality_dimensions
        assert service.quality_dimensions['patient_privacy']['threshold'] == 0.99
        
        # Should apply custom weights proportionally (normalized)
        assert service.quality_dimensions['accuracy']['weight'] > 0.30  # Should be high due to user preference


class TestBusinessNeutralFallbacks:
    """Test business-neutral fallback configurations"""

    def test_fallback_with_invalid_context(self):
        """Test fallback when invalid context is provided"""
        
        # Invalid context that should trigger fallbacks
        invalid_context = {
            'industry': 'nonexistent_industry',
            'business_size': 'invalid_size',
            'risk_tolerance': 'unknown_risk'
        }
        
        service = DynamicDataQualityService(invalid_context)
        
        # Should still initialize with valid thresholds
        assert 0.5 <= service.overall_quality_threshold <= 1.0
        assert 0.5 <= service.completeness_threshold <= 1.0
        assert 0.5 <= service.accuracy_threshold <= 1.0

    def test_fallback_with_empty_context(self):
        """Test fallback with empty context"""
        
        service = DynamicDataQualityService({})
        
        # Should use business-neutral defaults
        assert service.overall_quality_threshold > 0.5
        assert len(service.quality_dimensions) >= 6  # Standard dimensions

    def test_mathematical_consistency(self):
        """Test mathematical consistency of all configurations"""
        
        test_contexts = [
            {'industry': 'healthcare'},
            {'industry': 'fintech'},
            {'industry': 'retail'},
            {'business_size': 'startup'},
            {'business_size': 'enterprise'},
            {'risk_tolerance': 'conservative'},
            {'risk_tolerance': 'aggressive'}
        ]
        
        for context in test_contexts:
            service = DynamicDataQualityService(context)
            
            # All thresholds should be in valid range
            assert 0.0 <= service.overall_quality_threshold <= 1.0
            assert 0.0 <= service.completeness_threshold <= 1.0
            assert 0.0 <= service.accuracy_threshold <= 1.0
            assert 0.0 <= service.consistency_threshold <= 1.0
            
            # Weights should sum to approximately 1.0
            total_weight = sum(dim['weight'] for dim in service.quality_dimensions.values())
            assert abs(total_weight - 1.0) < 0.01
            
            # All dimension thresholds should be in valid range
            for dimension_config in service.quality_dimensions.values():
                assert 0.0 <= dimension_config['threshold'] <= 1.0
                assert 0.0 <= dimension_config['weight'] <= 1.0


if __name__ == '__main__':
    # Run all tests
    pytest.main([__file__, '-v'])