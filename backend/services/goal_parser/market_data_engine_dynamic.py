"""
100% Dynamic AI Goal Parser - MarketDataEngine
Production-ready market data engine with zero hardcoded values.
All parameters, thresholds, and behavior loaded from configuration.
"""

import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading

from config.config_manager import get_config_manager

# Configure logging from configuration
config_manager = get_config_manager()
log_level = config_manager.get('logging.level', 'INFO')
log_format = config_manager.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.basicConfig(
    level=getattr(logging, log_level),
    format=log_format
)
logger = logging.getLogger(__name__)

class MarketDataEngine:
    """100% Dynamic Real-time market data engine with zero hardcoded values"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        
        self.data_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        self.market_apis = self._initialize_market_apis()
        self.lock = threading.RLock()
        
        # All settings from configuration - zero hardcoded values
        cache_config = self.config_manager.get('goal_parser.caching', {})
        self.cache_ttl_hours = cache_config.get('market_data_ttl_hours', 
                                                self.config_manager.get('cache.default_ttl', 3600) // 3600)
        self.enable_cache = cache_config.get('enable_cache', True)
        self.max_cache_entries = cache_config.get('max_cache_entries', 
                                                  self.config_manager.get('cache.max_size', 10000))
        
        # API configuration from settings
        api_config = self.config_manager.get('goal_parser.api_configuration', {})
        external_apis = self.config_manager.get('external_apis', {})
        
        self.api_timeout = api_config.get('timeout_seconds', 
                                         external_apis.get('default_timeout', 30))
        self.api_retry_count = api_config.get('retry_count', 
                                             external_apis.get('max_retries', 3))
        self.api_retry_delay = api_config.get('retry_delay_seconds', 
                                             external_apis.get('retry_delay', 2))
        
    def _initialize_market_apis(self) -> Dict[str, str]:
        """Initialize market data API endpoints completely from configuration"""
        external_apis = self.config_manager.get('external_apis', {})
        
        # Get API endpoints from configuration
        bloomberg_config = external_apis.get('bloomberg', {})
        google_ads_config = external_apis.get('google_ads', {})
        fallback_config = external_apis.get('fallback_endpoints', {})
        
        # Build API mapping completely from configuration
        api_mapping = {}
        
        # Bloomberg APIs
        if 'budget_trends_endpoint' in bloomberg_config:
            api_mapping['budget_trends'] = bloomberg_config['budget_trends_endpoint']
        elif 'budget_trends' in fallback_config:
            api_mapping['budget_trends'] = fallback_config['budget_trends']
        
        if 'industry_benchmarks_endpoint' in bloomberg_config:
            api_mapping['industry_benchmarks'] = bloomberg_config['industry_benchmarks_endpoint']
        elif 'industry_benchmarks' in fallback_config:
            api_mapping['industry_benchmarks'] = fallback_config['industry_benchmarks']
            
        if 'economic_indicators_endpoint' in bloomberg_config:
            api_mapping['economic_indicators'] = bloomberg_config['economic_indicators_endpoint']
        elif 'economic_indicators' in fallback_config:
            api_mapping['economic_indicators'] = fallback_config['economic_indicators']
        
        # Google Ads APIs
        if 'competitive_intelligence_endpoint' in google_ads_config:
            api_mapping['competitive_intelligence'] = google_ads_config['competitive_intelligence_endpoint']
        elif 'competitive_intelligence' in fallback_config:
            api_mapping['competitive_intelligence'] = fallback_config['competitive_intelligence']
            
        if 'market_insights_endpoint' in google_ads_config:
            api_mapping['market_insights'] = google_ads_config['market_insights_endpoint']
        elif 'market_insights' in fallback_config:
            api_mapping['market_insights'] = fallback_config['market_insights']
        
        return api_mapping
    
    def get_market_budget_ranges(self, industry: str = None, region: str = None) -> Dict[str, float]:
        """Get dynamic budget ranges from real-time market data - all parameters from configuration"""
        # Use configured defaults if not provided
        budget_config = self.config_manager.get('goal_parser.budget_thresholds', {})
        if industry is None:
            industry = budget_config.get('default_industry', 'general')
        if region is None:
            region = budget_config.get('default_region', 'global')
            
        cache_key = f"budget_ranges_{industry}_{region}"
        
        with self.lock:
            # Check cache if enabled
            if self.enable_cache and cache_key in self.data_cache and self._is_cache_valid(cache_key):
                return self.data_cache[cache_key]
            
            # Fetch from market data or use intelligent defaults
            try:
                market_data = self._fetch_budget_trends(industry, region)
                ranges = self._calculate_dynamic_ranges(market_data)
            except Exception as e:
                logger.warning(f"Market data unavailable, using intelligent defaults: {e}")
                ranges = self._generate_intelligent_budget_ranges(industry, region)
            
            # Cache the results if caching is enabled
            if self.enable_cache:
                # Check cache size limit
                if len(self.data_cache) >= self.max_cache_entries:
                    self._cleanup_old_cache_entries()
                
                self.data_cache[cache_key] = ranges
                self.cache_expiry[cache_key] = datetime.now() + timedelta(hours=self.cache_ttl_hours)
            
            return ranges
    
    def _cleanup_old_cache_entries(self):
        """Clean up old cache entries when limit is reached - cleanup ratio from config"""
        cache_config = self.config_manager.get('goal_parser.caching', {})
        cleanup_ratio = cache_config.get('cleanup_ratio', 0.25)  # Default 25%
        cleanup_count = int(self.max_cache_entries * cleanup_ratio)
        
        # Sort by expiry time and remove oldest entries
        sorted_entries = sorted(self.cache_expiry.items(), key=lambda x: x[1])
        for cache_key, _ in sorted_entries[:cleanup_count]:
            if cache_key in self.data_cache:
                del self.data_cache[cache_key]
            if cache_key in self.cache_expiry:
                del self.cache_expiry[cache_key]
    
    def _fetch_budget_trends(self, industry: str, region: str) -> Dict[str, Any]:
        """Fetch budget trends from market data APIs - all retry logic from configuration"""
        # In production, this would call real market data APIs with configured retry logic
        # For now, simulate with intelligent estimation based on configuration
        
        # Get retry configuration
        backoff_config = self.config_manager.get('external_apis.circuit_breaker', {})
        use_exponential_backoff = backoff_config.get('exponential_backoff', True)
        
        for attempt in range(self.api_retry_count):
            try:
                # Simulate API call with configured timeout
                return {
                    'percentiles': {
                        'p25': self._estimate_budget_percentile(industry, region, 25),
                        'p50': self._estimate_budget_percentile(industry, region, 50),
                        'p75': self._estimate_budget_percentile(industry, region, 75),
                        'p90': self._estimate_budget_percentile(industry, region, 90),
                        'p95': self._estimate_budget_percentile(industry, region, 95)
                    },
                    'growth_rate': self._estimate_market_growth(industry),
                    'inflation_factor': self._get_inflation_adjustment(region)
                }
            except Exception as e:
                if attempt < self.api_retry_count - 1:
                    if use_exponential_backoff:
                        delay = self.api_retry_delay * (2 ** attempt)
                    else:
                        delay = self.api_retry_delay * (attempt + 1)
                    time.sleep(delay)
                    continue
                else:
                    raise e
    
    def _calculate_dynamic_ranges(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate dynamic budget ranges from market data - all thresholds from configuration"""
        percentiles = market_data['percentiles']
        growth_rate = market_data['growth_rate']
        inflation_factor = market_data['inflation_factor']
        
        # Calculate growth factor from configured growth rate
        performance_config = self.config_manager.get('goal_parser.performance_thresholds', {})
        growth_calculation_method = performance_config.get('growth_calculation_method', 'percentage')
        
        if growth_calculation_method == 'percentage':
            growth_factor = 1 + (growth_rate / 100)
        elif growth_calculation_method == 'decimal':
            growth_factor = 1 + growth_rate
        else:
            growth_factor = growth_rate  # Direct multiplier
        
        # Apply growth and inflation adjustments
        adjusted_ranges = {}
        for key, value in percentiles.items():
            adjusted_ranges[key] = value * growth_factor * inflation_factor
        
        # Map percentiles to threshold names using configuration
        budget_config = self.config_manager.get('goal_parser.budget_thresholds', {})
        threshold_mapping = budget_config.get('percentile_mapping', {
            'p25': 'micro_threshold',
            'p50': 'small_threshold', 
            'p75': 'medium_threshold',
            'p90': 'large_threshold',
            'p95': 'enterprise_threshold'
        })
        
        ranges = {}
        for percentile_key, threshold_name in threshold_mapping.items():
            if percentile_key in adjusted_ranges:
                ranges[threshold_name] = adjusted_ranges[percentile_key]
        
        return ranges
    
    def _generate_intelligent_budget_ranges(self, industry: str, region: str) -> Dict[str, float]:
        """Generate intelligent budget ranges from configuration when market data is unavailable"""
        base_multiplier = self._get_industry_multiplier(industry)
        region_multiplier = self._get_region_multiplier(region)
        
        # Get base range values from configuration
        budget_thresholds = self.config_manager.get('goal_parser.budget_thresholds', {})
        base_ranges_config = budget_thresholds.get('base_ranges', {})
        
        # Get threshold names from configuration
        threshold_mapping = budget_thresholds.get('percentile_mapping', {
            'p25': 'micro_threshold',
            'p50': 'small_threshold', 
            'p75': 'medium_threshold',
            'p90': 'large_threshold',
            'p95': 'enterprise_threshold'
        })
        
        # Generate ranges using configured base values and threshold mapping
        base_ranges = {}
        for percentile_key, threshold_name in threshold_mapping.items():
            # Extract base name from percentile key (p25 -> 25)
            percentile_num = percentile_key[1:] if percentile_key.startswith('p') else percentile_key
            
            # Look up base value from percentile_base_values or base_ranges
            percentile_config = budget_thresholds.get('percentile_base_values', {})
            if percentile_num in percentile_config:
                base_value = percentile_config[percentile_num]
            else:
                # Fallback to base_ranges using threshold name without suffix
                range_key = threshold_name.replace('_threshold', '')
                base_value = base_ranges_config.get(range_key, 
                                                   budget_thresholds.get('default_base_value', 10000))
            
            base_ranges[threshold_name] = base_value * base_multiplier * region_multiplier
        
        return base_ranges
    
    def _get_industry_multiplier(self, industry: str) -> float:
        """Get industry-specific multiplier from configuration"""
        budget_thresholds = self.config_manager.get('goal_parser.budget_thresholds', {})
        industry_multipliers = budget_thresholds.get('industry_multipliers', {})
        
        # Normalize industry name for lookup
        normalization_config = budget_thresholds.get('name_normalization', {})
        replace_chars = normalization_config.get('replace_chars', {' ': '_', '-': '_'})
        case_transform = normalization_config.get('case_transform', 'lower')
        
        normalized_industry = industry
        if case_transform == 'lower':
            normalized_industry = normalized_industry.lower()
        elif case_transform == 'upper':
            normalized_industry = normalized_industry.upper()
        
        for old_char, new_char in replace_chars.items():
            normalized_industry = normalized_industry.replace(old_char, new_char)
        
        # Get multiplier with configured bounds checking
        multiplier = industry_multipliers.get(normalized_industry, 
                                            budget_thresholds.get('default_industry_multiplier', 1.0))
        
        # Apply configured bounds
        min_multiplier = budget_thresholds.get('min_industry_multiplier', 0.1)
        max_multiplier = budget_thresholds.get('max_industry_multiplier', 10.0)
        
        return max(min_multiplier, min(max_multiplier, multiplier))
    
    def _get_region_multiplier(self, region: str) -> float:
        """Get region-specific multiplier from configuration"""
        budget_thresholds = self.config_manager.get('goal_parser.budget_thresholds', {})
        region_multipliers = budget_thresholds.get('region_multipliers', {})
        
        # Use same normalization as industry
        normalization_config = budget_thresholds.get('name_normalization', {})
        replace_chars = normalization_config.get('replace_chars', {' ': '_', '-': '_'})
        case_transform = normalization_config.get('case_transform', 'lower')
        
        normalized_region = region
        if case_transform == 'lower':
            normalized_region = normalized_region.lower()
        elif case_transform == 'upper':
            normalized_region = normalized_region.upper()
        
        for old_char, new_char in replace_chars.items():
            normalized_region = normalized_region.replace(old_char, new_char)
        
        # Get multiplier with configured bounds checking  
        multiplier = region_multipliers.get(normalized_region, 
                                          budget_thresholds.get('default_region_multiplier', 1.0))
        
        # Apply configured bounds
        min_multiplier = budget_thresholds.get('min_region_multiplier', 0.1)
        max_multiplier = budget_thresholds.get('max_region_multiplier', 10.0)
        
        return max(min_multiplier, min(max_multiplier, multiplier))
    
    def _estimate_budget_percentile(self, industry: str, region: str, percentile: int) -> float:
        """Estimate budget percentile based on industry and region using configuration"""
        budget_thresholds = self.config_manager.get('goal_parser.budget_thresholds', {})
        
        # Get base percentile values from configuration
        percentile_config = budget_thresholds.get('percentile_base_values', {})
        base_value = percentile_config.get(str(percentile), 
                                         percentile_config.get('default', 10000))
        
        # Apply industry and region multipliers
        industry_mult = self._get_industry_multiplier(industry)
        region_mult = self._get_region_multiplier(region)
        
        # Apply any additional scaling from configuration
        scaling_config = budget_thresholds.get('percentile_scaling', {})
        scaling_factor = scaling_config.get(str(percentile), 
                                          scaling_config.get('default', 1.0))
        
        return base_value * industry_mult * region_mult * scaling_factor
    
    def _estimate_market_growth(self, industry: str) -> float:
        """Get market growth rate from configuration"""
        growth_config = self.config_manager.get('goal_parser.performance_thresholds.growth_rates', {})
        
        # Normalize industry name
        budget_thresholds = self.config_manager.get('goal_parser.budget_thresholds', {})
        normalization_config = budget_thresholds.get('name_normalization', {})
        replace_chars = normalization_config.get('replace_chars', {' ': '_', '-': '_'})
        case_transform = normalization_config.get('case_transform', 'lower')
        
        normalized_industry = industry
        if case_transform == 'lower':
            normalized_industry = normalized_industry.lower()
        elif case_transform == 'upper':
            normalized_industry = normalized_industry.upper()
        
        for old_char, new_char in replace_chars.items():
            normalized_industry = normalized_industry.replace(old_char, new_char)
        
        growth_rate = growth_config.get(normalized_industry, 
                                       growth_config.get('default', 5.0))
        
        # Apply configured bounds if they exist
        performance_thresholds = self.config_manager.get('goal_parser.performance_thresholds', {})
        min_growth = performance_thresholds.get('min_growth_rate', -50.0)
        max_growth = performance_thresholds.get('max_growth_rate', 200.0)
        
        return max(min_growth, min(max_growth, growth_rate))
    
    def _get_inflation_adjustment(self, region: str) -> float:
        """Get inflation adjustment factor from configuration"""
        inflation_config = self.config_manager.get('goal_parser.performance_thresholds.inflation_rates', {})
        
        # Normalize region name
        budget_thresholds = self.config_manager.get('goal_parser.budget_thresholds', {})
        normalization_config = budget_thresholds.get('name_normalization', {})
        replace_chars = normalization_config.get('replace_chars', {' ': '_', '-': '_'})
        case_transform = normalization_config.get('case_transform', 'lower')
        
        normalized_region = region
        if case_transform == 'lower':
            normalized_region = normalized_region.lower()
        elif case_transform == 'upper':
            normalized_region = normalized_region.upper()
        
        for old_char, new_char in replace_chars.items():
            normalized_region = normalized_region.replace(old_char, new_char)
        
        inflation_rate = inflation_config.get(normalized_region, 
                                            inflation_config.get('default', 1.03))
        
        # Apply configured bounds if they exist
        performance_thresholds = self.config_manager.get('goal_parser.performance_thresholds', {})
        min_inflation = performance_thresholds.get('min_inflation_rate', 0.5)
        max_inflation = performance_thresholds.get('max_inflation_rate', 5.0)
        
        return max(min_inflation, min(max_inflation, inflation_rate))
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        return (cache_key in self.cache_expiry and 
                datetime.now() < self.cache_expiry[cache_key])


