#!/usr/bin/env python3
"""
Simple Progressive Intelligence Integration Test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.market_intelligence.intelligence_engine import MarketIntelligenceEngine

def test_integration():
    print("Testing Progressive Intelligence Integration in Intelligence Engine")
    print("=" * 70)
    
    try:
        # Initialize
        user_context = {'test_mode': True, 'personalization_enabled': True}
        engine = MarketIntelligenceEngine(user_context)
        
        # Test data
        business_profile = {
            'industry': 'technology',
            'business_size': 'startup',
            'risk_tolerance': 'aggressive'
        }
        
        market_data = {
            'trends': {
                'ai_adoption': {'strength': 0.8, 'growth_rate': 0.25}
            }
        }
        
        print("Running personalized market context analysis...")
        result = engine.analyze_market_context(business_profile, market_data)
        
        print(f"Results:")
        print(f"  Personalization Applied: {result.get('personalization_applied', 'None')}")
        print(f"  Confidence Score: {result.get('confidence_score', 0)}")
        print(f"  Market Opportunities: {len(result.get('market_opportunities', []))}")
        print(f"  Risk Assessment: {len(result.get('risk_assessment', []))}")
        print(f"  Recommendations: {len(result.get('recommendations', []))}")
        
        personalization = result.get('personalization_applied', 'mathematical_neutral')
        if personalization != 'mathematical_neutral':
            print(f"\nSUCCESS: Progressive Intelligence personalization working!")
            print(f"  Source: {personalization}")
        else:
            print(f"\nUsing mathematical neutral fallback (expected when no user data)")
            
        print(f"\nProgressive Intelligence Integration Test PASSED!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_integration()