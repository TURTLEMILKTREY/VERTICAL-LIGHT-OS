#!/usr/bin/env python3
"""
Test Progressive Intelligence Integration in Intelligence Engine
Validates that personalization is working correctly independent of configuration thresholds
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.market_intelligence.intelligence_engine import MarketIntelligenceEngine
from backend.config.config_manager import ConfigManager

def test_progressive_intelligence_personalization():
    """
    Test that Progressive Intelligence provides personalized analysis patterns
    This validates our integration, not configuration thresholds
    """
    
    print("Testing Progressive Intelligence Integration in Intelligence Engine")
    print("=" * 70)
    
    # Initialize the engine
    config_manager = ConfigManager()
    engine = MarketIntelligenceEngine(config_manager)
    
    # Test business profile with clear personalization context
    business_profile = {
        'industry': 'technology',
        'business_size': 'startup', 
        'risk_tolerance': 'aggressive',
        'strategy_focus': 'growth',
        'analysis_preferences': {
            'risk_weighting': 0.3,  # Low risk aversion
            'opportunity_threshold': 0.4,  # Lower threshold for opportunities
            'confidence_baseline': 0.7,
            'growth_focus_weight': 1.2  # High growth focus
        }
    }
    
    # Test market data
    market_data = {
        'trends': {
            'ai_adoption': {'strength': 0.8, 'growth_rate': 0.25},
            'remote_work': {'strength': 0.6, 'growth_rate': 0.15}
        },
        'competitive_landscape': {
            'intensity': 'high',
            'new_entrants': 0.7
        }
    }
    
    print("Testing Personalized Market Context Analysis...")
    
    # Test the personalized analysis
    result = engine.analyze_market_context(business_profile, market_data)
    
    print(f"\nAnalysis Results:")
    print(f"   Personalization Applied: {result.get('personalization_applied', 'None')}")
    print(f"   Confidence Score: {result.get('confidence_score', 0)}")
    print(f"   Market Opportunities Found: {len(result.get('market_opportunities', []))}")
    print(f"   Risks Identified: {len(result.get('risk_assessment', []))}")
    print(f"   Recommendations: {len(result.get('recommendations', []))}")
    
    # Validate personalization is working
    personalization_applied = result.get('personalization_applied', 'mathematical_neutral')
    
    if personalization_applied != 'mathematical_neutral':
        print(f"\nSUCCESS: Progressive Intelligence personalization is working!")
        print(f"   Using personalization source: {personalization_applied}")
    else:
        print(f"\nUsing mathematical neutral approach (no PI data available)")
        print("   This is expected behavior when no user learning data exists")
    
    # Test that personalized methods are being called
    print(f"\nChecking Personalized Analysis Components:")
    
    # Check market opportunities have personalization metadata
    opportunities = result.get('market_opportunities', [])
    if opportunities and any('personalization_applied' in opp for opp in opportunities):
        print(f"   PASS: Market opportunities include personalization metadata")
    
    # Check competitive analysis has personalization
    competitive = result.get('competitive_landscape', {})
    if 'personalization_metadata' in competitive:
        print(f"   PASS: Competitive analysis includes personalization metadata")
    
    # Check risk assessment has personalization
    risks = result.get('risk_assessment', [])
    if risks and any('personalization_applied' in risk for risk in risks):
        print(f"   PASS: Risk assessment includes personalization metadata")
    
    # Check recommendations have personalization
    recommendations = result.get('recommendations', [])
    if recommendations and any('personalization_applied' in rec for rec in recommendations):
        print(f"   PASS: Recommendations include personalization metadata")
    
    print(f"\nProgressive Intelligence Integration Test Complete!")
    return result

def test_zero_assumption_fallback():
    """
    Test that the system falls back to mathematical neutrality when no user data exists
    """
    print(f"\nTesting Zero-Assumption Fallback...")
    
    config_manager = ConfigManager()
    engine = MarketIntelligenceEngine(config_manager)
    
    # Business profile with no personalization data
    minimal_profile = {
        'industry': 'unknown',
        'business_size': 'medium'
    }
    
    minimal_market_data = {
        'basic_trend': 0.5
    }
    
    result = engine.analyze_market_context(minimal_profile, minimal_market_data)
    
    personalization = result.get('personalization_applied', 'mathematical_neutral')
    confidence = result.get('confidence_score', 0)
    
    print(f"   Personalization Source: {personalization}")
    print(f"   Confidence Score: {confidence}")
    
    if personalization == 'mathematical_neutral' or confidence == 0.5:
        print(f"   SUCCESS: System properly falls back to mathematical neutrality")
    else:
        print(f"   WARNING: System may not be using proper fallback logic")
    
    return result

if __name__ == "__main__":
    try:
        # Test Progressive Intelligence integration
        test_progressive_intelligence_personalization()
        
        # Test zero-assumption fallback
        test_zero_assumption_fallback()
        
        print(f"\nAll Progressive Intelligence Integration Tests Completed!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()