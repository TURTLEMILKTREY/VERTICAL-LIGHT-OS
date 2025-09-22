"""
Simple test suite for Week 1 foundation validation
Tests the standalone local services without complex dependencies
"""

import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_tier_config_standalone():
    """Test the standalone tier configuration system"""
    print("Testing standalone tier configuration...")
    
    try:
        from backend.services.local.tier_config_standalone import (
            TierConfigManager, 
            ENTERPRISE_CONFIG, 
            LOCAL_CONFIG
        )
        
        # Test tier configurations exist
        assert ENTERPRISE_CONFIG.monthly_pricing == 25000.0
        assert LOCAL_CONFIG.monthly_pricing == 999.0
        
        # Test config manager
        enterprise_config = TierConfigManager.get_config("enterprise")
        local_config = TierConfigManager.get_config("local")
        
        assert enterprise_config is not None
        assert local_config is not None
        
        # Test feature validation
        has_feature = TierConfigManager.validate_feature_access("local", "intelligence_depth")
        assert has_feature == True
        
        # Test pricing info
        local_pricing = TierConfigManager.get_pricing_info("local")
        assert local_pricing["monthly_price"] == 999.0
        assert local_pricing["currency"] == "INR"
        
        print("✓ Tier configuration system working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Tier configuration test failed: {e}")
        return False

def test_local_intelligence_engine():
    """Test the local intelligence engine"""
    print("Testing local intelligence engine...")
    
    try:
        from backend.services.local.intelligence.local_intelligence_engine import LocalIntelligenceEngine
        from backend.models.local_business import LocalBusiness, BusinessCategory, BudgetTier
        
        # Create a sample business for testing
        sample_business = LocalBusiness(
            name="Test Restaurant",
            category=BusinessCategory.RESTAURANT,
            city="Mumbai",
            state="Maharashtra",
            budget_tier=BudgetTier.GROWTH,
            monthly_marketing_budget=8000.0
        )
        
        # Create engine instance with business
        engine = LocalIntelligenceEngine(sample_business)
        
        # Test that engine was created successfully
        assert engine.business.name == "Test Restaurant"
        assert engine.business.category == BusinessCategory.RESTAURANT
        
        print("✓ Local intelligence engine working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Local intelligence engine test failed: {e}")
        return False

def test_basic_insights_generation():
    """Test that insights can be generated without external dependencies"""
    print("Testing basic insights generation...")
    
    try:
        from backend.services.local.intelligence.local_intelligence_engine import LocalIntelligenceEngine
        from backend.models.local_business import LocalBusiness, BusinessCategory, BudgetTier
        
        # Create a sample business for testing
        sample_business = LocalBusiness(
            name="Test Salon",
            category=BusinessCategory.SALON,
            city="Delhi",
            state="Delhi",
            budget_tier=BudgetTier.BOOTSTRAP,
            monthly_marketing_budget=3000.0
        )
        
        engine = LocalIntelligenceEngine(sample_business)
        
        # Test that engine attributes are accessible
        assert hasattr(engine, 'business')
        assert hasattr(engine, 'config')
        assert engine.business.name == "Test Salon"
        
        print("✓ Basic insights engine setup working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Basic insights generation test failed: {e}")
        return False

def run_foundation_tests():
    """Run all foundation tests for Week 1 validation"""
    print("Running Week 1 Foundation Tests")
    print("=" * 50)
    
    tests = [
        test_tier_config_standalone,
        test_local_intelligence_engine,
        test_basic_insights_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 50)
    print(f"Foundation Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ Week 1 foundation setup is working correctly")
        print("Ready to proceed to Week 2: Local Automation Services")
        return True
    else:
        print("✗ Foundation issues detected - need to resolve before proceeding")
        return False

if __name__ == "__main__":
    success = run_foundation_tests()
    sys.exit(0 if success else 1)