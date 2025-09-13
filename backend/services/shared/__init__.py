"""
Shared Services Module
Centralized, reusable AI and business intelligence services for the VERTICAL-LIGHT-OS platform.

This module provides modular, scalable services that can be shared across different components:
- Market Intelligence: Real-time market data and analysis
- Semantic Analysis: Advanced semantic vector processing and business profile generation
- Intelligence Engine: Pattern recognition and adaptive learning
- Strategic Synthesis: Strategic insight generation and business intelligence
- Learning Services: Adaptive learning and pattern-based optimization
- Optimization Engine: Advanced optimization algorithms for campaigns and processes
"""

# Import main service classes for easy access
from backend.services.market_intelligence import MarketDataEngine, get_market_data_engine
from .semantic import SemanticVector, ContextualEntity, DynamicBusinessProfile, SemanticAnalyzer
from .intelligence import DynamicIntelligenceEngine, get_intelligence_engine
from .synthesis import StrategicSynthesizer, get_strategic_synthesizer
from backend.services.learning import AdaptiveLearner, get_adaptive_learner
from backend.services.optimization import OptimizationEngine, get_optimization_engine

__all__ = [
    # Market Intelligence
    'MarketDataEngine',
    'get_market_data_engine',
    
    # Semantic Services
    'SemanticVector',
    'ContextualEntity', 
    'DynamicBusinessProfile',
    'SemanticAnalyzer',
    
    # Intelligence Services
    'DynamicIntelligenceEngine',
    'get_intelligence_engine',
    
    # Synthesis Services
    'StrategicSynthesizer',
    'get_strategic_synthesizer',
    
    # Learning Services
    'AdaptiveLearner',
    'get_adaptive_learner',
    
    # Optimization Services
    'OptimizationEngine',
    'get_optimization_engine'
]
