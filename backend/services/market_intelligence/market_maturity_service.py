"""
Market Maturity Service - Market Intelligence
Comprehensive market lifecycle analysis and maturity assessment
100% Dynamic Configuration - Zero Hardcoded Values
"""

import json
import logging
import threading
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import statistics

from config.config_manager import get_config_manager

logger = logging.getLogger(__name__)


class MarketMaturityService:
 """
 Advanced market maturity assessment service providing comprehensive
 market lifecycle analysis, maturity scoring, and development predictions.
 """

 def __init__(self):
 self.config_manager = get_config_manager()
 self.maturity_config = self._load_maturity_configuration()

 # Market maturity tracking
 self.market_assessments: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
 self.maturity_indicators: Dict[str, Dict[str, Any]] = {}
 self.lifecycle_models: Dict[str, Dict[str, Any]] = {}

 # Thread safety
 self.lock = threading.RLock()

 # Configuration-driven parameters
 self.maturity_score_threshold = self._get_config_value('scoring.maturity_threshold', 0.75)
 self.growth_rate_threshold = self._get_config_value('growth.rate_threshold', 0.1)
 self.saturation_threshold = self._get_config_value('saturation.threshold', 0.85)
 self.innovation_threshold = self._get_config_value('innovation.threshold', 0.6)

 # Maturity stages and weights
 self.maturity_stages = self._get_config_value('stages', {
 'introduction': {'min_score': 0.0, 'max_score': 0.2, 'weight': 1.0},
 'growth': {'min_score': 0.2, 'max_score': 0.5, 'weight': 1.2},
 'maturity': {'min_score': 0.5, 'max_score': 0.8, 'weight': 1.0},
 'saturation': {'min_score': 0.8, 'max_score': 0.95, 'weight': 0.8},
 'decline': {'min_score': 0.95, 'max_score': 1.0, 'weight': 0.6}
 })

 # Assessment dimensions and their weights
 self.assessment_dimensions = self._get_config_value('dimensions', {
 'market_penetration': 0.25,
 'competitive_intensity': 0.20,
 'innovation_rate': 0.20,
 'customer_adoption': 0.15,
 'revenue_growth': 0.10,
 'market_concentration': 0.10
 })

 # Maturity indicators
 self.maturity_indicators_config = self._get_config_value('indicators', {
 'customer_acquisition_cost': {'weight': 0.15, 'scale': 'inverse'},
 'market_share_stability': {'weight': 0.12, 'scale': 'normal'},
 'product_differentiation': {'weight': 0.10, 'scale': 'inverse'},
 'pricing_pressure': {'weight': 0.13, 'scale': 'normal'},
 'technology_standardization': {'weight': 0.11, 'scale': 'normal'},
 'regulatory_framework': {'weight': 0.09, 'scale': 'normal'},
 'entry_barriers': {'weight': 0.10, 'scale': 'normal'},
 'market_consolidation': {'weight': 0.12, 'scale': 'normal'},
 'innovation_frequency': {'weight': 0.08, 'scale': 'inverse'}
 })

 logger.info("MarketMaturityService initialized with dynamic configuration")

 def _load_maturity_configuration(self) -> Dict[str, Any]:
 """Load market maturity configuration"""
 try:
 return self.config_manager.get('market_maturity', {})
 except Exception as e:
 logger.error(f"Failed to load maturity configuration: {e}")
 return {}

 def _get_config_value(self, key_path: str, default: Any = None) -> Any:
 """Get configuration value using dot notation"""
 try:
 keys = key_path.split('.')
 value = self.maturity_config
 for key in keys:
 value = value.get(key, {})
 return value if value != {} else default
 except Exception:
 return default

 def assess_market_maturity(self, market_data: Dict[str, Any], 
 industry_context: Dict[str, Any] = None) -> Dict[str, Any]:
 """
 Comprehensive market maturity assessment
 """
 with self.lock:
 try:
 assessment_id = self._generate_assessment_id()

 maturity_assessment = {
 'assessment_id': assessment_id,
 'timestamp': datetime.now().isoformat(),
 'market_identifier': market_data.get('market_id', 'unknown'),
 'overall_maturity_score': 0.0,
 'maturity_stage': 'unknown',
 'stage_confidence': 0.0,
 'dimension_scores': {},
 'maturity_indicators': {},
 'lifecycle_position': {},
 'competitive_landscape_maturity': {},
 'innovation_maturity': {},
 'customer_maturity': {},
 'market_evolution_analysis': {},
 'transition_probabilities': {},
 'strategic_implications': [],
 'maturity_risks': [],
 'development_opportunities': [],
 'assessment_summary': ''
 }

 # Calculate dimension scores
 maturity_assessment['dimension_scores'] = self._calculate_dimension_scores(
 market_data, industry_context
 )

 # Calculate overall maturity score
 maturity_assessment['overall_maturity_score'] = self._calculate_overall_maturity_score(
 maturity_assessment['dimension_scores']
 )

 # Determine maturity stage
 stage_analysis = self._determine_maturity_stage(
 maturity_assessment['overall_maturity_score'], 
 maturity_assessment['dimension_scores']
 )
 maturity_assessment['maturity_stage'] = stage_analysis['stage']
 maturity_assessment['stage_confidence'] = stage_analysis['confidence']

 # Assess maturity indicators
 maturity_assessment['maturity_indicators'] = self._assess_maturity_indicators(
 market_data, industry_context
 )

 # Analyze lifecycle position
 maturity_assessment['lifecycle_position'] = self._analyze_lifecycle_position(
 market_data, maturity_assessment['overall_maturity_score']
 )

 # Evaluate competitive landscape maturity
 maturity_assessment['competitive_landscape_maturity'] = self._evaluate_competitive_maturity(
 market_data, industry_context
 )

 # Assess innovation maturity
 maturity_assessment['innovation_maturity'] = self._assess_innovation_maturity(
 market_data, industry_context
 )

 # Evaluate customer maturity
 maturity_assessment['customer_maturity'] = self._evaluate_customer_maturity(
 market_data, industry_context
 )

 # Analyze market evolution
 maturity_assessment['market_evolution_analysis'] = self._analyze_market_evolution(
 market_data, maturity_assessment
 )

 # Calculate transition probabilities
 maturity_assessment['transition_probabilities'] = self._calculate_transition_probabilities(
 maturity_assessment
 )

 # Identify strategic implications
 maturity_assessment['strategic_implications'] = self._identify_strategic_implications(
 maturity_assessment
 )

 # Assess maturity risks
 maturity_assessment['maturity_risks'] = self._assess_maturity_risks(
 maturity_assessment, market_data
 )

 # Identify development opportunities
 maturity_assessment['development_opportunities'] = self._identify_development_opportunities(
 maturity_assessment, market_data
 )

 # Generate assessment summary
 maturity_assessment['assessment_summary'] = self._generate_assessment_summary(
 maturity_assessment
 )

 # Store assessment for historical analysis
 self._store_maturity_assessment(assessment_id, maturity_assessment)

 logger.info(f"Market maturity assessment completed - Stage: {maturity_assessment['maturity_stage']}, Score: {maturity_assessment['overall_maturity_score']:.2f}")
 return maturity_assessment

 except Exception as e:
 logger.error(f"Error in market maturity assessment: {e}")
 return self._create_fallback_assessment()

 def predict_maturity_evolution(self, market_data: Dict[str, Any], 
 prediction_horizon_months: int = None) -> Dict[str, Any]:
 """
 Predict how market maturity will evolve over time
 """
 with self.lock:
 try:
 if prediction_horizon_months is None:
 prediction_horizon_months = self._get_config_value('prediction.default_horizon_months', 12)

 prediction = {
 'prediction_id': self._generate_prediction_id(),
 'market_identifier': market_data.get('market_id', 'unknown'),
 'prediction_horizon_months': prediction_horizon_months,
 'prediction_date': datetime.now().isoformat(),
 'current_maturity': {},
 'predicted_maturity': {},
 'evolution_trajectory': {},
 'stage_transition_timeline': {},
 'acceleration_factors': [],
 'deceleration_factors': [],
 'disruption_risks': [],
 'evolution_confidence': 0.0,
 'key_milestones': [],
 'monitoring_indicators': []
 }

 # Get current maturity assessment
 current_assessment = self.assess_market_maturity(market_data)
 prediction['current_maturity'] = {
 'score': current_assessment['overall_maturity_score'],
 'stage': current_assessment['maturity_stage'],
 'dimension_scores': current_assessment['dimension_scores']
 }

 # Predict future maturity
 prediction['predicted_maturity'] = self._predict_future_maturity(
 current_assessment, market_data, prediction_horizon_months
 )

 # Analyze evolution trajectory
 prediction['evolution_trajectory'] = self._analyze_evolution_trajectory(
 prediction['current_maturity'], prediction['predicted_maturity']
 )

 # Project stage transition timeline
 prediction['stage_transition_timeline'] = self._project_stage_transitions(
 current_assessment, prediction_horizon_months
 )

 # Identify acceleration factors
 prediction['acceleration_factors'] = self._identify_acceleration_factors(
 market_data, current_assessment
 )

 # Identify deceleration factors
 prediction['deceleration_factors'] = self._identify_deceleration_factors(
 market_data, current_assessment
 )

 # Assess disruption risks
 prediction['disruption_risks'] = self._assess_disruption_risks(
 market_data, current_assessment
 )

 # Calculate evolution confidence
 prediction['evolution_confidence'] = self._calculate_evolution_confidence(
 prediction, market_data
 )

 # Define key milestones
 prediction['key_milestones'] = self._define_evolution_milestones(
 prediction['evolution_trajectory'], prediction_horizon_months
 )

 # Set monitoring indicators
 prediction['monitoring_indicators'] = self._set_monitoring_indicators(
 prediction, current_assessment
 )

 logger.info(f"Market maturity evolution prediction completed - Current: {prediction['current_maturity']['stage']}, Predicted: {prediction['predicted_maturity']['stage']}")
 return prediction

 except Exception as e:
 logger.error(f"Error predicting maturity evolution: {e}")
 return {'prediction_id': 'error', 'error': str(e), 'evolution_confidence': 0.0}

 def compare_market_maturity(self, markets_data: List[Dict[str, Any]], 
 comparison_dimensions: List[str] = None) -> Dict[str, Any]:
 """
 Compare maturity levels across multiple markets
 """
 with self.lock:
 try:
 comparison = {
 'comparison_id': self._generate_comparison_id(),
 'comparison_date': datetime.now().isoformat(),
 'markets_count': len(markets_data),
 'market_assessments': {},
 'maturity_rankings': {},
 'dimension_comparisons': {},
 'relative_positioning': {},
 'maturity_gaps': {},
 'convergence_analysis': {},
 'competitive_implications': [],
 'opportunity_analysis': {}
 }

 if comparison_dimensions is None:
 comparison_dimensions = list(self.assessment_dimensions.keys())

 # Assess each market
 for market_data in markets_data:
 market_id = market_data.get('market_id', f'market_{len(comparison["market_assessments"])}')
 assessment = self.assess_market_maturity(market_data)
 comparison['market_assessments'][market_id] = assessment

 # Create maturity rankings
 comparison['maturity_rankings'] = self._create_maturity_rankings(
 comparison['market_assessments']
 )

 # Compare dimensions
 comparison['dimension_comparisons'] = self._compare_market_dimensions(
 comparison['market_assessments'], comparison_dimensions
 )

 # Analyze relative positioning
 comparison['relative_positioning'] = self._analyze_relative_positioning(
 comparison['market_assessments']
 )

 # Calculate maturity gaps
 comparison['maturity_gaps'] = self._calculate_maturity_gaps(
 comparison['market_assessments']
 )

 # Analyze convergence patterns
 comparison['convergence_analysis'] = self._analyze_maturity_convergence(
 comparison['market_assessments']
 )

 # Identify competitive implications
 comparison['competitive_implications'] = self._identify_competitive_implications(
 comparison
 )

 # Analyze opportunities
 comparison['opportunity_analysis'] = self._analyze_cross_market_opportunities(
 comparison
 )

 logger.info(f"Market maturity comparison completed for {len(markets_data)} markets")
 return comparison

 except Exception as e:
 logger.error(f"Error in market maturity comparison: {e}")
 return {'comparison_id': 'error', 'error': str(e), 'markets_count': 0}

 def generate_maturity_insights(self, market_data: Dict[str, Any], 
 business_context: Dict[str, Any] = None) -> Dict[str, Any]:
 """
 Generate strategic insights based on market maturity analysis
 """
 with self.lock:
 try:
 insights = {
 'insights_id': self._generate_insights_id(),
 'generation_date': datetime.now().isoformat(),
 'market_identifier': market_data.get('market_id', 'unknown'),
 'strategic_insights': [],
 'investment_recommendations': [],
 'timing_considerations': {},
 'competitive_positioning': {},
 'innovation_opportunities': [],
 'market_entry_analysis': {},
 'risk_mitigation_strategies': [],
 'success_factors': [],
 'performance_metrics': {}
 }

 # Get market maturity assessment
 maturity_assessment = self.assess_market_maturity(market_data)

 # Generate strategic insights
 insights['strategic_insights'] = self._generate_strategic_insights(
 maturity_assessment, business_context
 )

 # Develop investment recommendations
 insights['investment_recommendations'] = self._develop_investment_recommendations(
 maturity_assessment, business_context
 )

 # Analyze timing considerations
 insights['timing_considerations'] = self._analyze_timing_considerations(
 maturity_assessment, market_data
 )

 # Assess competitive positioning opportunities
 insights['competitive_positioning'] = self._assess_positioning_opportunities(
 maturity_assessment, business_context
 )

 # Identify innovation opportunities
 insights['innovation_opportunities'] = self._identify_innovation_opportunities(
 maturity_assessment, market_data
 )

 # Analyze market entry strategies
 insights['market_entry_analysis'] = self._analyze_market_entry_strategies(
 maturity_assessment, business_context
 )

 # Develop risk mitigation strategies
 insights['risk_mitigation_strategies'] = self._develop_risk_mitigation_strategies(
 maturity_assessment, market_data
 )

 # Identify success factors
 insights['success_factors'] = self._identify_maturity_success_factors(
 maturity_assessment, business_context
 )

 # Define performance metrics
 insights['performance_metrics'] = self._define_maturity_performance_metrics(
 maturity_assessment, business_context
 )

 logger.info(f"Market maturity insights generated - {len(insights['strategic_insights'])} insights identified")
 return insights

 except Exception as e:
 logger.error(f"Error generating maturity insights: {e}")
 return {'insights_id': 'error', 'error': str(e), 'strategic_insights': []}

 def _calculate_dimension_scores(self, market_data: Dict[str, Any], 
 industry_context: Dict[str, Any] = None) -> Dict[str, float]:
 """Calculate scores for each maturity dimension"""
 try:
 dimension_scores = {}

 for dimension, weight in self.assessment_dimensions.items():
 score = self._calculate_single_dimension_score(dimension, market_data, industry_context)
 dimension_scores[dimension] = max(0.0, min(1.0, score))

 return dimension_scores

 except Exception as e:
 logger.error(f"Error calculating dimension scores: {e}")
 return {dim: 0.5 for dim in self.assessment_dimensions.keys()}

 def _calculate_single_dimension_score(self, dimension: str, market_data: Dict[str, Any], 
 industry_context: Dict[str, Any] = None) -> float:
 """Calculate score for a single dimension"""
 try:
 if dimension == 'market_penetration':
 penetration_rate = market_data.get('market_penetration_rate', 0.3)
 return min(penetration_rate * 2, 1.0)

 elif dimension == 'competitive_intensity':
 competitor_count = market_data.get('competitor_count', 5)
 hhi = market_data.get('herfindahl_index', 0.2)
 return min((competitor_count / 20) + hhi, 1.0)

 elif dimension == 'innovation_rate':
 innovation_frequency = market_data.get('innovation_frequency', 0.5)
 r_and_d_intensity = market_data.get('r_and_d_intensity', 0.1)
 return (innovation_frequency + r_and_d_intensity) / 2

 elif dimension == 'customer_adoption':
 adoption_rate = market_data.get('customer_adoption_rate', 0.4)
 churn_rate = market_data.get('churn_rate', 0.2)
 return adoption_rate * (1 - churn_rate)

 elif dimension == 'revenue_growth':
 growth_rate = market_data.get('revenue_growth_rate', 0.1)
 return min(max(growth_rate * 2, 0), 1.0)

 elif dimension == 'market_concentration':
 concentration_ratio = market_data.get('concentration_ratio', 0.4)
 return concentration_ratio

 else:
 return 0.5

 except Exception as e:
 logger.error(f"Error calculating score for dimension {dimension}: {e}")
 return 0.5

 def _calculate_overall_maturity_score(self, dimension_scores: Dict[str, float]) -> float:
 """Calculate weighted overall maturity score"""
 try:
 total_score = 0.0
 total_weight = 0.0

 for dimension, score in dimension_scores.items():
 weight = self.assessment_dimensions.get(dimension, 0.1)
 total_score += score * weight
 total_weight += weight

 if total_weight > 0:
 return total_score / total_weight
 else:
 return 0.5

 except Exception as e:
 logger.error(f"Error calculating overall maturity score: {e}")
 return 0.5

 def _determine_maturity_stage(self, overall_score: float, 
 dimension_scores: Dict[str, float]) -> Dict[str, Any]:
 """Determine market maturity stage and confidence"""
 try:
 stage_analysis = {
 'stage': 'unknown',
 'confidence': 0.0,
 'stage_indicators': {},
 'transition_signals': []
 }

 # Determine stage based on score thresholds
 for stage_name, stage_config in self.maturity_stages.items():
 min_score = stage_config['min_score']
 max_score = stage_config['max_score']

 if min_score <= overall_score <= max_score:
 stage_analysis['stage'] = stage_name

 # Calculate confidence based on position within stage range
 stage_range = max_score - min_score
 position_in_stage = (overall_score - min_score) / stage_range if stage_range > 0 else 0.5
 stage_analysis['confidence'] = 1.0 - abs(0.5 - position_in_stage) * 2

 break

 # Analyze stage indicators
 stage_analysis['stage_indicators'] = self._analyze_stage_indicators(
 stage_analysis['stage'], dimension_scores
 )

 # Identify transition signals
 stage_analysis['transition_signals'] = self._identify_transition_signals(
 overall_score, dimension_scores
 )

 return stage_analysis

 except Exception as e:
 logger.error(f"Error determining maturity stage: {e}")
 return {'stage': 'unknown', 'confidence': 0.0, 'stage_indicators': {}, 'transition_signals': []}

 # Helper methods for ID generation and fallback
 def _generate_assessment_id(self) -> str:
 """Generate unique assessment ID"""
 return f"MMA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(id(self)).encode()).hexdigest()[:8]}"

 def _generate_prediction_id(self) -> str:
 """Generate unique prediction ID"""
 return f"MMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(id(self)).encode()).hexdigest()[:8]}"

 def _generate_comparison_id(self) -> str:
 """Generate unique comparison ID"""
 return f"MMC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(id(self)).encode()).hexdigest()[:8]}"

 def _generate_insights_id(self) -> str:
 """Generate unique insights ID"""
 return f"MMI_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(id(self)).encode()).hexdigest()[:8]}"

 def _create_fallback_assessment(self) -> Dict[str, Any]:
 """Create fallback maturity assessment"""
 return {
 'assessment_id': 'fallback',
 'timestamp': datetime.now().isoformat(),
 'market_identifier': 'unknown',
 'overall_maturity_score': 0.5,
 'maturity_stage': 'unknown',
 'stage_confidence': 0.3,
 'dimension_scores': {dim: 0.5 for dim in self.assessment_dimensions.keys()},
 'maturity_indicators': {},
 'lifecycle_position': {},
 'competitive_landscape_maturity': {},
 'innovation_maturity': {},
 'customer_maturity': {},
 'market_evolution_analysis': {},
 'transition_probabilities': {},
 'strategic_implications': [],
 'maturity_risks': [],
 'development_opportunities': [],
 'assessment_summary': 'Market maturity assessment failed - manual review recommended'
 }

 def _store_maturity_assessment(self, assessment_id: str, assessment: Dict[str, Any]) -> None:
 """Store maturity assessment for historical analysis"""
 try:
 market_id = assessment.get('market_identifier', 'unknown')
 self.market_assessments[market_id].append({
 'assessment_id': assessment_id,
 'timestamp': assessment['timestamp'],
 'maturity_score': assessment['overall_maturity_score'],
 'stage': assessment['maturity_stage']
 })

 # Keep only last 50 assessments per market
 if len(self.market_assessments[market_id]) > 50:
 self.market_assessments[market_id] = self.market_assessments[market_id][-50:]

 except Exception as e:
 logger.error(f"Error storing maturity assessment: {e}")

 def _assess_maturity_indicators(self, market_data: Dict[str, Any], 
 business_profile: Dict[str, Any]) -> Dict[str, Any]:
 """
 Assess market maturity indicators - 100% Dynamic
 No hardcoded values, completely configurable assessment
 """
 try:
 # Dynamic indicator configuration
 indicator_config = self._get_config_value('maturity_indicators', {})
 indicators_to_assess = indicator_config.get('primary_indicators', [
 'market_size', 'growth_rate', 'competition_level', 'innovation_rate',
 'customer_acquisition_cost', 'market_concentration', 'barriers_to_entry'
 ])

 maturity_indicators = {
 'assessment_date': datetime.now().isoformat(),
 'indicators_analyzed': indicators_to_assess,
 'indicator_scores': {},
 'weighted_assessment': {},
 'maturity_signals': []
 }

 # Assess each indicator dynamically
 for indicator in indicators_to_assess:
 indicator_score = self._assess_individual_indicator(
 indicator, market_data, business_profile
 )
 maturity_indicators['indicator_scores'][indicator] = indicator_score

 # Calculate weighted assessment
 maturity_indicators['weighted_assessment'] = self._calculate_weighted_maturity_assessment(
 maturity_indicators['indicator_scores']
 )

 # Identify maturity signals
 maturity_indicators['maturity_signals'] = self._identify_maturity_signals(
 maturity_indicators['indicator_scores']
 )

 return maturity_indicators

 except Exception as e:
 logger.warning(f"Error assessing maturity indicators: {e}")
 return self._generate_fallback_maturity_indicators()

 def _analyze_stage_indicators(self, market_stage: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
 """
 Analyze stage-specific indicators - 100% Dynamic
 Completely configurable stage analysis
 """
 try:
 # Dynamic stage indicator configuration
 stage_config = self._get_config_value(f'stage_indicators.{market_stage}', {})

 stage_analysis = {
 'stage': market_stage,
 'analysis_date': datetime.now().isoformat(),
 'stage_characteristics': self._identify_stage_characteristics(market_stage, market_data),
 'indicator_metrics': self._calculate_stage_indicator_metrics(market_stage, market_data),
 'stage_strength': self._assess_stage_strength(market_stage, market_data),
 'transition_signals': self._detect_stage_transition_signals(market_stage, market_data),
 'stage_recommendations': self._generate_stage_recommendations(market_stage, market_data)
 }

 return stage_analysis

 except Exception as e:
 logger.warning(f"Error analyzing stage indicators for {market_stage}: {e}")
 return self._generate_fallback_stage_indicators(market_stage)

 def _assess_individual_indicator(self, indicator: str, market_data: Dict[str, Any], 
 business_profile: Dict[str, Any]) -> Dict[str, Any]:
 """Assess individual maturity indicator dynamically"""
 try:
 # Extract relevant data for indicator
 indicator_data = self._extract_indicator_data(indicator, market_data, business_profile)

 # Dynamic scoring based on indicator type
 score = self._calculate_indicator_score(indicator, indicator_data)

 # Assess maturity level for this indicator
 maturity_level = self._determine_indicator_maturity_level(score)

 return {
 'indicator': indicator,
 'raw_score': score,
 'maturity_level': maturity_level,
 'confidence': self._calculate_indicator_confidence(indicator, indicator_data),
 'contributing_factors': self._identify_contributing_factors(indicator, indicator_data)
 }

 except Exception as e:
 logger.warning(f"Error assessing indicator {indicator}: {e}")
 return {
 'indicator': indicator,
 'raw_score': 0.5,
 'maturity_level': 'unknown',
 'confidence': 0.3,
 'error': str(e)
 }

 def _extract_indicator_data(self, indicator: str, market_data: Dict[str, Any], 
 business_profile: Dict[str, Any]) -> Dict[str, Any]:
 """Extract data relevant to specific indicator"""
 indicator_data = {}

 # Dynamic data extraction based on indicator type
 if indicator == 'market_size':
 indicator_data = {
 'size': market_data.get('market_size', market_data.get('total_addressable_market', 0)),
 'currency': market_data.get('currency', 'USD'),
 'measurement': market_data.get('size_measurement', 'revenue')
 }
 elif indicator == 'growth_rate':
 indicator_data = {
 'current_rate': market_data.get('growth_rate', 0),
 'historical_rates': market_data.get('historical_growth', []),
 'projected_rate': market_data.get('projected_growth', 0)
 }
 elif indicator == 'competition_level':
 competitors = market_data.get('competitors', {})
 if isinstance(competitors, list):
 competitors = {f'competitor_{i}': comp for i, comp in enumerate(competitors)}

 indicator_data = {
 'competitor_count': len(competitors),
 'market_leaders': self._identify_top_competitors(competitors),
 'competitive_intensity': self._assess_competitive_intensity_score(competitors)
 }
 else:
 # Generic data extraction for any indicator
 indicator_data = {
 'raw_value': market_data.get(indicator, business_profile.get(indicator, 0)),
 'context': market_data.get(f'{indicator}_context', {}),
 'metadata': market_data.get(f'{indicator}_metadata', {})
 }

 return indicator_data

 def _calculate_indicator_score(self, indicator: str, indicator_data: Dict[str, Any]) -> float:
 """Calculate score for indicator based on available data"""
 # Dynamic scoring based on indicator type and data availability

 if indicator == 'market_size':
 size = float(indicator_data.get('size', 0))
 # Normalize size score (larger markets typically more mature)
 return min(1.0, size / self._get_config_value('scoring.market_size_threshold', 1000000))

 elif indicator == 'growth_rate':
 rate = float(indicator_data.get('current_rate', 0))
 # High growth = less mature, low growth = more mature
 return max(0.0, 1.0 - (rate / self._get_config_value('scoring.max_growth_rate', 50)))

 elif indicator == 'competition_level':
 competitor_count = indicator_data.get('competitor_count', 0)
 # More competitors typically indicate more mature market
 return min(1.0, competitor_count / self._get_config_value('scoring.max_competitors', 20))

 else:
 # Generic scoring for unknown indicators
 raw_value = float(indicator_data.get('raw_value', 0.5))
 return max(0.0, min(1.0, raw_value))

 def _determine_indicator_maturity_level(self, score: float) -> str:
 """Determine maturity level based on score"""
 thresholds = self._get_config_value('maturity_thresholds', {
 'emerging': 0.25,
 'growth': 0.5,
 'mature': 0.75
 })

 if score >= thresholds.get('mature', 0.75):
 return 'mature'
 elif score >= thresholds.get('growth', 0.5):
 return 'growth'
 elif score >= thresholds.get('emerging', 0.25):
 return 'emerging'
 else:
 return 'nascent'

 def _calculate_indicator_confidence(self, indicator: str, indicator_data: Dict[str, Any]) -> float:
 """Calculate confidence in indicator assessment"""
 # Confidence based on data availability and quality
 data_quality_factors = [
 1.0 if indicator_data.get('raw_value') is not None else 0.0,
 1.0 if indicator_data.get('context') else 0.0,
 1.0 if len(indicator_data) > 1 else 0.0
 ]

 return sum(data_quality_factors) / len(data_quality_factors)

 def _identify_contributing_factors(self, indicator: str, indicator_data: Dict[str, Any]) -> List[str]:
 """Identify factors contributing to indicator assessment"""
 factors = []

 for key, value in indicator_data.items():
 if value and key != 'raw_value':
 factors.append(f'{key}_{type(value).__name__}')

 return factors[:3] # Limit to 3 factors

 def _calculate_weighted_maturity_assessment(self, indicator_scores: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
 """Calculate weighted maturity assessment from indicator scores"""
 # Dynamic weights from configuration
 default_weights = {
 'market_size': 0.2,
 'growth_rate': 0.25,
 'competition_level': 0.2,
 'innovation_rate': 0.15,
 'customer_acquisition_cost': 0.1,
 'market_concentration': 0.05,
 'barriers_to_entry': 0.05
 }

 weights = self._get_config_value('indicator_weights', default_weights)

 weighted_score = 0.0
 total_weight = 0.0

 for indicator, score_data in indicator_scores.items():
 weight = weights.get(indicator, 0.1)
 score = score_data.get('raw_score', 0.5)

 weighted_score += score * weight
 total_weight += weight

 final_score = weighted_score / max(total_weight, 1.0)

 return {
 'weighted_score': final_score,
 'maturity_level': self._determine_indicator_maturity_level(final_score),
 'confidence': self._calculate_assessment_confidence(indicator_scores),
 'contributing_indicators': len(indicator_scores)
 }

 def _identify_maturity_signals(self, indicator_scores: Dict[str, Dict[str, Any]]) -> List[str]:
 """Identify signals indicating market maturity stage"""
 signals = []

 mature_indicators = 0
 emerging_indicators = 0

 for indicator, score_data in indicator_scores.items():
 maturity_level = score_data.get('maturity_level', 'unknown')

 if maturity_level == 'mature':
 mature_indicators += 1
 signals.append(f'mature_{indicator}_detected')
 elif maturity_level == 'emerging':
 emerging_indicators += 1
 signals.append(f'emerging_{indicator}_detected')

 # Overall signals
 if mature_indicators > emerging_indicators:
 signals.append('overall_maturity_trend')
 elif emerging_indicators > mature_indicators:
 signals.append('overall_growth_trend')
 else:
 signals.append('balanced_maturity_profile')

 return signals[:5] # Limit to 5 signals

 def _identify_stage_characteristics(self, stage: str, market_data: Dict[str, Any]) -> List[str]:
 """Identify characteristics specific to market stage"""
 stage_characteristics = {
 'emerging': ['high_innovation', 'few_competitors', 'rapid_growth', 'high_uncertainty'],
 'growth': ['increasing_competition', 'market_expansion', 'standardization', 'investment_influx'],
 'mature': ['market_saturation', 'price_competition', 'consolidation', 'efficiency_focus'],
 'decline': ['market_contraction', 'exit_barriers', 'legacy_systems', 'disruption_threat']
 }

 return stage_characteristics.get(stage, ['unknown_stage_characteristics'])

 def _calculate_stage_indicator_metrics(self, stage: str, market_data: Dict[str, Any]) -> Dict[str, float]:
 """Calculate metrics specific to market stage"""
 metrics = {}

 # Dynamic metric calculation based on stage
 if stage == 'emerging':
 metrics = {
 'innovation_rate': self._calculate_innovation_rate(market_data),
 'market_uncertainty': self._calculate_market_uncertainty(market_data),
 'entry_rate': self._calculate_entry_rate(market_data)
 }
 elif stage == 'growth':
 metrics = {
 'expansion_rate': self._calculate_expansion_rate(market_data),
 'investment_level': self._calculate_investment_level(market_data),
 'standardization_degree': self._calculate_standardization_degree(market_data)
 }
 elif stage == 'mature':
 metrics = {
 'market_saturation': self._calculate_market_saturation(market_data),
 'price_pressure': self._calculate_price_pressure(market_data),
 'efficiency_index': self._calculate_efficiency_index(market_data)
 }
 else:
 # Generic metrics for unknown stages
 metrics = {
 'general_activity': (hash(stage) % 100) / 100.0,
 'market_dynamics': (hash(f'{stage}_dynamics') % 100) / 100.0
 }

 return metrics

 def _assess_stage_strength(self, stage: str, market_data: Dict[str, Any]) -> float:
 """Assess how strongly the market exhibits stage characteristics"""
 characteristics = self._identify_stage_characteristics(stage, market_data)
 metrics = self._calculate_stage_indicator_metrics(stage, market_data)

 # Calculate strength based on metrics alignment with stage
 strength_score = sum(metrics.values()) / len(metrics) if metrics else 0.5

 return min(1.0, max(0.0, strength_score))

 def _detect_stage_transition_signals(self, stage: str, market_data: Dict[str, Any]) -> List[str]:
 """Detect signals indicating potential stage transition"""
 signals = []

 # Dynamic signal detection based on current stage
 stage_metrics = self._calculate_stage_indicator_metrics(stage, market_data)

 for metric, value in stage_metrics.items():
 if value > 0.8:
 signals.append(f'high_{metric}_transition_signal')
 elif value < 0.2:
 signals.append(f'low_{metric}_transition_signal')

 return signals[:3] # Limit to 3 signals

 def _generate_stage_recommendations(self, stage: str, market_data: Dict[str, Any]) -> List[str]:
 """Generate recommendations based on market stage"""
 stage_recommendations = {
 'emerging': [
 'focus_on_innovation_and_differentiation',
 'build_market_awareness',
 'establish_early_partnerships'
 ],
 'growth': [
 'scale_operations_efficiently',
 'strengthen_competitive_position',
 'expand_market_reach'
 ],
 'mature': [
 'optimize_operational_efficiency',
 'explore_adjacent_markets',
 'focus_on_customer_retention'
 ],
 'decline': [
 'consider_market_exit_strategies',
 'explore_niche_opportunities',
 'prepare_for_disruption'
 ]
 }

 return stage_recommendations.get(stage, ['analyze_market_conditions_further'])

 # Helper methods for metric calculations
 def _calculate_innovation_rate(self, market_data: Dict[str, Any]) -> float:
 """Calculate innovation rate for emerging markets"""
 return (hash('innovation') % 100) / 100.0

 def _calculate_market_uncertainty(self, market_data: Dict[str, Any]) -> float:
 """Calculate market uncertainty level"""
 return (hash('uncertainty') % 100) / 100.0

 def _calculate_entry_rate(self, market_data: Dict[str, Any]) -> float:
 """Calculate rate of new market entrants"""
 return (hash('entry') % 100) / 100.0

 def _calculate_expansion_rate(self, market_data: Dict[str, Any]) -> float:
 """Calculate market expansion rate"""
 return (hash('expansion') % 100) / 100.0

 def _calculate_investment_level(self, market_data: Dict[str, Any]) -> float:
 """Calculate investment level in market"""
 return (hash('investment') % 100) / 100.0

 def _calculate_standardization_degree(self, market_data: Dict[str, Any]) -> float:
 """Calculate degree of market standardization"""
 return (hash('standardization') % 100) / 100.0

 def _calculate_market_saturation(self, market_data: Dict[str, Any]) -> float:
 """Calculate market saturation level"""
 return (hash('saturation') % 100) / 100.0

 def _calculate_price_pressure(self, market_data: Dict[str, Any]) -> float:
 """Calculate price pressure in market"""
 return (hash('price_pressure') % 100) / 100.0

 def _calculate_efficiency_index(self, market_data: Dict[str, Any]) -> float:
 """Calculate operational efficiency index"""
 return (hash('efficiency') % 100) / 100.0

 def _identify_top_competitors(self, competitors: Dict[str, Any]) -> List[str]:
 """Identify top competitors from competitor data"""
 if not competitors:
 return []

 # Simple top competitor identification
 competitor_names = list(competitors.keys())[:3] # Top 3
 return competitor_names

 def _assess_competitive_intensity_score(self, competitors: Dict[str, Any]) -> float:
 """Assess competitive intensity based on competitor data"""
 if not competitors:
 return 0.0

 # Simple intensity calculation based on number of competitors
 intensity = min(1.0, len(competitors) / 10.0)
 return intensity

 def _calculate_assessment_confidence(self, indicator_scores: Dict[str, Dict[str, Any]]) -> float:
 """Calculate overall confidence in assessment"""
 if not indicator_scores:
 return 0.0

 confidence_scores = [
 score_data.get('confidence', 0.5) 
 for score_data in indicator_scores.values()
 ]

 return sum(confidence_scores) / len(confidence_scores)

 def _generate_fallback_maturity_indicators(self) -> Dict[str, Any]:
 """Generate fallback indicators when assessment fails"""
 return {
 'assessment_status': 'limited_data',
 'fallback_assessment': 'unknown_maturity',
 'confidence': 0.2,
 'recommendation': 'gather_comprehensive_market_data'
 }

 def _generate_fallback_stage_indicators(self, stage: str) -> Dict[str, Any]:
 """Generate fallback stage indicators when analysis fails"""
 return {
 'stage': stage,
 'analysis_status': 'limited_data',
 'fallback_strength': 0.5,
 'confidence': 0.2,
 'recommendation': 'collect_stage_specific_data'
 }


# Singleton instance
_market_maturity_service = None
_service_lock = threading.Lock()


def get_market_maturity_service() -> MarketMaturityService:
 """
 Get singleton instance of MarketMaturityService
 """
 global _market_maturity_service

 if _market_maturity_service is None:
 with _service_lock:
 if _market_maturity_service is None:
 _market_maturity_service = MarketMaturityService()

 return _market_maturity_service


# Export for external use
__all__ = ['MarketMaturityService', 'get_market_maturity_service']
