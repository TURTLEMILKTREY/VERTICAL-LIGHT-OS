# 🏗️ DYNAMIC CONFIGURATION ARCHITECTURE
## Production Readiness Implementation - Day 1 Hour 3-4

---

## 📋 CONFIGURATION SYSTEM OVERVIEW

### Core Principles
1. **Environment-Driven**: Different configs for dev/staging/prod
2. **API-First**: Real-time data prioritized over static values  
3. **Intelligent Caching**: Multi-tier caching with smart invalidation
4. **Graceful Fallbacks**: Multiple fallback layers for reliability
5. **Performance Optimized**: <200ms overhead for dynamic lookups

---

## 🔧 CONFIGURATION SCHEMA DESIGN

### 1. Environment Configuration Structure
```yaml
# config/environments/production.yaml
environment: production

cache:
  redis_url: ${REDIS_URL}
  default_ttl: 21600  # 6 hours
  performance_ttl: 3600  # 1 hour for high-change data
  
api_integration:
  market_intelligence:
    primary: "google_ads_api"
    secondary: "facebook_marketing_api" 
    tertiary: "semrush_api"
    
  economic_data:
    primary: "world_bank_api"
    secondary: "imf_api"
    
  rate_limits:
    requests_per_minute: 1000
    burst_allowance: 200
    
dynamic_values:
  budget_classification:
    update_frequency: "PT6H"  # ISO 8601 duration
    sources:
      - api: "market_research_api"
        weight: 0.6
      - api: "industry_benchmarks_api"  
        weight: 0.4
    validation:
      min_threshold_ratio: 0.1
      max_threshold_ratio: 10.0
      
  industry_multipliers:
    update_frequency: "P1D"  # Daily updates
    sources:
      - api: "economic_intelligence_api"
        weight: 0.7
      - api: "competitive_analysis_api"
        weight: 0.3
    validation:
      min_multiplier: 0.3
      max_multiplier: 3.0
      
  channel_performance:
    update_frequency: "PT1H"  # Hourly for performance data
    sources:
      - api: "google_ads_api"
        channels: ["search_advertising"]
        weight: 0.8
      - api: "facebook_marketing_api" 
        channels: ["social_media"]
        weight: 0.8
      - api: "email_intelligence_api"
        channels: ["email_marketing"]
        weight: 0.9
```

### 2. Development Environment Override
```yaml
# config/environments/development.yaml
environment: development

# Simplified for development
api_integration:
  mock_mode: true
  response_delay: 100  # Simulate API latency
  
cache:
  provider: "memory"  # In-memory cache for dev
  default_ttl: 300   # 5 minutes for faster testing
  
dynamic_values:
  budget_classification:
    update_frequency: "PT5M"  # 5 minutes for testing
```

---

## 🔌 API INTEGRATION FRAMEWORK

### 1. Market Intelligence API Wrapper
```python
# config/api_clients.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import aiohttp
import asyncio
from datetime import datetime, timedelta

@dataclass
class APIResponse:
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    confidence: float
    ttl_seconds: int

class MarketIntelligenceAPI(ABC):
    @abstractmethod
    async def get_budget_thresholds(self, region: str, industry: str) -> APIResponse:
        pass
    
    @abstractmethod 
    async def get_industry_multipliers(self, industries: List[str]) -> APIResponse:
        pass
    
    @abstractmethod
    async def get_channel_performance(self, channels: List[str]) -> APIResponse:
        pass

class GoogleAdsIntelligenceAPI(MarketIntelligenceAPI):
    def __init__(self, api_key: str, developer_token: str):
        self.api_key = api_key
        self.developer_token = developer_token
        self.base_url = "https://googleads.googleapis.com/v14"
        
    async def get_budget_thresholds(self, region: str, industry: str) -> APIResponse:
        # Implementation for real Google Ads API integration
        async with aiohttp.ClientSession() as session:
            # Real API call logic here
            pass
    
    async def get_industry_multipliers(self, industries: List[str]) -> APIResponse:
        # Competitive landscape analysis via Google Ads
        pass
        
    async def get_channel_performance(self, channels: List[str]) -> APIResponse:
        # Real-time performance metrics
        pass

class FacebookMarketingAPI(MarketIntelligenceAPI):
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    # Similar implementation for Facebook Marketing API
    pass
```

