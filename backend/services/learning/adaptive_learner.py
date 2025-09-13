"""
Adaptive Learner - Shared Service
Advanced adaptive learning system for pattern recognition and insight generation
"""

import logging
from typing import Dict, Any, List

from backend.config.config_manager import get_config_manager

logger = logging.getLogger(__name__)


class AdaptiveLearner:
    """Generates adaptive insights using learned patterns and machine learning techniques - fully dynamic configuration"""
    
    def __init__(self):
        self.learning_history: List[Dict[str, Any]] = []
        self.pattern_cache: Dict[str, Dict[str, Any]] = {}
        self.adaptation_strategies: Dict[str, Any] = {}
        self.config_manager = get_config_manager()
        
    def generate_adaptive_insights(self, strategic_synthesis: Dict[str, Any],
                                 context: Dict[str, Any],
                                 intelligence_engine=None) -> Dict[str, Any]:
        """Generate insights using adaptive learning"""
        
        # Create pattern for similarity search using dynamic configuration
        pattern_config = self.config_manager.get('adaptive_learner.pattern_matching', {})
        timeline_default = pattern_config.get('timeline_urgency_default', 0.5)
        complexity_default = pattern_config.get('text_complexity_default', 0.5)
        similarity_threshold = pattern_config.get('context_similarity_threshold', 0.6)
        
        current_pattern = {
            'strategic_direction': strategic_synthesis.get('primary_strategic_direction', 'unknown'),
            'budget_scale': context.get('derived_context', {}).get('budget_scale', 'medium'),
            'timeline_urgency': context.get('derived_context', {}).get('timeline_urgency', timeline_default),
            'text_complexity': context.get('derived_context', {}).get('text_complexity', complexity_default)
        }
        
        # Retrieve similar patterns if intelligence engine is available
        similar_patterns = []
        if intelligence_engine:
            similar_patterns = intelligence_engine.retrieve_similar_patterns(
                'strategic_analysis', current_pattern, similarity_threshold=similarity_threshold
            )
        
        # Generate adaptive insights
        insights = self._synthesize_adaptive_insights(similar_patterns, strategic_synthesis)
        
        # Generate learning recommendations
        learning_recommendations = self._generate_learning_recommendations(current_pattern, insights)
        
        return {
            'success_indicators': insights['success_indicators'],
            'measurable_outcomes': insights['measurable_outcomes'],
            'pattern_matches': len(similar_patterns),
            'adaptation_confidence': insights['confidence'],
            'learned_optimizations': insights['optimizations'],
            'learning_recommendations': learning_recommendations,
            'adaptive_metadata': {
                'pattern_hash': self._generate_pattern_hash(current_pattern),
                'learning_depth': self._assess_learning_depth(similar_patterns),
                'adaptation_potential': self._assess_adaptation_potential(current_pattern)
            }
        }
    
    def learn_from_outcome(self, pattern: Dict[str, Any], outcome: Dict[str, Any], 
                          success_score: float) -> None:
        """Learn from outcome to improve future predictions"""
        learning_entry = {
            'pattern': pattern,
            'outcome': outcome,
            'success_score': success_score,
            'timestamp': self._get_timestamp(),
            'improvement_factors': self._extract_improvement_factors(pattern, outcome, success_score)
        }
        
        self.learning_history.append(learning_entry)
        self._update_adaptation_strategies(learning_entry)
        
        # Maintain learning history size using dynamic configuration
        learning_config = self.config_manager.get('adaptive_learner.learning_parameters', {})
        max_history = learning_config.get('max_learning_history', 1000)
        retention_count = learning_config.get('history_retention_count', 800)
        
        if len(self.learning_history) > max_history:
            self.learning_history = self.learning_history[-retention_count:]
    
    def predict_success_probability(self, pattern: Dict[str, Any]) -> float:
        """Predict success probability based on learned patterns using dynamic configuration"""
        prediction_config = self.config_manager.get('adaptive_learner.prediction_settings', {})
        learning_config = self.config_manager.get('adaptive_learner.learning_parameters', {})
        
        default_probability = prediction_config.get('default_probability_fallback', 0.5)
        confidence_boost = prediction_config.get('confidence_boost_threshold', 0.7)
        weight_high = learning_config.get('weight_multiplier_high', 1.0)
        weight_low = learning_config.get('weight_multiplier_low', 0.5)
        min_total_weight = prediction_config.get('minimum_total_weight', 0.0)
        
        if not self.learning_history:
            return default_probability
        
        # Find similar historical patterns
        similar_entries = self._find_similar_historical_patterns(pattern)
        
        if not similar_entries:
            return default_probability
        
        # Calculate weighted average success score using dynamic configuration
        total_weight = 0
        weighted_success = 0
        
        for entry in similar_entries:
            similarity = self._calculate_pattern_similarity(pattern, entry['pattern'])
            weight = similarity * (weight_high if entry['success_score'] > confidence_boost else weight_low)
            weighted_success += entry['success_score'] * weight
            total_weight += weight
        
        return weighted_success / total_weight if total_weight > min_total_weight else default_probability
    
    def generate_optimization_suggestions(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on learned patterns using dynamic configuration"""
        optimization_config = self.config_manager.get('adaptive_learner.optimization_rules', {})
        
        success_filter_threshold = optimization_config.get('success_filter_threshold', 0.7)
        similarity_filter_threshold = optimization_config.get('similarity_filter_threshold', 0.5)
        max_suggestions_returned = optimization_config.get('max_suggestions_returned', 5)
        
        suggestions = []
        
        # Analyze similar successful patterns using dynamic thresholds
        successful_patterns = [
            entry for entry in self.learning_history 
            if entry['success_score'] > success_filter_threshold and self._calculate_pattern_similarity(pattern, entry['pattern']) > similarity_filter_threshold
        ]
        
        for entry in successful_patterns:
            improvement_factors = entry.get('improvement_factors', {})
            for factor, value in improvement_factors.items():
                suggestions.append({
                    'type': 'optimization',
                    'factor': factor,
                    'recommendation': f"Consider optimizing {factor} based on successful patterns",
                    'confidence': entry['success_score'],
                    'evidence_strength': len([e for e in successful_patterns if factor in e.get('improvement_factors', {})])
                })
        
        # Remove duplicates and sort by confidence
        unique_suggestions = {}
        for suggestion in suggestions:
            key = suggestion['factor']
            if key not in unique_suggestions or suggestion['confidence'] > unique_suggestions[key]['confidence']:
                unique_suggestions[key] = suggestion
        
        return sorted(unique_suggestions.values(), key=lambda x: x['confidence'], reverse=True)[:max_suggestions_returned]
    
    def _synthesize_adaptive_insights(self, similar_patterns: List[Dict[str, Any]],
                                    strategic_synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize insights from similar patterns using dynamic configuration"""
        synthesis_config = self.config_manager.get('adaptive_learner.synthesis_parameters', {})
        
        # Get dynamic fallback values instead of hardcoded ones
        default_success_indicators = synthesis_config.get('default_success_indicators', ['goal_achievement', 'strategic_alignment'])
        default_measurable_outcomes = synthesis_config.get('default_measurable_outcomes', ['performance_improvement', 'objective_completion'])
        default_confidence = synthesis_config.get('default_confidence_level', 0.3)
        default_optimizations = synthesis_config.get('default_optimizations', ['data_driven_optimization', 'continuous_improvement'])
        
        # Get success rate filter threshold dynamically
        success_rate_threshold = synthesis_config.get('high_success_pattern_threshold', 0.7)
        
        # Get result limits dynamically
        max_success_indicators = synthesis_config.get('max_success_indicators', 5)
        max_measurable_outcomes = synthesis_config.get('max_measurable_outcomes', 5)
        max_optimizations = synthesis_config.get('max_optimizations', 3)
        
        if not similar_patterns:
            return {
                'success_indicators': default_success_indicators,
                'measurable_outcomes': default_measurable_outcomes,
                'confidence': default_confidence,
                'optimizations': default_optimizations
            }
        
        # Extract common success patterns using dynamic threshold
        high_success_patterns = [p for p in similar_patterns if p.get('success_rate', 0) > success_rate_threshold]
        
        success_indicators = []
        measurable_outcomes = []
        optimizations = []
        
        # Extract insights from successful patterns
        for pattern in high_success_patterns:
            # Extract strategic indicators based on pattern type
            direction = pattern.get('pattern', {}).get('strategic_direction', '')
            if 'growth' in direction:
                success_indicators.extend(['revenue_growth', 'market_expansion'])
                measurable_outcomes.extend(['revenue_increase', 'market_share_growth'])
            elif 'optimization' in direction:
                success_indicators.extend(['efficiency_improvement', 'cost_reduction'])
                measurable_outcomes.extend(['cost_savings', 'process_efficiency'])
            elif 'innovation' in direction:
                success_indicators.extend(['innovation_adoption', 'competitive_advantage'])
                measurable_outcomes.extend(['product_development', 'market_differentiation'])
            
            # Add optimization strategies
            optimizations.extend(['pattern_based_optimization', 'adaptive_tuning'])
        
        # Remove duplicates and limit using dynamic configuration
        success_indicators = list(set(success_indicators))[:max_success_indicators]
        measurable_outcomes = list(set(measurable_outcomes))[:max_measurable_outcomes]
        optimizations = list(set(optimizations))[:max_optimizations]
        
        # Calculate confidence based on pattern success rates using dynamic configuration
        if similar_patterns:
            default_success_rate = synthesis_config.get('default_success_rate_fallback', 0.5)
            default_pattern_weight = synthesis_config.get('default_pattern_weight', 1.0)
            success_rate_weight = synthesis_config.get('success_rate_weight_factor', 0.7)
            pattern_weight_factor = synthesis_config.get('pattern_weight_factor', 0.3)
            max_confidence = synthesis_config.get('max_confidence_limit', 1.0)
            
            avg_success_rate = sum(p.get('success_rate', default_success_rate) for p in similar_patterns) / len(similar_patterns)
            pattern_weight = sum(p.get('weight', default_pattern_weight) for p in similar_patterns) / len(similar_patterns)
            confidence = min(max_confidence, avg_success_rate * success_rate_weight + pattern_weight * pattern_weight_factor)
        else:
            confidence = default_confidence
        
        # Fallback values if empty using dynamic configuration
        fallback_success_indicators = synthesis_config.get('fallback_success_indicators', ['goal_achievement', 'strategic_progress'])
        fallback_measurable_outcomes = synthesis_config.get('fallback_measurable_outcomes', ['performance_improvement', 'objective_completion'])
        fallback_optimizations = synthesis_config.get('fallback_optimizations', ['adaptive_optimization', 'continuous_learning'])
        
        if not success_indicators:
            success_indicators = fallback_success_indicators
        if not measurable_outcomes:
            measurable_outcomes = fallback_measurable_outcomes
        if not optimizations:
            optimizations = fallback_optimizations
        
        return {
            'success_indicators': success_indicators,
            'measurable_outcomes': measurable_outcomes,
            'confidence': confidence,
            'optimizations': optimizations
        }
    
    def _generate_learning_recommendations(self, pattern: Dict[str, Any], 
                                         insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for improving learning using dynamic configuration"""
        learning_config = self.config_manager.get('adaptive_learner.learning_parameters', {})
        
        confidence_threshold = learning_config.get('low_confidence_threshold', 0.5)
        default_confidence = learning_config.get('default_confidence_fallback', 0.5)
        min_indicators_required = learning_config.get('minimum_success_indicators', 3)
        
        recommendations = []
        
        confidence = insights.get('confidence', default_confidence)
        
        if confidence < confidence_threshold:
            recommendations.append({
                'type': 'data_enhancement',
                'description': 'Gather more contextual data to improve predictions',
                'priority': 'high'
            })
        
        if len(insights.get('success_indicators', [])) < min_indicators_required:
            recommendations.append({
                'type': 'indicator_expansion',
                'description': 'Identify additional success indicators for comprehensive tracking',
                'priority': 'medium'
            })
        
        # Strategic direction specific recommendations
        strategic_direction = pattern.get('strategic_direction', '')
        if 'unknown' in strategic_direction:
            recommendations.append({
                'type': 'strategic_clarity',
                'description': 'Clarify strategic direction for better pattern matching',
                'priority': 'high'
            })
        
        return recommendations
    
    def _find_similar_historical_patterns(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar patterns from learning history using dynamic configuration"""
        similarity_config = self.config_manager.get('adaptive_learner.similarity_analysis', {})
        
        similarity_threshold = similarity_config.get('pattern_similarity_threshold', 0.5)
        max_similar_patterns = similarity_config.get('max_similar_patterns_returned', 10)
        
        similar_patterns = []
        
        for entry in self.learning_history:
            similarity = self._calculate_pattern_similarity(pattern, entry['pattern'])
            if similarity > similarity_threshold:
                similar_patterns.append(entry)
        
        return sorted(similar_patterns, 
                     key=lambda x: self._calculate_pattern_similarity(pattern, x['pattern']), 
                     reverse=True)[:max_similar_patterns]
    
    def _calculate_pattern_similarity(self, pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> float:
        """Calculate similarity between two patterns"""
        if not pattern1 or not pattern2:
            return 0.0
        
        common_keys = set(pattern1.keys()) & set(pattern2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1, val2 = pattern1[key], pattern2[key]
            
            similarity_config = self.config_manager.get('adaptive_learner.similarity_analysis', {})
            
            if isinstance(val1, str) and isinstance(val2, str):
                # String similarity using dynamic configuration
                exact_match_score = similarity_config.get('string_exact_match_score', 1.0)
                partial_match_score = similarity_config.get('string_partial_match_score', 0.5)
                no_match_score = similarity_config.get('string_no_match_score', 0.0)
                
                similarities.append(exact_match_score if val1 == val2 else partial_match_score if val1 in val2 or val2 in val1 else no_match_score)
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity using dynamic configuration
                min_max_val = similarity_config.get('numerical_min_max_value', 1.0)
                max_val = max(abs(val1), abs(val2), min_max_val)
                base_score = similarity_config.get('numerical_base_score', 1.0)
                
                similarities.append(base_score - abs(val1 - val2) / max_val)
            else:
                # Default similarity using dynamic configuration
                default_match_score = similarity_config.get('default_match_score', 0.5)
                default_no_match_score = similarity_config.get('default_no_match_score', 0.0)
                
                similarities.append(default_match_score if str(val1) == str(val2) else default_no_match_score)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _extract_improvement_factors(self, pattern: Dict[str, Any], outcome: Dict[str, Any], 
                                   success_score: float) -> Dict[str, Any]:
        """Extract factors that contributed to improvement using dynamic configuration"""
        improvement_config = self.config_manager.get('adaptive_learner.improvement_analysis', {})
        
        high_success_threshold = improvement_config.get('high_success_threshold', 0.7)
        urgency_threshold = improvement_config.get('timeline_urgency_threshold', 0.6)
        
        factors = {}
        
        if success_score > high_success_threshold:
            factors['strategic_alignment'] = improvement_config.get('high_success_strategic_alignment', 'high')
            factors['execution_quality'] = improvement_config.get('high_success_execution_quality', 'effective')
        
        if 'timeline_urgency' in pattern and pattern['timeline_urgency'] > urgency_threshold:
            factors['time_management'] = improvement_config.get('urgent_execution_label', 'urgent_execution')
        
        if 'budget_scale' in pattern:
            factors['resource_allocation'] = pattern['budget_scale']
        
        return factors
    
    def _update_adaptation_strategies(self, learning_entry: Dict[str, Any]) -> None:
        """Update adaptation strategies based on new learning"""
        success_score = learning_entry['success_score']
        pattern = learning_entry['pattern']
        
        # Update strategies based on successful patterns using dynamic configuration
        success_config = self.config_manager.get('adaptive_learner.success_criteria', {})
        strategy_update_threshold = success_config.get('strategy_update_threshold', 0.7)
        default_strategy_key = success_config.get('default_strategy_key', 'default')
        
        if success_score > strategy_update_threshold:
            strategy_key = pattern.get('strategic_direction', default_strategy_key)
            if strategy_key not in self.adaptation_strategies:
                self.adaptation_strategies[strategy_key] = {
                    'success_count': 0,
                    'total_attempts': 0,
                    'best_practices': []
                }
            
            strategy = self.adaptation_strategies[strategy_key]
            strategy['success_count'] += 1
            strategy['total_attempts'] += 1
            
            # Add best practices
            for factor, value in learning_entry.get('improvement_factors', {}).items():
                if factor not in [bp['factor'] for bp in strategy['best_practices']]:
                    strategy['best_practices'].append({
                        'factor': factor,
                        'value': value,
                        'confidence': success_score
                    })
    
    def _assess_learning_depth(self, similar_patterns: List[Dict[str, Any]]) -> str:
        """Assess the depth of learning from available patterns"""
        if len(similar_patterns) >= 10:
            return 'deep'
        elif len(similar_patterns) >= 5:
            return 'moderate'
        elif len(similar_patterns) >= 2:
            return 'shallow'
        else:
            return 'minimal'
    
    def _assess_adaptation_potential(self, pattern: Dict[str, Any]) -> float:
        """Assess the potential for adaptation based on pattern characteristics"""
        complexity_factors = [
            len(str(pattern)) / 500.0,  # Pattern complexity
            len(pattern.keys()) / 10.0,  # Feature diversity
            1.0 if any(isinstance(v, (list, dict)) for v in pattern.values()) else 0.5  # Structure complexity
        ]
        
        return min(1.0, sum(complexity_factors) / len(complexity_factors))
    
    def _generate_pattern_hash(self, pattern: Dict[str, Any]) -> str:
        """Generate a hash for pattern identification"""
        import hashlib
        import json
        pattern_str = json.dumps(pattern, sort_keys=True)
        return hashlib.md5(pattern_str.encode()).hexdigest()[:16]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Singleton instance for easy import
_adaptive_learner = None

def get_adaptive_learner() -> AdaptiveLearner:
    """Get shared AdaptiveLearner instance"""
    global _adaptive_learner
    if _adaptive_learner is None:
        _adaptive_learner = AdaptiveLearner()
    return _adaptive_learner
