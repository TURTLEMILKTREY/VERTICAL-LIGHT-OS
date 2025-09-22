"""
Standalone Tier Configuration for Parallel Architecture
Independent of existing enterprise services
"""

from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum

class BusinessTier(Enum):
    """Business service tiers"""
    ENTERPRISE = "enterprise"
    LOCAL = "local"

@dataclass
class TierConfiguration:
    """Configuration for specific business tier"""
    
    tier_name: str
    monthly_pricing: float
    feature_set: Dict[str, str]
    api_limits: Dict[str, int]
    integrations: List[str]
    support_level: str
    automation_level: str

# Enterprise Configuration (Maps to existing system)
ENTERPRISE_CONFIG = TierConfiguration(
    tier_name="enterprise",
    monthly_pricing=25000.0,  # Rs.25,000/month
    feature_set={
        "intelligence_depth": "comprehensive",
        "automation_complexity": "advanced",
        "customization_level": "full",
        "analytics_depth": "deep_insights",
        "multi_tenant": "enabled",
        "white_labeling": "available",
        "strategic_synthesis": "advanced",
        "market_intelligence": "global_comprehensive"
    },
    api_limits={
        "requests_per_hour": 10000,
        "data_export": "unlimited",
        "concurrent_campaigns": 100,
        "team_members": 50,
        "storage_gb": 1000
    },
    integrations=[
        "salesforce", "hubspot", "marketo", "pipedrive",
        "google_ads", "facebook_ads", "linkedin_ads",
        "zapier", "webhook_unlimited", "custom_api"
    ],
    support_level="dedicated_account_manager",
    automation_level="95% comprehensive automation"
)

# Local Business Configuration (New system)  
LOCAL_CONFIG = TierConfiguration(
    tier_name="local",
    monthly_pricing=999.0,  # Rs.999/month
    feature_set={
        "intelligence_depth": "actionable_insights",
        "automation_complexity": "essential_tasks",
        "customization_level": "template_based",
        "analytics_depth": "key_metrics",
        "multi_tenant": "single_business",
        "white_labeling": "not_available",
        "strategic_synthesis": "simplified",
        "market_intelligence": "hyperlocal_focused"
    },
    api_limits={
        "requests_per_hour": 1000,
        "data_export": "monthly_reports",
        "concurrent_campaigns": 5,
        "team_members": 3,
        "storage_gb": 10
    },
    integrations=[
        "whatsapp_business", "google_my_business",
        "facebook_pages", "instagram_business",
        "basic_webhooks", "simple_crm"
    ],
    support_level="chat_plus_community",
    automation_level="80% essential task automation"
)

class TierConfigManager:
    """Manages configuration for different business tiers"""
    
    configs = {
        "enterprise": ENTERPRISE_CONFIG,
        "local": LOCAL_CONFIG
    }
    
    @classmethod
    def get_config(cls, tier: str) -> TierConfiguration:
        """Get configuration for specified tier"""
        return cls.configs.get(tier.lower())
    
    @classmethod
    def validate_feature_access(cls, tier: str, feature: str) -> bool:
        """Check if tier has access to specific feature"""
        config = cls.get_config(tier)
        if not config:
            return False
        return feature in config.feature_set
    
    @classmethod
    def get_pricing_info(cls, tier: str) -> Dict[str, Any]:
        """Get pricing information for tier"""
        config = cls.get_config(tier)
        if not config:
            return {}
        
        return {
            "monthly_price": config.monthly_pricing,
            "currency": "INR",
            "automation_level": config.automation_level,
            "support_level": config.support_level,
            "features": list(config.feature_set.keys()),
            "integrations": config.integrations[:5]  # Top 5 integrations
        }
    
    @classmethod
    def get_all_tiers(cls) -> Dict[str, Dict[str, Any]]:
        """Get comparison of all tiers"""
        return {
            tier_name: {
                "pricing": config.monthly_pricing,
                "automation_level": config.automation_level,
                "target_market": "Large enterprises" if tier_name == "enterprise" else "Small local businesses",
                "key_features": list(config.feature_set.values())[:3]
            }
            for tier_name, config in cls.configs.items()
        }