"""
Strategic Synthesizer - Shared Service
Advanced strategic synthesis and insight generation for business intelligence
"""

import logging
from typing import Dict, Any, List

from backend.services.shared.semantic import DynamicBusinessProfile
from backend.config.config_manager import get_config_manager

logger = logging.getLogger(__name__)


class StrategicSynthesizer:
 """Synthesizes strategic insights from all analyses - fully dynamic configuration"""

 def __init__(self):
 self.strategy_templates = {}
 self.synthesis_patterns = {}
 self.config_manager = get_config_manager()

 def synthesize_strategy(self, business_profile: DynamicBusinessProfile,
 patterns: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
 """Synthesize comprehensive strategic insights"""

 # Determine primary strategic direction
 primary_direction = self._determine_primary_direction(patterns, context)

 # Identify secondary directions
 secondary_directions = self._identify_secondary_directions(patterns, business_profile)

 # Calculate strategic confidence
 confidence = self._calculate_strategic_confidence(patterns, business_profile)

 # Generate strategic recommendations
 recommendations = self._generate_recommendations(patterns, context, business_profile)

 return {
 'primary_strategic_direction': primary_direction,
 'secondary_directions': secondary_directions,
 'confidence': confidence,
 'strategic_focus': patterns.get('strategic_patterns', {}).get('strategic_focus', 'balanced'),
 'recommended_approach': self._recommend_approach(patterns, context),
 'strategic_recommendations': recommendations,
 'synthesis_metadata': {
 'patterns_analyzed': len(patterns),
 'confidence_factors': self._get_confidence_factors(patterns, business_profile),
 'synthesis_timestamp': self._get_timestamp()
 }
 }

 def synthesize_market_strategy(self, market_data: Dict[str, Any], 
 competitive_analysis: Dict[str, Any]) -> Dict[str, Any]:
 """Synthesize market-specific strategy"""
 market_opportunities = self._identify_market_opportunities(market_data)
 competitive_advantages = self._analyze_competitive_positioning(competitive_analysis)

 return {
 'market_opportunities': market_opportunities,
 'competitive_positioning': competitive_advantages,
 'market_entry_strategy': self._recommend_market_entry(market_data, competitive_analysis),
 'growth_vectors': self._identify_growth_vectors(market_data)
 }

 def _determine_primary_direction(self, patterns: Dict[str, Any], context: Dict[str, Any]) -> str:
 """Determine primary strategic direction using dynamic configuration"""
 goal_text = context.get('primary_inputs', {}).get('goal_text', '').lower()

 # Get direction indicators from configuration instead of hardcoded values
 direction_indicators = self.config_manager.get('strategic_synthesizer.direction_indicators', {})
 default_direction = self.config_manager.get('strategic_synthesizer.defaults.primary_direction', 'comprehensive_business_strategy')

 direction_scores = {}
 # Get scoring configuration
 scoring_config = self.config_manager.get('strategic_synthesizer.scoring', {})
 full_match_weight = scoring_config.get('full_match_weight', 1.0)
 partial_match_weight = scoring_config.get('partial_match_weight', 0.5)

 for direction, indicators in direction_indicators.items():
 score = sum(full_match_weight for indicator in indicators if indicator in goal_text)
 # Weight by indicator strength using dynamic configuration
 score += sum(partial_match_weight for indicator in indicators if any(word in goal_text for word in indicator.split()))
 direction_scores[direction] = score

 if not direction_scores or max(direction_scores.values()) == 0:
 return default_direction

 return max(direction_scores.items(), key=lambda x: x[1])[0]

 def _identify_secondary_directions(self, patterns: Dict[str, Any], profile: DynamicBusinessProfile) -> List[str]:
 """Identify secondary strategic directions using dynamic configuration"""
 secondary = []

 # Get thresholds from configuration instead of hardcoded values
 priority_threshold = self.config_manager.get('strategic_synthesizer.thresholds.priority_medium', 0.6)
 risk_threshold = self.config_manager.get('strategic_synthesizer.thresholds.risk_high', 0.6)
 growth_threshold = self.config_manager.get('strategic_synthesizer.thresholds.growth_strong', 0.7)
 max_directions = self.config_manager.get('strategic_synthesizer.strategic_limits.max_secondary_directions', 3)

 # Based on opportunity matrix
 for opportunity, metrics in profile.opportunity_matrix.items():
 priority = metrics.get('priority', 0) if isinstance(metrics, dict) else 0
 if priority > priority_threshold:
 secondary.append(f"{opportunity}_initiative")

 # Based on risk mitigation needs
 high_risks = [risk for risk, level in profile.risk_profile.items() if level > risk_threshold]
 for risk in high_risks:
 secondary.append(f"{risk}_mitigation")

 # Based on growth indicators
 strong_growth_areas = [area for area, score in profile.growth_indicators.items() if score > growth_threshold]
 for area in strong_growth_areas:
 secondary.append(f"{area}_acceleration")

 return secondary[:max_directions]

 def _calculate_strategic_confidence(self, patterns: Dict[str, Any], profile: DynamicBusinessProfile) -> float:
 """Calculate confidence in strategic synthesis using dynamic configuration"""
 # Get confidence weights from configuration instead of hardcoded values
 weights = self.config_manager.get('strategic_synthesizer.confidence_weights', {})
 bounds = self.config_manager.get('strategic_synthesizer.confidence_bounds', {})
 fallback_confidence = self.config_manager.get('strategic_synthesizer.defaults.confidence_fallback', 0.5)

 # Pattern clarity factor
 strategic_patterns = patterns.get('strategic_patterns', {})
 pattern_clarity = strategic_patterns.get('strategic_clarity', fallback_confidence)

 # Growth potential factor
 growth_indicators = profile.growth_indicators
 growth_potential = sum(growth_indicators.values()) / len(growth_indicators) if growth_indicators else fallback_confidence

 # Risk level factor (inverse relationship)
 risk_profile = profile.risk_profile
 risk_level = sum(risk_profile.values()) / len(risk_profile) if risk_profile else fallback_confidence

 # Data completeness factor
 data_completeness = self._assess_data_completeness(patterns, profile)

 # Weighted confidence calculation using dynamic weights
 confidence = (
 pattern_clarity * weights.get('pattern_clarity', 0.3) +
 growth_potential * weights.get('growth_potential', 0.25) +
 (1 - risk_level) * weights.get('risk_factor', 0.2) +
 data_completeness * weights.get('data_completeness', 0.25)
 )

 return min(bounds.get('maximum', 1.0), max(bounds.get('minimum', 0.1), confidence))

 def _recommend_approach(self, patterns: Dict[str, Any], context: Dict[str, Any]) -> str:
 """Recommend strategic approach using dynamic configuration"""
 derived_context = context.get('derived_context', {})
 urgency = derived_context.get('timeline_urgency', 0.5)
 budget_scale = derived_context.get('budget_scale', 'medium_budget')
 complexity = derived_context.get('text_complexity', 0.5)

 # Get approach criteria from configuration instead of hardcoded values
 criteria = self.config_manager.get('strategic_synthesizer.approach_criteria', {})
 default_approach = self.config_manager.get('strategic_synthesizer.defaults.strategic_approach', 'balanced_strategic_approach')

 # Strategic approach decision tree using dynamic criteria
 rapid_exec = criteria.get('rapid_execution', {})
 if (urgency > rapid_exec.get('urgency_threshold', 0.7) and 
 complexity < rapid_exec.get('complexity_max', 0.5)):
 return 'rapid_execution'

 comprehensive = criteria.get('comprehensive_transformation', {})
 if (budget_scale in comprehensive.get('budget_scales', ['large_budget', 'enterprise_budget']) and 
 complexity > comprehensive.get('complexity_min', 0.6)):
 return 'comprehensive_transformation'

 phased = criteria.get('phased_implementation', {})
 if (complexity > phased.get('complexity_min', 0.7) or 
 urgency < phased.get('urgency_max', 0.3)):
 return 'phased_implementation'

 lean_agile = criteria.get('lean_agile_approach', {})
 if (urgency > lean_agile.get('urgency_min', 0.6) and 
 budget_scale in lean_agile.get('budget_scales', ['small_budget', 'micro_budget'])):
 return 'lean_agile_approach'

 return default_approach

 def _generate_recommendations(self, patterns: Dict[str, Any], context: Dict[str, Any], 
 profile: DynamicBusinessProfile) -> List[Dict[str, Any]]:
 """Generate specific strategic recommendations using dynamic configuration"""
 recommendations = []

 # Get thresholds from configuration instead of hardcoded values
 growth_threshold = self.config_manager.get('strategic_synthesizer.thresholds.growth_potential_threshold', 0.6)
 risk_threshold = self.config_manager.get('strategic_synthesizer.thresholds.risk_high', 0.6)
 priority_high_threshold = self.config_manager.get('strategic_synthesizer.thresholds.priority_high', 0.8)
 max_recommendations = self.config_manager.get('strategic_synthesizer.strategic_limits.max_recommendations', 5)

 # Growth-based recommendations
 for growth_area, score in profile.growth_indicators.items():
 if score > growth_threshold:
 recommendations.append({
 'type': 'growth_opportunity',
 'area': growth_area,
 'priority': 'high' if score > priority_high_threshold else 'medium',
 'description': f"Leverage {growth_area} for strategic growth",
 'confidence': score
 })

 # Risk mitigation recommendations
 for risk, level in profile.risk_profile.items():
 if level > risk_threshold:
 recommendations.append({
 'type': 'risk_mitigation',
 'area': risk,
 'priority': 'high' if level > priority_high_threshold else 'medium',
 'description': f"Implement {risk} risk mitigation strategies",
 'confidence': 1 - level
 })

 return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)[:max_recommendations]

 def _identify_market_opportunities(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
 """Identify market opportunities from data using dynamic configuration"""
 opportunities = []

 # Get thresholds from configuration instead of hardcoded values
 moderate_growth = self.config_manager.get('strategic_synthesizer.thresholds.market_growth_moderate', 0.1)
 significant_growth = self.config_manager.get('strategic_synthesizer.thresholds.market_growth_significant', 0.2)

 trends = market_data.get('trends', {})
 for trend, growth_rate in trends.items():
 if isinstance(growth_rate, (int, float)) and growth_rate > moderate_growth:
 opportunities.append({
 'type': 'market_trend',
 'trend': trend,
 'growth_rate': growth_rate,
 'priority': 'high' if growth_rate > significant_growth else 'medium'
 })

 return opportunities

 def _analyze_competitive_positioning(self, competitive_analysis: Dict[str, Any]) -> Dict[str, Any]:
 """Analyze competitive positioning advantages"""
 return {
 'competitive_strengths': competitive_analysis.get('strengths', []),
 'market_gaps': competitive_analysis.get('gaps', []),
 'differentiation_opportunities': competitive_analysis.get('opportunities', [])
 }

 def _recommend_market_entry(self, market_data: Dict[str, Any], 
 competitive_analysis: Dict[str, Any]) -> str:
 """Recommend market entry strategy using dynamic configuration"""
 market_maturity = market_data.get('maturity', 'medium')
 competition_level = competitive_analysis.get('intensity', 'medium')

 # Get market entry strategies from configuration instead of hardcoded logic
 strategies = self.config_manager.get('strategic_synthesizer.market_entry_strategies', {})

 # Check for first mover advantage
 first_mover = strategies.get('first_mover_advantage', {})
 if (market_maturity == first_mover.get('market_maturity', 'emerging') and 
 competition_level == first_mover.get('competition_level', 'low')):
 return 'first_mover_advantage'

 # Check for niche differentiation
 niche_diff = strategies.get('niche_differentiation', {})
 if (market_maturity == niche_diff.get('market_maturity', 'mature') and 
 competition_level == niche_diff.get('competition_level', 'high')):
 return 'niche_differentiation'

 # Check for direct competition
 direct_comp = strategies.get('direct_competition', {})
 if competition_level == direct_comp.get('competition_level', 'low'):
 return 'direct_competition'

 # Default to strategic partnership
 return 'strategic_partnership'

 def _identify_growth_vectors(self, market_data: Dict[str, Any]) -> List[str]:
 """Identify potential growth vectors using dynamic configuration"""
 vectors = []

 # Get threshold from configuration instead of hardcoded value
 growth_threshold = self.config_manager.get('strategic_synthesizer.thresholds.growth_potential_threshold', 0.6)

 segments = market_data.get('segments', {})
 for segment, data in segments.items():
 if isinstance(data, dict) and data.get('growth_potential', 0) > growth_threshold:
 vectors.append(f"{segment}_expansion")

 return vectors

 def _assess_data_completeness(self, patterns: Dict[str, Any], profile: DynamicBusinessProfile) -> float:
 """Assess completeness of available data using dynamic configuration"""
 # Get baseline from configuration instead of hardcoded value
 pattern_baseline = self.config_manager.get('strategic_synthesizer.strategic_limits.pattern_completeness_baseline', 10)

 pattern_score = len(patterns) / float(pattern_baseline)
 profile_score = (
 (1 if profile.industry_vectors else 0) +
 (1 if profile.growth_indicators else 0) +
 (1 if profile.risk_profile else 0) +
 (1 if profile.opportunity_matrix else 0)
 ) / 4.0

 return min(1.0, (pattern_score + profile_score) / 2.0)

 def _get_confidence_factors(self, patterns: Dict[str, Any], profile: DynamicBusinessProfile) -> Dict[str, float]:
 """Get detailed confidence factors"""
 return {
 'pattern_clarity': patterns.get('strategic_patterns', {}).get('strategic_clarity', 0.5),
 'data_completeness': self._assess_data_completeness(patterns, profile),
 'growth_potential': sum(profile.growth_indicators.values()) / len(profile.growth_indicators) if profile.growth_indicators else 0.5,
 'risk_assessment': 1 - (sum(profile.risk_profile.values()) / len(profile.risk_profile) if profile.risk_profile else 0.5)
 }

 def _get_timestamp(self) -> str:
 """Get current timestamp for synthesis metadata"""
 from datetime import datetime
 return datetime.now().isoformat()


# Singleton instance for easy import
_strategic_synthesizer = None

def get_strategic_synthesizer() -> StrategicSynthesizer:
 """Get shared StrategicSynthesizer instance"""
 global _strategic_synthesizer
 if _strategic_synthesizer is None:
 _strategic_synthesizer = StrategicSynthesizer()
 return _strategic_synthesizer
