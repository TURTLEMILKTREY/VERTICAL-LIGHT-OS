"""
Optimization Engine - Shared Service
Advanced optimization algorithms and strategy generation for campaigns and business processes
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from backend.config.config_manager import get_config_manager

logger = logging.getLogger(__name__)


class OptimizationEngine:
    """Advanced optimization engine for campaigns, strategies, and business processes - fully dynamic configuration"""
    
    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        self.optimization_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.config_manager = get_config_manager()
        
    def generate_campaign_optimization(self, campaign_data: Dict[str, Any], 
                                     performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate optimization strategy for marketing campaigns"""
        
        # Analyze current performance
        performance_analysis = self._analyze_performance(performance_metrics)
        
        # Identify optimization opportunities
        opportunities = self._identify_optimization_opportunities(campaign_data, performance_metrics)
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(opportunities, performance_analysis)
        
        return {
            'optimization_strategy': {
                'primary_focus': self._determine_primary_optimization_focus(performance_analysis),
                'optimization_dimensions': self._get_optimization_dimensions(campaign_data),
                'optimization_frequency': self._determine_optimization_frequency(performance_analysis),
                'success_thresholds': self._calculate_success_thresholds(performance_metrics),
                'adaptation_rules': self._generate_adaptation_rules(performance_analysis)
            },
            'performance_analysis': performance_analysis,
            'opportunities': opportunities,
            'recommendations': recommendations,
            'implementation_plan': self._create_implementation_plan(recommendations),
            'monitoring_framework': self._create_monitoring_framework(campaign_data)
        }
    
    def optimize_budget_allocation(self, budget: float, channels: List[str], 
                                 historical_performance: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Optimize budget allocation across multiple channels"""
        
        if not channels or budget <= 0:
            return {channel: 0.0 for channel in channels}
        
        # Calculate channel efficiency scores
        channel_scores = self._calculate_channel_efficiency(channels, historical_performance)
        
        # Apply optimization algorithm
        allocation = self._apply_budget_optimization_algorithm(budget, channel_scores)
        
        # Ensure minimum allocation constraints
        allocation = self._apply_allocation_constraints(allocation, budget)
        
        return allocation
    
    def optimize_targeting_parameters(self, target_audience: Dict[str, Any], 
                                    performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize targeting parameters for better performance"""
        
        optimized_targeting = {
            'demographic_optimization': self._optimize_demographics(target_audience, performance_data),
            'behavioral_optimization': self._optimize_behavioral_targeting(target_audience, performance_data),
            'geographic_optimization': self._optimize_geographic_targeting(target_audience, performance_data),
            'temporal_optimization': self._optimize_temporal_targeting(performance_data),
            'lookalike_optimization': self._optimize_lookalike_audiences(target_audience, performance_data)
        }
        
        return {
            'optimized_parameters': optimized_targeting,
            'expected_improvement': self._calculate_expected_improvement(optimized_targeting),
            'confidence_level': self._calculate_optimization_confidence(optimized_targeting),
            'testing_recommendations': self._generate_testing_recommendations(optimized_targeting)
        }
    
    def optimize_creative_strategy(self, creative_data: Dict[str, Any], 
                                 engagement_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Optimize creative strategy based on performance data"""
        
        creative_optimizations = {
            'message_optimization': self._optimize_messaging(creative_data, engagement_metrics),
            'visual_optimization': self._optimize_visuals(creative_data, engagement_metrics),
            'format_optimization': self._optimize_creative_formats(creative_data, engagement_metrics),
            'cta_optimization': self._optimize_call_to_action(creative_data, engagement_metrics),
            'personalization_optimization': self._optimize_personalization(creative_data, engagement_metrics)
        }
        
        return {
            'creative_optimizations': creative_optimizations,
            'performance_predictions': self._predict_creative_performance(creative_optimizations),
            'testing_strategy': self._create_creative_testing_strategy(creative_optimizations),
            'implementation_priority': self._prioritize_creative_optimizations(creative_optimizations)
        }
    
    def generate_adaptive_rules(self, context: Dict[str, Any], 
                              optimization_goals: List[str]) -> List[Dict[str, Any]]:
        """Generate adaptive optimization rules based on context and goals"""
        
        rules = []
        
        for goal in optimization_goals:
            rule_set = self._generate_goal_specific_rules(goal, context)
            rules.extend(rule_set)
        
        # Add contextual rules
        contextual_rules = self._generate_contextual_rules(context)
        rules.extend(contextual_rules)
        
        # Prioritize and validate rules
        rules = self._prioritize_rules(rules)
        rules = self._validate_rules(rules)
        
        return rules
    
    def _analyze_performance(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analyze performance metrics to identify patterns"""
        analysis = {
            'performance_score': self._calculate_overall_performance_score(metrics),
            'metric_trends': self._analyze_metric_trends(metrics),
            'performance_categories': self._categorize_performance_metrics(metrics),
            'improvement_potential': self._assess_improvement_potential(metrics)
        }
        
        return analysis
    
    def _identify_optimization_opportunities(self, campaign_data: Dict[str, Any], 
                                          metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities using dynamic configuration"""
        opportunities = []
        
        # Get thresholds from configuration instead of hardcoded values
        thresholds = self.config_manager.get('optimization_engine.performance_thresholds', {})
        opportunity_config = self.config_manager.get('optimization_engine.opportunity_detection', {})
        
        default_target_cpa = thresholds.get('target_cpa', 100)
        low_ctr_threshold = opportunity_config.get('low_ctr_threshold', 0.02)
        low_conversion_threshold = opportunity_config.get('low_conversion_threshold', 0.05)
        
        # Budget optimization opportunities
        target_cpa = metrics.get('target_cpa', default_target_cpa)
        current_cpa = metrics.get('cost_per_acquisition', 0)
        if current_cpa > target_cpa * opportunity_config.get('high_cpa_threshold_multiplier', 1.0):
            opportunities.append({
                'type': 'budget_optimization',
                'description': 'Reduce cost per acquisition through budget reallocation',
                'potential_impact': 'high',
                'difficulty': 'medium'
            })
        
        # Targeting optimization opportunities
        if metrics.get('click_through_rate', 0) < low_ctr_threshold:
            opportunities.append({
                'type': 'targeting_optimization',
                'description': 'Improve targeting to increase engagement',
                'potential_impact': 'high',
                'difficulty': 'medium'
            })
        
        # Creative optimization opportunities
        if metrics.get('conversion_rate', 0) < low_conversion_threshold:
            opportunities.append({
                'type': 'creative_optimization',
                'description': 'Enhance creative elements to improve conversions',
                'potential_impact': 'medium',
                'difficulty': 'low'
            })
        
        return opportunities
    
    def _generate_optimization_recommendations(self, opportunities: List[Dict[str, Any]], 
                                            performance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific optimization recommendations"""
        recommendations = []
        
        for opportunity in opportunities:
            rec = {
                'opportunity_type': opportunity['type'],
                'recommendation': self._create_specific_recommendation(opportunity, performance_analysis),
                'expected_impact': opportunity['potential_impact'],
                'implementation_effort': opportunity['difficulty'],
                'timeline': self._estimate_implementation_timeline(opportunity),
                'success_metrics': self._define_success_metrics(opportunity)
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _calculate_channel_efficiency(self, channels: List[str], 
                                    historical_performance: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate efficiency scores for each channel using dynamic configuration"""
        efficiency_scores = {}
        
        # Get configuration values instead of hardcoded parameters
        budget_config = self.config_manager.get('optimization_engine.budget_optimization', {})
        weights = self.config_manager.get('optimization_engine.efficiency_weights', {})
        
        roas_normalization = budget_config.get('roas_normalization_factor', 5.0)
        cpa_normalization = budget_config.get('cpa_normalization_factor', 200.0)
        volume_normalization = budget_config.get('volume_normalization_factor', 1000.0)
        default_score = budget_config.get('default_channel_score', 0.5)
        
        roas_weight = weights.get('roas_weight', 0.4)
        cpa_weight = weights.get('cpa_weight', 0.4)
        volume_weight = weights.get('volume_weight', 0.2)
        
        for channel in channels:
            if channel in historical_performance:
                perf_data = historical_performance[channel]
                
                # Calculate efficiency score based on ROAS, CPA, and volume
                roas = perf_data.get('roas', 1.0)
                cpa = perf_data.get('cpa', 100.0)
                volume = perf_data.get('conversions', 0)
                
                # Normalize and weight factors using configuration
                roas_score = min(1.0, roas / roas_normalization)
                cpa_score = max(0.0, 1.0 - (cpa / cpa_normalization))
                volume_score = min(1.0, volume / volume_normalization)
                
                efficiency_scores[channel] = (roas_score * roas_weight + cpa_score * cpa_weight + volume_score * volume_weight)
            else:
                efficiency_scores[channel] = default_score
        
        return efficiency_scores
    
    def _apply_budget_optimization_algorithm(self, budget: float, 
                                           channel_scores: Dict[str, float]) -> Dict[str, float]:
        """Apply optimization algorithm to allocate budget"""
        total_score = sum(channel_scores.values())
        
        if total_score == 0:
            # Equal allocation if no performance data
            per_channel = budget / len(channel_scores)
            return {channel: per_channel for channel in channel_scores}
        
        # Weighted allocation based on efficiency scores
        allocation = {}
        for channel, score in channel_scores.items():
            allocation[channel] = budget * (score / total_score)
        
        return allocation
    
    def _apply_allocation_constraints(self, allocation: Dict[str, float], 
                                   total_budget: float) -> Dict[str, float]:
        """Apply minimum allocation constraints using dynamic configuration"""
        # Get minimum allocation percentage from configuration instead of hardcoded 5%
        budget_config = self.config_manager.get('optimization_engine.budget_optimization', {})
        min_allocation_pct = budget_config.get('min_allocation_percentage', 0.05)
        min_allocation = total_budget * min_allocation_pct
        
        constrained_allocation = {}
        remaining_budget = total_budget
        
        # First pass: ensure minimum allocation
        for channel, amount in allocation.items():
            constrained_allocation[channel] = max(min_allocation, amount)
            remaining_budget -= constrained_allocation[channel]
        
        # Second pass: redistribute if over-allocated
        if remaining_budget < 0:
            # Scale down proportionally
            scale_factor = total_budget / sum(constrained_allocation.values())
            constrained_allocation = {
                channel: amount * scale_factor 
                for channel, amount in constrained_allocation.items()
            }
        
        return constrained_allocation
    
    def _optimize_demographics(self, target_audience: Dict[str, Any], 
                             performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize demographic targeting parameters"""
        return {
            'age_ranges': self._optimize_age_targeting(target_audience, performance_data),
            'gender_distribution': self._optimize_gender_targeting(target_audience, performance_data),
            'income_levels': self._optimize_income_targeting(target_audience, performance_data)
        }
    
    def _optimize_behavioral_targeting(self, target_audience: Dict[str, Any], 
                                     performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize behavioral targeting parameters"""
        return {
            'interests': self._optimize_interest_targeting(target_audience, performance_data),
            'behaviors': self._optimize_behavior_targeting(target_audience, performance_data),
            'purchase_intent': self._optimize_purchase_intent_targeting(target_audience, performance_data)
        }
    
    def _determine_primary_optimization_focus(self, performance_analysis: Dict[str, Any]) -> str:
        """Determine the primary focus for optimization efforts using dynamic configuration"""
        performance_score = performance_analysis.get('performance_score', 0.5)
        
        # Get performance scoring thresholds from configuration instead of hardcoded values
        scoring_config = self.config_manager.get('optimization_engine.optimization_scoring', {})
        poor_threshold = scoring_config.get('performance_poor', 0.3)
        good_threshold = scoring_config.get('performance_good', 0.6)
        
        if performance_score < poor_threshold:
            return 'comprehensive_overhaul'
        elif performance_score < good_threshold:
            return 'targeted_improvements'
        else:
            return 'fine_tuning'
    
    def _get_optimization_dimensions(self, campaign_data: Dict[str, Any]) -> List[str]:
        """Get relevant optimization dimensions for the campaign"""
        dimensions = ['targeting', 'budget_allocation', 'creative']
        
        if campaign_data.get('multichannel', False):
            dimensions.append('channel_mix')
        
        if campaign_data.get('automated_bidding', False):
            dimensions.append('bidding_strategy')
        
        return dimensions
    
    # Helper methods with placeholder implementations
    def _determine_optimization_frequency(self, performance_analysis: Dict[str, Any]) -> str:
        """Determine optimization frequency using dynamic configuration"""
        performance_score = performance_analysis.get('performance_score', 0.5)
        freq_config = self.config_manager.get('optimization_engine.optimization_frequency', {})
        daily_threshold = freq_config.get('daily_threshold', 0.6)
        
        return 'daily' if performance_score < daily_threshold else 'weekly'
    
    def _calculate_success_thresholds(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate success thresholds using dynamic configuration"""
        threshold_config = self.config_manager.get('optimization_engine.success_thresholds', {})
        
        return {
            'min_roas': metrics.get('target_roas', threshold_config.get('default_min_roas', 3.0)),
            'max_cpa': metrics.get('target_cpa', threshold_config.get('default_max_cpa', 50.0)),
            'min_ctr': threshold_config.get('default_min_ctr', 0.02),
            'min_conversion_rate': threshold_config.get('default_min_conversion_rate', 0.03)
        }
    
    def _generate_adaptation_rules(self, performance_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate adaptation rules using dynamic configuration"""
        rules_config = self.config_manager.get('optimization_engine.adaptation_rules', {})
        
        high_performer_mult = rules_config.get('high_performer_multiplier', 1.5)
        underperformer_mult = rules_config.get('underperformer_multiplier', 0.5)
        audience_expansion_mult = rules_config.get('audience_expansion_multiplier', 2.0)
        
        return [
            {'rule': 'increase_budget_for_high_performers', 'threshold': f'{high_performer_mult}x_target_roas'},
            {'rule': 'pause_underperforming_ads', 'threshold': f'{underperformer_mult}x_target_roas'},
            {'rule': 'expand_successful_audiences', 'threshold': f'{audience_expansion_mult}x_avg_ctr'}
        ]
    
    def _create_implementation_plan(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            'phase_1': 'Quick wins and low-effort optimizations',
            'phase_2': 'Medium-effort targeting and creative improvements',
            'phase_3': 'Comprehensive strategy overhaul',
            'timeline': '4-6 weeks'
        }
    
    def _create_monitoring_framework(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring framework using dynamic configuration"""
        monitoring_config = self.config_manager.get('optimization_engine.monitoring', {})
        threshold_config = self.config_manager.get('optimization_engine.success_thresholds', {})
        
        key_metrics = monitoring_config.get('key_metrics', ['roas', 'cpa', 'ctr', 'conversion_rate'])
        frequency = monitoring_config.get('default_frequency', 'daily')
        roas_drop_alert = threshold_config.get('roas_drop_alert', 0.2)
        cpa_increase_alert = threshold_config.get('cpa_increase_alert', 0.3)
        
        return {
            'key_metrics': key_metrics,
            'monitoring_frequency': frequency,
            'alert_thresholds': {'roas_drop': roas_drop_alert, 'cpa_increase': cpa_increase_alert}
        }
    
    # Additional placeholder methods for comprehensive optimization
    def _calculate_overall_performance_score(self, metrics: Dict[str, float]) -> float:
        return sum(metrics.values()) / len(metrics) if metrics else 0.5
    
    def _analyze_metric_trends(self, metrics: Dict[str, float]) -> Dict[str, str]:
        return {metric: 'stable' for metric in metrics}
    
    def _categorize_performance_metrics(self, metrics: Dict[str, float]) -> Dict[str, List[str]]:
        return {'good': [], 'needs_improvement': [], 'critical': []}
    
    def _assess_improvement_potential(self, metrics: Dict[str, float]) -> float:
        """Assess improvement potential using dynamic configuration"""
        scoring_config = self.config_manager.get('optimization_engine.optimization_scoring', {})
        return scoring_config.get('improvement_potential_default', 0.3)
    
    def _create_specific_recommendation(self, opportunity: Dict[str, Any], 
                                      performance_analysis: Dict[str, Any]) -> str:
        return f"Implement {opportunity['type']} based on {opportunity['description']}"
    
    def _estimate_implementation_timeline(self, opportunity: Dict[str, Any]) -> str:
        """Estimate implementation timeline using dynamic configuration"""
        timeline_config = self.config_manager.get('optimization_engine.timeline_estimates', {})
        
        difficulty_map = {
            'low': timeline_config.get('low_difficulty', '1-2 weeks'),
            'medium': timeline_config.get('medium_difficulty', '2-4 weeks'),
            'high': timeline_config.get('high_difficulty', '4-8 weeks')
        }
        
        return difficulty_map.get(opportunity['difficulty'], timeline_config.get('default_timeline', '2-4 weeks'))
    
    def _define_success_metrics(self, opportunity: Dict[str, Any]) -> List[str]:
        return ['improvement_percentage', 'cost_reduction', 'performance_increase']


# Singleton instance for easy import
_optimization_engine = None

def get_optimization_engine() -> OptimizationEngine:
    """Get shared OptimizationEngine instance"""
    global _optimization_engine
    if _optimization_engine is None:
        _optimization_engine = OptimizationEngine()
    return _optimization_engine
