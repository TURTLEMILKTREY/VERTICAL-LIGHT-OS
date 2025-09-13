"""
Market Intelligence Services Package
Complete microservices architecture for AI-powered market intelligence
100% Dynamic Configuration - Zero Hardcoded Values
"""

# Core market intelligence services
from .intelligence_engine import MarketIntelligenceEngine, get_intelligence_engine
from .competitive_analysis_service import CompetitiveAnalysisService, get_competitive_analysis_service
from .data_quality_service import DataQualityService, get_data_quality_service
from .intelligence_orchestrator import IntelligenceOrchestrator, get_intelligence_orchestrator
from .risk_assessment_service import RiskAssessmentService, get_risk_assessment_service
from .trend_analysis_service import TrendAnalysisService, get_trend_analysis_service
from .market_maturity_service import MarketMaturityService, get_market_maturity_service

# Legacy import for backward compatibility
try:
    from .market_data_engine import MarketDataEngine, get_market_data_engine
except ImportError:
    MarketDataEngine = None
    get_market_data_engine = None

# Service factory functions for easy access
def get_all_intelligence_services():
    """
    Get all market intelligence services as a dictionary
    """
    return {
        'intelligence_engine': get_intelligence_engine(),
        'competitive_analysis': get_competitive_analysis_service(),
        'data_quality': get_data_quality_service(),
        'intelligence_orchestrator': get_intelligence_orchestrator(),
        'risk_assessment': get_risk_assessment_service(),
        'trend_analysis': get_trend_analysis_service(),
        'market_maturity': get_market_maturity_service()
    }

def get_service_by_name(service_name: str):
    """
    Get a specific market intelligence service by name
    
    Args:
        service_name: Name of the service ('intelligence_engine', 'competitive_analysis', 
                     'data_quality', 'intelligence_orchestrator', 'risk_assessment', 
                     'trend_analysis', 'market_maturity')
    
    Returns:
        The requested service instance or None if not found
    """
    services = get_all_intelligence_services()
    return services.get(service_name)

# Export all services and utilities
__all__ = [
    # Service classes
    'MarketIntelligenceEngine',
    'CompetitiveAnalysisService', 
    'DataQualityService',
    'IntelligenceOrchestrator',
    'RiskAssessmentService',
    'TrendAnalysisService',
    'MarketMaturityService',
    
    # Service factory functions
    'get_intelligence_engine',
    'get_competitive_analysis_service',
    'get_data_quality_service',
    'get_intelligence_orchestrator',
    'get_risk_assessment_service',
    'get_trend_analysis_service',
    'get_market_maturity_service',
    
    # Utility functions
    'get_all_intelligence_services',
    'get_service_by_name'
]

# Legacy exports for backward compatibility
if MarketDataEngine:
    __all__.extend(['MarketDataEngine', 'get_market_data_engine'])

# Package metadata
__version__ = '1.0.0'
__author__ = 'Vertical Light OS'
__description__ = 'Enterprise-grade market intelligence microservices architecture'
