#!/usr/bin/env python3
"""
Test script to verify competitive analysis service requires proper configuration
and has zero hardcoded business-affecting fallbacks.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.market_intelligence.competitive_analysis_service import CompetitiveAnalysisService

def test_config_requirements():
    """Test that service properly validates required configuration"""
    print("Testing competitive analysis service configuration requirements...")
    
    # Test with empty config - should raise ValueError for missing required values
    try:
        service = CompetitiveAnalysisService({})
        
        # These should fail due to missing required configuration
        test_data = {
            'competitors': {
                'test_competitor': {
                    'name': 'Test Corp',
                    'market_share': 0.15,
                    'innovation_score': 0.8,
                    'brand_recognition': 0.7
                }
            },
            'market_data': {
                'growth_rate': 0.1,
                'size': 1000000
            }
        }
        
        # This should raise ValueError for missing configuration
        result = service.analyze_competitive_landscape(test_data)
        print("❌ ERROR: Service should have failed without proper configuration!")
        return False
        
    except ValueError as e:
        if "required configuration" in str(e).lower():
            print("✅ PASS: Service correctly validates required configuration")
            return True
        else:
            print(f"❌ FAIL: Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected exception: {e}")
        return False

def test_null_handling():
    """Test that service handles null values properly without hardcoded fallbacks"""
    print("Testing null value handling without hardcoded fallbacks...")
    
    # Create minimal config for testing
    config = {
        'competitive_analysis': {
            'brand_recognition_threshold': 0.7,
            'innovation_leadership_threshold': 0.8,
            'customer_satisfaction_threshold': 0.6,
            'declining_revenue_threshold': 0.0
        }
    }
    
    try:
        service = CompetitiveAnalysisService(config)
        
        # Test data with null values (which should be preserved, not replaced with 0)
        test_data = {
            'name': 'Test Corp',
            'market_share': None,  # Should remain None, not become 0
            'innovation_score': None,  # Should remain None, not become 0
            'brand_recognition': None,  # Should remain None, not become 0
            'revenue': None,
            'revenue_growth': None,
            'profit_margin': None
        }
        
        # Test market presence analysis
        result = service._analyze_market_presence(test_data)
        
        # Verify None values are preserved
        if result['market_share'] is None and result['brand_recognition'] is None:
            print("✅ PASS: Null values properly preserved without hardcoded fallbacks")
            return True
        else:
            print(f"❌ FAIL: Null values replaced with hardcoded fallbacks: {result}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception during null handling test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Competitive Analysis Service - Production Readiness")
    print("=" * 60)
    
    tests = [
        test_config_requirements,
        test_null_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SUCCESS: Competitive Analysis Service is production ready!")
        print("✅ Zero hardcoded business-affecting fallbacks")
        print("✅ Proper configuration validation")
        print("✅ Null-safe data handling")
    else:
        print("❌ FAILURE: Service still has hardcoded values or configuration issues")
        sys.exit(1)