### 2. Configuration Manager
```python
# config/dynamic_config_manager.py
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yaml
import redis
from functools import wraps

class DynamicConfigManager:
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.config = self._load_config()
        self.redis_client = redis.Redis.from_url(self.config['cache']['redis_url'])
        self.api_clients = self._initialize_api_clients()
        self._background_tasks = set()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        config_path = f"config/environments/{self.environment}.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_api_clients(self) -> Dict[str, MarketIntelligenceAPI]:
        """Initialize API clients based on configuration"""
        clients = {}
        
        # Google Ads API Client
        if 'google_ads_api' in self.config['api_integration']:
            clients['google_ads'] = GoogleAdsIntelligenceAPI(
                api_key=os.getenv('GOOGLE_ADS_API_KEY'),
                developer_token=os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
            )
            
        # Facebook Marketing API Client  
        if 'facebook_marketing_api' in self.config['api_integration']:
            clients['facebook'] = FacebookMarketingAPI(
                access_token=os.getenv('FACEBOOK_ACCESS_TOKEN')
            )
            
        return clients
    
    async def get_dynamic_value(self, 
                               value_type: str, 
                               context: Dict[str, Any] = None,
                               use_cache: bool = True) -> Any:
        """
        Get dynamic value with intelligent fallback system
        
        Args:
            value_type: Type of value (e.g., 'budget_thresholds', 'industry_multipliers')
            context: Context for value generation (region, industry, etc.)
            use_cache: Whether to use cached values
        """
        cache_key = f"dynamic:{value_type}:{hash(str(context))}"
        
        # Try cache first
        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached:
                return cached
                
        # Try primary API source
        try:
            value = await self._fetch_from_primary_source(value_type, context)
            if value:
                await self._store_in_cache(cache_key, value)
                return value
        except Exception as e:
            logger.warning(f"Primary source failed for {value_type}: {e}")
            
        # Try secondary sources
        for source_name in self.config['api_integration'].get('secondary_sources', []):
            try:
                value = await self._fetch_from_source(source_name, value_type, context)
                if value:
                    await self._store_in_cache(cache_key, value, ttl=3600)  # Shorter TTL for fallback
                    return value
            except Exception as e:
                logger.warning(f"Secondary source {source_name} failed: {e}")
        
        # Emergency fallback to ML prediction or conservative defaults
        return await self._get_emergency_fallback(value_type, context)
    
    async def _fetch_from_primary_source(self, value_type: str, context: Dict[str, Any]) -> Any:
        """Fetch from primary API source based on value type"""
        if value_type == "budget_thresholds":
            response = await self.api_clients['google_ads'].get_budget_thresholds(
                region=context.get('region', 'global'),
                industry=context.get('industry', 'general')
            )
            return self._process_budget_thresholds(response)
            
        elif value_type == "industry_multipliers":
            response = await self.api_clients['google_ads'].get_industry_multipliers(
                industries=context.get('industries', [])
            )
            return self._process_industry_multipliers(response)
            
        elif value_type == "channel_performance":
            response = await self.api_clients['google_ads'].get_channel_performance(
                channels=context.get('channels', ['search_advertising'])
            )
            return self._process_channel_performance(response)
            
        return None
    
    def _process_budget_thresholds(self, response: APIResponse) -> Dict[str, float]:
        """Process API response into budget threshold structure"""
        # Transform API data into our expected format
        raw_data = response.data
        
        return {
            'micro_threshold': raw_data.get('micro_business_spending_median', 500),
            'small_threshold': raw_data.get('small_business_spending_median', 5000),
            'medium_threshold': raw_data.get('medium_business_spending_median', 50000),
            'large_threshold': raw_data.get('large_business_spending_median', 500000),
            'enterprise_threshold': raw_data.get('enterprise_spending_median', 2000000)
        }
    
    def _process_industry_multipliers(self, response: APIResponse) -> Dict[str, float]:
        """Process API response into industry multiplier structure"""
        raw_data = response.data
        
        return {
            'technology': raw_data.get('technology_performance_multiplier', 1.2),
            'healthcare': raw_data.get('healthcare_performance_multiplier', 1.1),
            'finance': raw_data.get('finance_performance_multiplier', 1.3),
            'manufacturing': raw_data.get('manufacturing_performance_multiplier', 1.0),
            'retail': raw_data.get('retail_performance_multiplier', 1.1),
            'services': raw_data.get('services_performance_multiplier', 1.0)
        }
    
    def _process_channel_performance(self, response: APIResponse) -> Dict[str, Any]:
        """Process API response into channel performance metrics"""
        raw_data = response.data
        
        return {
            'search_advertising': {
                'ctr_range': (
                    raw_data.get('search_ctr_p25', 0.02),
                    raw_data.get('search_ctr_p75', 0.08)
                ),
                'cpc_range': (
                    raw_data.get('search_cpc_p25', 1.5),
                    raw_data.get('search_cpc_p75', 8.0)
                ),
                'conversion_rate_range': (
                    raw_data.get('search_cvr_p25', 0.02),
                    raw_data.get('search_cvr_p75', 0.12)
                ),
                'competitive_intensity': raw_data.get('search_competition_index', 0.75)
            }
        }
    
    async def _get_emergency_fallback(self, value_type: str, context: Dict[str, Any]) -> Any:
        """Emergency fallback values when all APIs fail"""
        fallback_values = {
            'budget_thresholds': {
                'micro_threshold': 500,
                'small_threshold': 5000, 
                'medium_threshold': 50000,
                'large_threshold': 500000,
                'enterprise_threshold': 2000000
            },
            'industry_multipliers': {
                'technology': 1.2,
                'healthcare': 1.1,
                'finance': 1.3,
                'manufacturing': 1.0,
                'retail': 1.1,
                'services': 1.0
            },
            'channel_performance': {
                'search_advertising': {
                    'ctr_range': (0.02, 0.08),
                    'cpc_range': (1.5, 8.0), 
                    'conversion_rate_range': (0.02, 0.12),
                    'competitive_intensity': 0.75
                }
            }
        }
        
        logger.error(f"Using emergency fallback for {value_type}")
        return fallback_values.get(value_type, {})
    
    async def start_background_updates(self):
        """Start background tasks for proactive cache updates"""
        update_configs = self.config.get('dynamic_values', {})
        
        for value_type, config in update_configs.items():
            frequency = self._parse_duration(config['update_frequency'])
            task = asyncio.create_task(
                self._background_update_loop(value_type, frequency)
            )
            self._background_tasks.add(task)
    
    async def _background_update_loop(self, value_type: str, frequency: timedelta):
        """Background loop for proactive value updates"""
        while True:
            try:
                # Update common contexts proactively
                common_contexts = self._get_common_contexts(value_type)
                
                for context in common_contexts:
                    await self.get_dynamic_value(
                        value_type=value_type,
                        context=context,
                        use_cache=False  # Force fresh fetch
                    )
                    
                await asyncio.sleep(frequency.total_seconds())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background update failed for {value_type}: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
```

