"""
Service Factory Pattern for Parallel Architecture
Routes requests to appropriate services based on business tier
Keeps enterprise and local services completely separate
"""

from typing import Union, Any, Optional, Dict
import logging
from .shared.tier_config import BusinessTier, TierConfigManager

logger = logging.getLogger(__name__)

class ServiceFactory:
 """
 Factory for creating appropriate services based on business tier
 Ensures enterprise and local services remain isolated
 """

 @staticmethod
 def create_intelligence_service(tier: BusinessTier, **kwargs) -> Any:
 """Create intelligence service based on business tier"""

 logger.info(f"Creating intelligence service for tier: {tier.value}")

 if tier == BusinessTier.ENTERPRISE:
 # Import existing enterprise service (NO CHANGES to existing code)
 try:
 from .market_intelligence.intelligence_engine import IntelligenceEngine
 logger.info("Loading existing enterprise IntelligenceEngine")
 return IntelligenceEngine(**kwargs)
 except ImportError as e:
 logger.error(f"Failed to import enterprise IntelligenceEngine: {e}")
 # Fallback to existing shared intelligence
 from .shared.intelligence import DynamicIntelligenceEngine
 return DynamicIntelligenceEngine(**kwargs)

 elif tier == BusinessTier.LOCAL:
 # Import new local service
 try:
 from .local.intelligence.local_intelligence_engine import LocalIntelligenceEngine
 logger.info("Loading new local business LocalIntelligenceEngine")
 return LocalIntelligenceEngine(**kwargs)
 except ImportError as e:
 logger.error(f"Failed to import LocalIntelligenceEngine: {e}")
 raise ImportError(f"Local intelligence service not available: {e}")

 else:
 raise ValueError(f"Unknown business tier: {tier}")

 @staticmethod 
 def create_automation_service(tier: BusinessTier, **kwargs) -> Any:
 """Create automation service based on business tier"""

 logger.info(f"Creating automation service for tier: {tier.value}")

 if tier == BusinessTier.ENTERPRISE:
 try:
 from .campaign_generator.campaign_generator import CampaignGenerator
 logger.info("Loading existing enterprise CampaignGenerator")
 return CampaignGenerator(**kwargs)
 except ImportError as e:
 logger.error(f"Failed to import enterprise CampaignGenerator: {e}")
 raise ImportError(f"Enterprise automation service not available: {e}")

 elif tier == BusinessTier.LOCAL:
 try:
 from .local.automation.automation_orchestrator import LocalAutomationOrchestrator
 logger.info("Loading new local business AutomationOrchestrator")
 return LocalAutomationOrchestrator(**kwargs)
 except ImportError as e:
 logger.error(f"Failed to import LocalAutomationOrchestrator: {e}")
 raise ImportError(f"Local automation service not available: {e}")

 else:
 raise ValueError(f"Unknown business tier: {tier}")

 @staticmethod
 def create_execution_service(tier: BusinessTier, **kwargs) -> Any:
 """Create execution service based on business tier"""

 logger.info(f"Creating execution service for tier: {tier.value}")

 if tier == BusinessTier.ENTERPRISE:
 # Enterprise execution (if exists)
 try:
 from .campaign_executor.campaign_executor import CampaignExecutor
 return CampaignExecutor(**kwargs)
 except ImportError:
 logger.warning("Enterprise execution service not found")
 return None

 elif tier == BusinessTier.LOCAL:
 try:
 from .local.execution.task_executor import LocalTaskExecutor
 return LocalTaskExecutor(**kwargs)
 except ImportError as e:
 logger.error(f"Failed to import LocalTaskExecutor: {e}")
 raise ImportError(f"Local execution service not available: {e}")

 else:
 raise ValueError(f"Unknown business tier: {tier}")

 @staticmethod
 def get_supported_features(tier: BusinessTier) -> dict:
 """Get supported features for business tier"""

 config = TierConfigManager.get_config(tier.value)
 if not config:
 return {}

 features = {
 BusinessTier.ENTERPRISE: {
 "intelligence": "comprehensive_analysis",
 "automation": "advanced_campaign_management", 
 "integrations": config.integrations,
 "analytics": "deep_business_insights",
 "customization": "full_white_labeling",
 "support": "dedicated_account_manager",
 "data_limits": "unlimited",
 "api_calls": "10,000/hour",
 "team_size": "up_to_50_members"
 },
 BusinessTier.LOCAL: {
 "intelligence": "hyperlocal_insights",
 "automation": "essential_task_automation",
 "integrations": config.integrations,
 "analytics": "actionable_business_metrics", 
 "customization": "template_based_branding",
 "support": "chat_and_community",
 "data_limits": "monthly_reports",
 "api_calls": "1,000/hour",
 "team_size": "up_to_3_members"
 }
 }

 return features.get(tier, {})

 @staticmethod
 def validate_tier_access(tier: BusinessTier, feature: str) -> bool:
 """Validate if tier has access to specific feature"""

 features = ServiceFactory.get_supported_features(tier)
 return feature in features

 @staticmethod
 def get_tier_from_budget(monthly_budget: float) -> BusinessTier:
 """Determine appropriate tier based on monthly budget"""

 if monthly_budget >= 25000:
 return BusinessTier.ENTERPRISE
 else:
 return BusinessTier.LOCAL

 @staticmethod
 def get_tier_comparison() -> Dict[str, Any]:
 """Get detailed comparison between tiers"""

 return {
 "enterprise": {
 "pricing": "₹25,000+/month",
 "target": "Large businesses, B2B companies, enterprises",
 "automation_level": "95% comprehensive automation",
 "intelligence": "Global market analysis, competitive intelligence",
 "support": "Dedicated account manager, 24/7 priority support",
 "customization": "Full white-labeling, custom integrations",
 "ideal_for": "Companies with complex marketing needs, multiple teams"
 },
 "local": {
 "pricing": "₹999/month",
 "target": "Small local businesses, individual entrepreneurs",
 "automation_level": "80% essential task automation", 
 "intelligence": "Hyperlocal market insights, budget-aware recommendations",
 "support": "Chat support, community forum, knowledge base",
 "customization": "Template-based branding, pre-built workflows",
 "ideal_for": "Restaurants, salons, retail stores, service providers"
 }
 }

 @staticmethod
 def create_service_suite(tier: BusinessTier, **kwargs) -> Dict[str, Any]:
 """Create complete service suite for a business tier"""

 logger.info(f"Creating complete service suite for tier: {tier.value}")

 suite = {
 "tier": tier.value,
 "config": TierConfigManager.get_config(tier.value),
 "services": {}
 }

 try:
 # Intelligence Service
 suite["services"]["intelligence"] = ServiceFactory.create_intelligence_service(tier, **kwargs)
 logger.info(f"Intelligence service created for {tier.value}")

 # Automation Service 
 suite["services"]["automation"] = ServiceFactory.create_automation_service(tier, **kwargs)
 logger.info(f"Automation service created for {tier.value}")

 # Execution Service (if available)
 execution_service = ServiceFactory.create_execution_service(tier, **kwargs)
 if execution_service:
 suite["services"]["execution"] = execution_service
 logger.info(f"Execution service created for {tier.value}")

 suite["status"] = "ready"
 suite["features"] = ServiceFactory.get_supported_features(tier)

 except Exception as e:
 logger.error(f"Failed to create service suite for {tier.value}: {e}")
 suite["status"] = "error"
 suite["error"] = str(e)

 return suite