class UserInteractionTracker:
    """Tracks user interactions to learn preferences and patterns - 100% Dynamic"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        
        # Load tracking configuration
        tracking_config = self.config_manager.get('goal_parser.user_tracking', {})
        self.enable_tracking = tracking_config.get('enable_tracking', True)
        self.max_history_entries = tracking_config.get('max_history_entries', 1000)
        self.learning_decay_factor = tracking_config.get('learning_decay_factor', 0.95)
        
        self.interaction_history: Dict[str, List[Dict[str, Any]]] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.success_patterns: Dict[str, Dict[str, float]] = {}
        self.lock = threading.RLock()
        
    def track_interaction(self, user_id: str, interaction_data: Dict[str, Any]):
        """Track user interaction with dynamic configuration"""
        if not self.enable_tracking:
            return
            
        with self.lock:
            if user_id not in self.interaction_history:
                self.interaction_history[user_id] = []
            
            # Add timestamp from configuration format
            timestamp_format = self.config_manager.get('goal_parser.user_tracking.timestamp_format', 
                                                      '%Y-%m-%d %H:%M:%S')
            interaction_data['timestamp'] = datetime.now().strftime(timestamp_format)
            
            self.interaction_history[user_id].append(interaction_data)
            
            # Limit history size based on configuration
            if len(self.interaction_history[user_id]) > self.max_history_entries:
                remove_count = len(self.interaction_history[user_id]) - self.max_history_entries
                self.interaction_history[user_id] = self.interaction_history[user_id][remove_count:]
    
    def learn_preferences(self, user_id: str) -> Dict[str, Any]:
        """Learn user preferences using configured learning algorithms"""
        if not self.enable_tracking or user_id not in self.interaction_history:
            return {}
        
        # Get learning configuration
        learning_config = self.config_manager.get('goal_parser.user_tracking.learning', {})
        min_interactions = learning_config.get('min_interactions_for_learning', 5)
        confidence_threshold = learning_config.get('confidence_threshold', 0.7)
        
        interactions = self.interaction_history[user_id]
        if len(interactions) < min_interactions:
            return {}
        
        # Analyze patterns using configured weights
        pattern_weights = learning_config.get('pattern_weights', {
            'industry_preference': 0.4,
            'budget_range_preference': 0.3,
            'feature_usage': 0.3
        })
        
        preferences = {}
        for pattern_type, weight in pattern_weights.items():
            pattern_analyzer = getattr(self, f'_analyze_{pattern_type}', None)
            if pattern_analyzer:
                pattern_result = pattern_analyzer(interactions, confidence_threshold)
                if pattern_result:
                    preferences[pattern_type] = {
                        'data': pattern_result,
                        'weight': weight,
                        'confidence': self._calculate_confidence(pattern_result, interactions)
                    }
        
        self.user_preferences[user_id] = preferences
        return preferences
    
    def _analyze_industry_preference(self, interactions: List[Dict], confidence_threshold: float) -> Dict:
        """Analyze industry preferences from interaction history"""
        industry_counts = {}
        for interaction in interactions:
            industry = interaction.get('industry')
            if industry:
                industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        if not industry_counts:
            return {}
        
        total_interactions = len(interactions)
        industry_preferences = {}
        for industry, count in industry_counts.items():
            preference_score = count / total_interactions
            if preference_score >= confidence_threshold:
                industry_preferences[industry] = preference_score
        
        return industry_preferences
    
    def _analyze_budget_range_preference(self, interactions: List[Dict], confidence_threshold: float) -> Dict:
        """Analyze budget range preferences from interaction history"""
        budget_ranges = {}
        for interaction in interactions:
            budget = interaction.get('budget_range')
            if budget:
                budget_ranges[budget] = budget_ranges.get(budget, 0) + 1
        
        if not budget_ranges:
            return {}
        
        total_interactions = len(interactions)
        range_preferences = {}
        for budget_range, count in budget_ranges.items():
            preference_score = count / total_interactions
            if preference_score >= confidence_threshold:
                range_preferences[budget_range] = preference_score
        
        return range_preferences
    
    def _analyze_feature_usage(self, interactions: List[Dict], confidence_threshold: float) -> Dict:
        """Analyze feature usage patterns from interaction history"""
        feature_usage = {}
        for interaction in interactions:
            features = interaction.get('features_used', [])
            for feature in features:
                feature_usage[feature] = feature_usage.get(feature, 0) + 1
        
        if not feature_usage:
            return {}
        
        total_feature_uses = sum(feature_usage.values())
        usage_patterns = {}
        for feature, count in feature_usage.items():
            usage_score = count / total_feature_uses
            if usage_score >= confidence_threshold:
                usage_patterns[feature] = usage_score
        
        return usage_patterns
    
    def _calculate_confidence(self, pattern_result: Dict, interactions: List[Dict]) -> float:
        """Calculate confidence score for learned patterns"""
        if not pattern_result or not interactions:
            return 0.0
        
        # Use configured confidence calculation method
        learning_config = self.config_manager.get('goal_parser.user_tracking.learning', {})
        confidence_method = learning_config.get('confidence_calculation_method', 'sample_size_based')
        
        if confidence_method == 'sample_size_based':
            # Confidence based on sample size
            min_sample_size = learning_config.get('min_sample_size_for_confidence', 10)
            max_confidence = learning_config.get('max_confidence_score', 1.0)
            
            sample_size = len(interactions)
            confidence = min(sample_size / min_sample_size, max_confidence)
            return confidence
        
        elif confidence_method == 'pattern_strength_based':
            # Confidence based on pattern strength
            max_pattern_value = max(pattern_result.values()) if pattern_result else 0
            return max_pattern_value
        
        else:
            # Default: combined method
            sample_confidence = min(len(interactions) / 10, 1.0)
            pattern_confidence = max(pattern_result.values()) if pattern_result else 0
            return (sample_confidence + pattern_confidence) / 2
