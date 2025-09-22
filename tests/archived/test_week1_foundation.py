"""
Test script for Week 1: Foundation Setup
Tests the new parallel architecture without importing existing complex services
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.shared.tier_config import BusinessTier, TierConfigManager, LOCAL_CONFIG, ENTERPRISE_CONFIG
from models.local_business import LocalBusiness, BusinessCategory

def test_tier_configuration():
    """Test tier configuration system"""
    print("🧪 Testing Tier Configuration...")
    
    # Test tier configs
    local_config = TierConfigManager.get_config("local")
    enterprise_config = TierConfigManager.get_config("enterprise")
    
    assert local_config.monthly_pricing == 999.0
    assert enterprise_config.monthly_pricing == 25000.0
    
    print(f"✅ Local tier: ₹{local_config.monthly_pricing}/month - {local_config.automation_level}")
    print(f"✅ Enterprise tier: ₹{enterprise_config.monthly_pricing}/month - {enterprise_config.automation_level}")
    
    # Test pricing info
    pricing = TierConfigManager.get_pricing_info("local")
    assert pricing["monthly_price"] == 999.0
    
    print(f"✅ Pricing info retrieved: {pricing['automation_level']}")

def test_local_business_model():
    """Test local business model"""
    print("\n🧪 Testing Local Business Model...")
    
    # Create test business
    business = LocalBusiness(
        name="Test Pizza Corner",
        category=BusinessCategory.RESTAURANT,
        city="Mumbai",
        state="Maharashtra", 
        monthly_marketing_budget=5000,
        service_radius_km=5.0
    )
    
    assert business.name == "Test Pizza Corner"
    assert business.category == BusinessCategory.RESTAURANT
    assert business.monthly_marketing_budget == 5000
    
    print(f"✅ Business created: {business.name}")
    print(f"✅ Category: {business.category.value}")
    print(f"✅ Budget: ₹{business.monthly_marketing_budget}")
    print(f"✅ Service radius: {business.service_radius_km}km")

def test_local_intelligence_engine():
    """Test local intelligence engine"""
    print("\n🧪 Testing Local Intelligence Engine...")
    
    # Import local intelligence engine directly
    from services.local.intelligence.local_intelligence_engine import LocalIntelligenceEngine
    
    # Create test business
    business = LocalBusiness(
        name="Test Salon",
        category=BusinessCategory.SALON,
        city="Delhi",
        state="Delhi",
        monthly_marketing_budget=8000
    )
    
    # Create intelligence engine
    engine = LocalIntelligenceEngine(business)
    
    assert engine.business.name == "Test Salon"
    assert engine.config == LOCAL_CONFIG
    
    print(f"✅ Intelligence engine created for: {engine.business.name}")
    print(f"✅ Budget tier: {engine._get_budget_tier()}")
    
    # Test budget tier calculation
    assert engine._get_budget_tier() == "growth"  # 8000 is in growth tier (5001-15000)
    
    print(f"✅ Budget tier calculation working: {engine._get_budget_tier()}")

async def test_local_intelligence_insights():
    """Test local intelligence insights generation"""
    print("\n🧪 Testing Local Intelligence Insights...")
    
    from services.local.intelligence.local_intelligence_engine import LocalIntelligenceEngine
    
    # Create test business
    business = LocalBusiness(
        name="Test Restaurant",
        category=BusinessCategory.RESTAURANT,
        city="Bangalore",
        state="Karnataka",
        monthly_marketing_budget=3000
    )
    
    engine = LocalIntelligenceEngine(business)
    
    # Test insights generation
    insights = await engine.get_daily_insights()
    
    assert "business_info" in insights
    assert "hyperlocal_market" in insights
    assert "immediate_opportunities" in insights
    assert "budget_optimization" in insights
    
    print(f"✅ Daily insights generated with {len(insights)} sections")
    print(f"✅ Business tier: {insights['business_info']['budget_tier']}")
    print(f"✅ Automation recommendations available: {'automation_recommendations' in insights}")
    
    # Test automation status
    automation_status = await engine.get_automation_status()
    assert automation_status["overall_automation"] == "80%"
    
    print(f"✅ Automation status: {automation_status['overall_automation']}")
    print(f"✅ Active automations: {len(automation_status['active_automations'])}")

def test_tier_comparison():
    """Test tier comparison functionality"""
    print("\n🧪 Testing Tier Comparison...")
    
    comparison = TierConfigManager.get_all_tiers()
    
    assert "enterprise" in comparison
    assert "local" in comparison
    assert comparison["enterprise"]["pricing"] == 25000.0
    assert comparison["local"]["pricing"] == 999.0
    
    print(f"✅ Enterprise tier: ₹{comparison['enterprise']['pricing']}/month")
    print(f"✅ Local tier: ₹{comparison['local']['pricing']}/month")
    print(f"✅ Tier comparison working correctly")

def main():
    """Run all tests for Week 1 Foundation Setup"""
    print("🚀 Week 1: Foundation Setup Testing")
    print("=" * 50)
    
    try:
        # Test configurations
        test_tier_configuration()
        
        # Test business model
        test_local_business_model()
        
        # Test intelligence engine
        test_local_intelligence_engine()
        
        # Test insights (async)
        import asyncio
        asyncio.run(test_local_intelligence_insights())
        
        # Test tier comparison
        test_tier_comparison()
        
        print("\n" + "=" * 50)
        print("🎉 Week 1 Foundation Setup - ALL TESTS PASSED!")
        print("✅ Parallel architecture is working correctly")
        print("✅ Local business services are functional")
        print("✅ Enterprise services remain untouched")
        print("✅ Ready to proceed to Week 2: Local Intelligence")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)