---

## 📊 MONITORING & OBSERVABILITY

### 1. Performance Monitoring
```python
# config/monitoring.py
from dataclasses import dataclass
from typing import Dict, List
import time
from datetime import datetime
import logging

@dataclass
class PerformanceMetrics:
    api_response_times: Dict[str, List[float]]
    cache_hit_rates: Dict[str, float]
    fallback_usage: Dict[str, int]
    error_rates: Dict[str, float]
    
class DynamicConfigMonitor:
    def __init__(self):
        self.metrics = PerformanceMetrics(
            api_response_times={},
            cache_hit_rates={},
            fallback_usage={},
            error_rates={}
        )
    
    def track_api_call(self, source: str, duration: float, success: bool):
        """Track API call performance"""
        if source not in self.metrics.api_response_times:
            self.metrics.api_response_times[source] = []
            
        self.metrics.api_response_times[source].append(duration)
        
        # Keep only last 100 measurements
        if len(self.metrics.api_response_times[source]) > 100:
            self.metrics.api_response_times[source].pop(0)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health"""
        health = {}
        
        for source, times in self.metrics.api_response_times.items():
            if times:
                avg_time = sum(times) / len(times)
                health[f"{source}_avg_response"] = avg_time
                health[f"{source}_status"] = "healthy" if avg_time < 1.0 else "degraded"
                
        return health
```

---

## 🚀 INTEGRATION POINTS

### 1. Modified Parser Integration
```python
# In dynamic_ai_parser.py - replace hardcoded values
class UltraDynamicGoalParser:
    def __init__(self, config_manager: DynamicConfigManager):
        self.config_manager = config_manager
        # Remove all hardcoded dictionaries
        
    async def _get_dynamic_budget_thresholds(self, industry: str, region: str) -> Dict[str, float]:
        """Get budget thresholds from dynamic config"""
        context = {'industry': industry, 'region': region}
        return await self.config_manager.get_dynamic_value('budget_thresholds', context)
    
    async def _get_dynamic_industry_multipliers(self) -> Dict[str, float]:
        """Get industry multipliers from dynamic config"""
        return await self.config_manager.get_dynamic_value('industry_multipliers')
```

### 2. Modified Generator Integration  
```python
# In ai_generator.py - replace hardcoded values
class UltraDynamicCampaignGenerator:
    def __init__(self, config_manager: DynamicConfigManager):
        self.config_manager = config_manager
        
    async def _get_dynamic_channel_performance(self, channels: List[str]) -> Dict[str, Any]:
        """Get channel performance from dynamic config"""
        context = {'channels': channels}
        return await self.config_manager.get_dynamic_value('channel_performance', context)
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### 1. Intelligent Caching Strategy
- **L1 Cache**: In-memory (100ms response)
- **L2 Cache**: Redis distributed cache (10ms response)  
- **L3 Cache**: Database persistent cache (50ms response)

### 2. Async Optimization
- All API calls are async/await
- Concurrent fetching for multiple values
- Background preloading of common values

### 3. Circuit Breaker Pattern
- Automatic fallback when APIs are down
- Gradual recovery testing
- Health check integration

---

## 🔄 DEPLOYMENT STRATEGY

### Phase 1: Configuration Infrastructure (Day 2)
1. Deploy Redis cache layer
2. Set up API client configurations  
3. Implement basic dynamic config manager

### Phase 2: Value Migration (Day 3-5)
1. Replace critical business values first
2. Implement fallback systems
3. Add monitoring and alerts

### Phase 3: Full Dynamic System (Day 6-8)
1. Complete all hardcoded value replacements
2. Optimize performance and caching
3. Add comprehensive monitoring

---

**Status**: ✅ Configuration architecture designed | 🔄 Ready for API integration setup

**Next**: Day 1 Hour 5-6 - External API integration planning and authentication setup
