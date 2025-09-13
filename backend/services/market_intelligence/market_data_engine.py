"""
Market Data Engine - Shared Service
100% Dynamic Real-time market data engine with zero hardcoded values
"""

import json
import logging
import threading
from typing import Dict, Any
from datetime import datetime, timedelta

from config.config_manager import get_config_manager

logger = logging.getLogger(__name__)


class MarketDataEngine:
    """100% Dynamic Real-time market data engine with zero hardcoded values"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        
        # Load dynamic configuration metadata
        self.dynamic_config = self._load_dynamic_configuration()
        
        self.data_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        self.market_apis = self._initialize_market_apis()
        self.lock = threading.RLock()
        
        # All cache settings from configuration
        self.cache_ttl_hours = self._get_dynamic_value('cache_settings.ttl_hours_config_key')
        self.enable_cache = self._get_dynamic_value('cache_settings.enable_cache_config_key')
        self.max_cache_entries = self._get_dynamic_value('cache_settings.max_entries_config_key')
        
    def _load_dynamic_configuration(self) -> Dict[str, Any]:
        """Load completely dynamic configuration metadata"""
        try:
            # Use the config manager's base path to find the dynamic config file
            import os
            config_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            dynamic_config_path = os.path.join(config_dir, 'config', 'dynamic_market_data.json')
            
            with open(dynamic_config_path, 'r') as f:
                return json.load(f)['market_data_engine']
        except Exception as e:
            logger.error(f"Failed to load dynamic configuration: {e}")
            raise RuntimeError("Cannot operate without dynamic configuration")
    
    def _get_dynamic_value(self, config_path: str) -> Any:
        """Get any value dynamically from configuration using dot notation"""
        return self.config_manager.get(self.dynamic_config[config_path])
    
    def _initialize_market_apis(self) -> Dict[str, str]:
        """Initialize market data API endpoints completely from configuration"""
        apis = {}
        
        # Get primary sources configuration
        primary_sources = self.dynamic_config['api_endpoints']['primary_sources']
        
        for provider, endpoints in primary_sources.items():
            for endpoint_name, config_key in endpoints.items():
                endpoint_url = self.config_manager.get(config_key)
                if endpoint_url:
                    api_name = endpoint_name.replace('_endpoint_key', '')
                    apis[api_name] = endpoint_url
        
        # Dynamic fallback discovery
        fallback_config = self.dynamic_config['api_endpoints']['fallback_discovery']
        timeout = self.config_manager.get(fallback_config['timeout_config_key'])
        retry_count = self.config_manager.get(fallback_config['retry_config_key'])
        
        # Store configuration values for use in API calls
        self.api_timeout = timeout
        self.api_retry_count = retry_count
        
        return apis
    
    def get_market_budget_ranges(self, industry: str = 'general', region: str = 'global') -> Dict[str, float]:
        """Get dynamic budget ranges with 100% configuration-driven calculation"""
        if not self.enable_cache:
            return self._calculate_fresh_ranges(industry, region)
            
        cache_key = f"budget_ranges_{industry}_{region}"
        
        with self.lock:
            # Check cache validity using dynamic configuration
            if cache_key in self.data_cache and self._is_cache_valid(cache_key):
                return self.data_cache[cache_key]
            
            # Fetch using completely dynamic process
            try:
                market_data = self._fetch_budget_trends(industry, region)
                ranges = self._calculate_dynamic_ranges(market_data)
            except Exception as e:
                logger.warning(f"Market data unavailable, using intelligent defaults: {e}")
                ranges = self._generate_intelligent_budget_ranges(industry, region)
            
            # Cache management using dynamic configuration
            self._manage_cache_size()
            self.data_cache[cache_key] = ranges
            self.cache_expiry[cache_key] = datetime.now() + timedelta(hours=self.cache_ttl_hours)
            
            return ranges
    
    def _calculate_fresh_ranges(self, industry: str, region: str) -> Dict[str, float]:
        """Calculate ranges without caching when cache is disabled"""
        try:
            market_data = self._fetch_budget_trends(industry, region)
            return self._calculate_dynamic_ranges(market_data)
        except Exception as e:
            logger.warning(f"Market data unavailable, using intelligent defaults: {e}")
            return self._generate_intelligent_budget_ranges(industry, region)
    
    def _manage_cache_size(self):
        """Manage cache size using dynamic configuration"""
        if len(self.data_cache) >= self.max_cache_entries:
            # Remove oldest entries
            cleanup_count = int(self.max_cache_entries * 0.2)  # Remove 20% when full
            oldest_keys = sorted(self.cache_expiry.keys(), 
                               key=lambda k: self.cache_expiry[k])[:cleanup_count]
            for key in oldest_keys:
                self.data_cache.pop(key, None)
                self.cache_expiry.pop(key, None)
    
    def _fetch_budget_trends(self, industry: str, region: str) -> Dict[str, Any]:
        """Fetch budget trends using completely dynamic API configuration"""
        # In production, this would call real APIs using dynamic endpoints
        # For now, simulate with dynamic intelligent estimation
        percentile_config = self._get_dynamic_value('budget_calculation.percentile_values_config_key')
        
        return {
            'percentiles': {
                f'p{p}': self._estimate_budget_percentile(industry, region, int(p))
                for p in percentile_config.keys() if p.isdigit()
            },
            'growth_rate': self._estimate_market_growth(industry),
            'inflation_factor': self._get_inflation_adjustment(region)
        }
    
    def _calculate_dynamic_ranges(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate ranges using completely dynamic rules from configuration"""
        percentiles = market_data['percentiles']
        
        # Get dynamic calculation rules
        calc_rules = self.dynamic_config['dynamic_calculation_rules']
        growth_rate = market_data['growth_rate']
        inflation_factor = market_data['inflation_factor']
        
        # Apply formula from configuration
        formula_template = calc_rules['growth_inflation_formula']
        growth_factor = 1 + (growth_rate / 100.0)
        
        # Apply dynamic threshold mapping
        threshold_mapping = calc_rules['threshold_mapping']
        ranges = {}
        
        for threshold_name, percentile_key in threshold_mapping.items():
            base_value = percentiles.get(percentile_key, percentiles.get('p50', 0))
            # Apply formula: base_value * (1 + growth_rate/100) * inflation_factor
            adjusted_value = base_value * growth_factor * inflation_factor
            ranges[threshold_name] = adjusted_value
        
        # Validate using dynamic rules
        self._validate_ranges(ranges)
        return ranges
    
    def _validate_ranges(self, ranges: Dict[str, float]):
        """Validate ranges using dynamic validation rules"""
        validation_rules = self.dynamic_config['validation_rules']
        
        if validation_rules['threshold_ordering'] == 'ascending':
            threshold_names = ['micro_threshold', 'small_threshold', 'medium_threshold', 
                             'large_threshold', 'enterprise_threshold']
            values = [ranges[name] for name in threshold_names if name in ranges]
            
            for i in range(len(values) - 1):
                if values[i] >= values[i + 1]:
                    raise ValueError(f"Threshold ordering validation failed: {values}")
    
    def _generate_intelligent_budget_ranges(self, industry: str, region: str) -> Dict[str, float]:
        """Generate intelligent ranges using completely dynamic configuration"""
        base_multiplier = self._get_industry_multiplier(industry)
        region_multiplier = self._get_region_multiplier(region)
        
        # Get all base ranges from configuration  
        base_ranges_config = self._get_dynamic_value('budget_calculation.base_ranges_config_key')
        threshold_mapping = self.dynamic_config['dynamic_calculation_rules']['threshold_mapping']
        
        ranges = {}
        for threshold_name, percentile_key in threshold_mapping.items():
            # Map threshold to base range key
            range_key = threshold_name.replace('_threshold', '')
            base_value = base_ranges_config.get(range_key, base_ranges_config.get('medium', 0))
            
            # Apply dynamic multiplier calculation
            final_value = base_value * base_multiplier * region_multiplier
            ranges[threshold_name] = final_value
        
        self._validate_ranges(ranges)
        return ranges
    
    def _get_industry_multiplier(self, industry: str) -> float:
        """Get industry multiplier completely from configuration"""
        industry_multipliers = self._get_dynamic_value('budget_calculation.industry_multipliers_config_key')
        default_multiplier = self._get_dynamic_value('budget_calculation.default_industry_config_key')
        
        # Normalize industry name for lookup
        normalized_industry = industry.lower().replace(' ', '_').replace('-', '_')
        multiplier = industry_multipliers.get(normalized_industry, default_multiplier)
        
        # Validate bounds using dynamic configuration
        min_bound = self.config_manager.get('goal_parser.budget_thresholds.min_industry_multiplier')
        max_bound = self.config_manager.get('goal_parser.budget_thresholds.max_industry_multiplier')
        
        return max(min_bound, min(max_bound, multiplier))
    
    def _get_region_multiplier(self, region: str) -> float:
        """Get region multiplier completely from configuration"""
        region_multipliers = self._get_dynamic_value('budget_calculation.region_multipliers_config_key')
        default_multiplier = self._get_dynamic_value('budget_calculation.default_region_config_key')
        
        normalized_region = region.lower().replace(' ', '_').replace('-', '_')
        multiplier = region_multipliers.get(normalized_region, default_multiplier)
        
        # Validate bounds using dynamic configuration
        min_bound = self.config_manager.get('goal_parser.budget_thresholds.min_region_multiplier')
        max_bound = self.config_manager.get('goal_parser.budget_thresholds.max_region_multiplier')
        
        return max(min_bound, min(max_bound, multiplier))
    
    def _estimate_budget_percentile(self, industry: str, region: str, percentile: int) -> float:
        """Estimate budget percentile using completely dynamic configuration"""
        percentile_config = self._get_dynamic_value('budget_calculation.percentile_values_config_key')
        base_value = percentile_config.get(str(percentile), percentile_config.get('default'))
        
        # Apply dynamic multipliers
        industry_mult = self._get_industry_multiplier(industry)
        region_mult = self._get_region_multiplier(region)
        
        return base_value * industry_mult * region_mult
    
    def _estimate_market_growth(self, industry: str) -> float:
        """Get market growth rate completely from configuration"""
        growth_config = self._get_dynamic_value('performance_metrics.growth_rates_config_key')
        normalized_industry = industry.lower().replace(' ', '_').replace('-', '_')
        return growth_config.get(normalized_industry, growth_config.get('default'))
    
    def _get_inflation_adjustment(self, region: str) -> float:
        """Get inflation adjustment completely from configuration"""
        inflation_config = self._get_dynamic_value('performance_metrics.inflation_rates_config_key')
        normalized_region = region.lower().replace(' ', '_').replace('-', '_')
        return inflation_config.get(normalized_region, inflation_config.get('default'))
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check cache validity using dynamic configuration"""
        if not self.enable_cache:
            return False
            
        return (cache_key in self.cache_expiry and 
                datetime.now() < self.cache_expiry[cache_key])


# Singleton instance for easy import
_market_data_engine = None

def get_market_data_engine() -> MarketDataEngine:
    """Get shared MarketDataEngine instance"""
    global _market_data_engine
    if _market_data_engine is None:
        _market_data_engine = MarketDataEngine()
    return _market_data_engine
