"""
Local Intelligence Engine
Simplified intelligence system focused on hyperlocal insights for small businesses
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.local_business import LocalBusiness, LocalCompetitor, LocalCustomer, BudgetTier, BusinessCategory

logger = logging.getLogger(__name__)

@dataclass
class LocalInsight:
    """Single actionable insight for local business"""
    title: str
    description: str
    action_required: str
    priority: str  # high, medium, low
    estimated_impact: str
    estimated_effort: str
    cost: float = 0.0
    timeline: str = "immediate"

@dataclass
class LocalRecommendation:
    """Budget-aware recommendation"""
    action: str
    reason: str
    cost: float
    expected_roi: float
    timeline: str
    difficulty: str  # easy, medium, hard
    automation_possible: bool = True

class LocalIntelligenceEngine:
    """
    Simplified intelligence engine for local businesses
    Focus: Actionable insights within budget constraints
    """
    
    def __init__(self, business: LocalBusiness):
        self.business = business
        self.insights_cache = {}
        self.last_analysis = None
        
    async def get_daily_insights(self) -> Dict[str, Any]:
        """Get today's actionable insights"""
        logger.info(f"Generating daily insights for {self.business.name}")
        
        # Check cache (refresh daily)
        cache_key = f"daily_insights_{datetime.now().date()}"
        if cache_key in self.insights_cache:
            return self.insights_cache[cache_key]
        
        insights = {
            "local_market": await self._analyze_local_market(),
            "customer_behavior": await self._analyze_customer_patterns(),
            "opportunities": await self._identify_opportunities(),
            "budget_optimization": await self._optimize_budget_allocation(),
            "immediate_actions": await self._get_immediate_actions(),
            "automation_recommendations": await self._get_automation_recommendations()
        }
        
        # Cache results
        self.insights_cache[cache_key] = insights
        self.last_analysis = datetime.now()
        
        return insights
    
    async def _analyze_local_market(self) -> Dict[str, Any]:
        """Analyze local market within service radius"""
        logger.info("Analyzing local market")
        
        # Simulate local competitor analysis (in real implementation, use Google Places API)
        competitors = await self._get_local_competitors()
        
        analysis = {
            "total_competitors": len(competitors),
            "average_rating": sum(c.google_rating or 4.0 for c in competitors) / max(len(competitors), 1),
            "market_saturation": self._calculate_market_saturation(competitors),
            "price_positioning": self._analyze_price_positioning(competitors),
            "competitive_gaps": self._identify_competitive_gaps(competitors),
            "market_trends": await self._get_local_market_trends()
        }
        
        return analysis
    
    async def _get_local_competitors(self) -> List[LocalCompetitor]:
        """Get competitors within service radius"""
        # In real implementation, use Google Places API
        # For now, simulate based on business category
        
        category_competitors = {
            BusinessCategory.RESTAURANT: [
                LocalCompetitor("Local Dhaba", BusinessCategory.RESTAURANT, 1.2, 4.2, 85, price_range="budget"),
                LocalCompetitor("Pizza Corner", BusinessCategory.RESTAURANT, 0.8, 3.9, 45, price_range="moderate"),
                LocalCompetitor("Fine Dine Restaurant", BusinessCategory.RESTAURANT, 2.1, 4.5, 120, price_range="premium")
            ],
            BusinessCategory.SALON: [
                LocalCompetitor("Beauty Palace", BusinessCategory.SALON, 0.5, 4.1, 95, price_range="moderate"),
                LocalCompetitor("Quick Cuts", BusinessCategory.SALON, 1.8, 3.7, 30, price_range="budget"),
                LocalCompetitor("Luxury Salon", BusinessCategory.SALON, 3.2, 4.6, 150, price_range="premium")
            ],
            BusinessCategory.RETAIL: [
                LocalCompetitor("Local Store", BusinessCategory.RETAIL, 0.3, 3.8, 25, price_range="budget"),
                LocalCompetitor("Brand Outlet", BusinessCategory.RETAIL, 1.5, 4.0, 75, price_range="moderate"),
                LocalCompetitor("Premium Store", BusinessCategory.RETAIL, 2.8, 4.4, 110, price_range="premium")
            ]
        }
        
        return category_competitors.get(self.business.category, [])
    
    def _calculate_market_saturation(self, competitors: List[LocalCompetitor]) -> str:
        """Calculate market saturation level"""
        competitor_density = len(competitors) / (self.business.service_radius_km ** 2)
        
        if competitor_density < 0.5:
            return "low"
        elif competitor_density < 1.5:
            return "moderate"  
        else:
            return "high"
    
    def _analyze_price_positioning(self, competitors: List[LocalCompetitor]) -> Dict[str, Any]:
        """Analyze price positioning vs competitors"""
        budget_count = sum(1 for c in competitors if c.price_range == "budget")
        moderate_count = sum(1 for c in competitors if c.price_range == "moderate")
        premium_count = sum(1 for c in competitors if c.price_range == "premium")
        
        return {
            "budget_competitors": budget_count,
            "moderate_competitors": moderate_count,
            "premium_competitors": premium_count,
            "recommended_positioning": self._get_optimal_price_positioning(budget_count, moderate_count, premium_count)
        }
    
    def _get_optimal_price_positioning(self, budget: int, moderate: int, premium: int) -> str:
        """Recommend optimal price positioning"""
        total = budget + moderate + premium
        if total == 0:
            return "moderate"
        
        budget_pct = budget / total
        moderate_pct = moderate / total
        premium_pct = premium / total
        
        # Recommend less saturated segment
        if budget_pct < 0.3:
            return "budget"
        elif premium_pct < 0.2:
            return "premium"
        else:
            return "moderate"
    
    def _identify_competitive_gaps(self, competitors: List[LocalCompetitor]) -> List[str]:
        """Identify gaps in competitive landscape"""
        gaps = []
        
        # Check rating gaps
        low_rated = [c for c in competitors if (c.google_rating or 0) < 4.0]
        if len(low_rated) > len(competitors) * 0.5:
            gaps.append("service_quality")
        
        # Check review count gaps  
        low_reviews = [c for c in competitors if (c.google_review_count or 0) < 50]
        if len(low_reviews) > len(competitors) * 0.4:
            gaps.append("customer_engagement")
        
        # Category-specific gaps
        if self.business.category == BusinessCategory.RESTAURANT:
            gaps.extend(["online_ordering", "delivery_optimization", "social_media_presence"])
        elif self.business.category == BusinessCategory.SALON:
            gaps.extend(["online_booking", "before_after_content", "customer_loyalty"])
        elif self.business.category == BusinessCategory.RETAIL:
            gaps.extend(["e_commerce", "inventory_updates", "customer_reviews"])
        
        return gaps[:3]  # Top 3 gaps
    
    async def _get_local_market_trends(self) -> Dict[str, Any]:
        """Get local market trends (simulate Google Trends data)"""
        # In real implementation, integrate with Google Trends API
        
        category_trends = {
            BusinessCategory.RESTAURANT: {
                "growing": ["home_delivery", "healthy_food", "online_ordering"],
                "declining": ["dine_in_only", "cash_only"],
                "seasonal": ["ice_cream_summer", "hot_food_winter"]
            },
            BusinessCategory.SALON: {
                "growing": ["bridal_makeup", "hair_treatments", "male_grooming"],
                "declining": ["basic_cuts_only"],
                "seasonal": ["wedding_season", "festival_makeup"]
            },
            BusinessCategory.RETAIL: {
                "growing": ["online_shopping", "contactless_payment", "home_delivery"],
                "declining": ["cash_transactions"],
                "seasonal": ["festival_shopping", "back_to_school"]
            }
        }
        
        return category_trends.get(self.business.category, {"growing": [], "declining": [], "seasonal": []})
    
    async def _analyze_customer_patterns(self) -> Dict[str, Any]:
        """Analyze local customer behavior patterns"""
        logger.info("Analyzing customer patterns")
        
        # Simulate customer insights based on business category and location
        patterns = {
            "peak_hours": self._get_peak_hours(),
            "preferred_communication": self._get_communication_preferences(),
            "price_sensitivity": self._analyze_price_sensitivity(),
            "loyalty_factors": self._get_loyalty_factors(),
            "seasonal_patterns": self._get_seasonal_patterns()
        }
        
        return patterns
    
    def _get_peak_hours(self) -> Dict:
        """Get peak business hours for category"""
        category_peaks = {
            BusinessCategory.RESTAURANT: {
                "breakfast": "08:00-10:00",
                "lunch": "12:00-14:00", 
                "dinner": "19:00-21:00",
                "weekend_evening": "18:00-22:00"
            },
            BusinessCategory.SALON: {
                "morning": "10:00-12:00",
                "afternoon": "14:00-17:00",
                "weekend": "09:00-18:00"
            },
            BusinessCategory.RETAIL: {
                "morning": "10:00-12:00",
                "evening": "17:00-20:00",
                "weekend": "11:00-21:00"
            }
        }
        
        return category_peaks.get(self.business.category, {})
    
    def _get_communication_preferences(self) -> Dict:
        """Get customer communication preferences"""
        return {
            "primary": "whatsapp",
            "secondary": "phone",
            "preferred_language": self.business.primary_language,
            "response_time_expectation": "within_2_hours"
        }
    
    def _analyze_price_sensitivity(self) -> str:
        """Analyze local price sensitivity"""
        # Base on budget tier and location
        if self.business.budget_tier == BudgetTier.BOOTSTRAP:
            return "high"
        elif self.business.budget_tier == BudgetTier.GROWTH:
            return "moderate"
        else:
            return "low"
    
    def _get_loyalty_factors(self) -> List[str]:
        """Get factors that drive customer loyalty for this business type"""
        category_loyalty = {
            BusinessCategory.RESTAURANT: ["food_quality", "service_speed", "value_for_money", "hygiene"],
            BusinessCategory.SALON: ["service_quality", "stylist_skill", "ambiance", "punctuality"],
            BusinessCategory.RETAIL: ["product_quality", "pricing", "variety", "customer_service"],
            BusinessCategory.PHARMACY: ["medicine_availability", "expert_advice", "home_delivery"],
            BusinessCategory.FITNESS: ["trainer_quality", "equipment", "cleanliness", "flexible_timings"]
        }
        
        return category_loyalty.get(self.business.category, ["service_quality", "value_for_money", "customer_service"])
    
    def _get_seasonal_patterns(self) -> Dict:
        """Get seasonal business patterns"""
        current_month = datetime.now().month
        
        # General patterns + category-specific
        patterns = {
            "current_season": self._get_current_season(current_month),
            "peak_months": self._get_peak_months(),
            "slow_months": self._get_slow_months(),
            "upcoming_opportunities": self._get_upcoming_seasonal_opportunities(current_month)
        }
        
        return patterns
    
    def _get_current_season(self, month: int) -> str:
        """Get current season"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8, 9]:
            return "monsoon"
        else:
            return "autumn"
    
    def _get_peak_months(self) -> List[str]:
        """Get peak business months for category"""
        category_peaks = {
            BusinessCategory.RESTAURANT: ["December", "January", "October", "November"],
            BusinessCategory.SALON: ["October", "November", "December", "February", "April"],
            BusinessCategory.RETAIL: ["October", "November", "December", "March", "April"],
            BusinessCategory.FITNESS: ["January", "February", "June", "July"]
        }
        
        return category_peaks.get(self.business.category, ["October", "November", "December"])
    
    def _get_slow_months(self) -> List[str]:
        """Get typically slow months"""
        return ["August", "September"]  # Generally slow due to monsoon
    
    def _get_upcoming_seasonal_opportunities(self, current_month: int) -> List[str]:
        """Get upcoming seasonal opportunities"""
        opportunities = []
        
        # Festival seasons
        if current_month in [8, 9]:
            opportunities.append("Festive season preparation")
        elif current_month in [10, 11]:
            opportunities.append("Wedding season marketing")
        elif current_month == 12:
            opportunities.append("New year promotions")
        elif current_month in [1, 2]:
            opportunities.append("Valentine's day campaigns")
        
        return opportunities
    
    async def _identify_opportunities(self) -> List[LocalInsight]:
        """Identify immediate growth opportunities"""
        logger.info("Identifying growth opportunities")
        
        opportunities = []
        
        # Google My Business optimization
        if not self.business.google_my_business_id:
            opportunities.append(LocalInsight(
                title="Set up Google My Business",
                description="73% of local searches result in store visits. Your business isn't on Google Maps yet.",
                action_required="Create and optimize Google My Business listing",
                priority="high",
                estimated_impact="30-40% increase in local visibility",
                estimated_effort="2 hours setup",
                cost=0.0,
                timeline="today"
            ))
        
        # Social media presence
        social_missing = []
        if not self.business.facebook_page_id:
            social_missing.append("Facebook")
        if not self.business.instagram_account_id:
            social_missing.append("Instagram")
        
        if social_missing:
            opportunities.append(LocalInsight(
                title=f"Create {' and '.join(social_missing)} presence",
                description=f"Missing {' and '.join(social_missing)} means missing 70% of local customers",
                action_required=f"Set up business profiles on {' and '.join(social_missing)}",
                priority="high",
                estimated_impact="25-35% increase in customer reach",
                estimated_effort="3 hours setup",
                cost=0.0,
                timeline="this_week"
            ))
        
        # WhatsApp Business
        if not self.business.whatsapp_number:
            opportunities.append(LocalInsight(
                title="Set up WhatsApp Business",
                description="89% of Indian customers prefer WhatsApp for business communication",
                action_required="Set up WhatsApp Business account with catalog and automated messages",
                priority="high",
                estimated_impact="40-50% improvement in customer communication",
                estimated_effort="1 hour setup",
                cost=0.0,
                timeline="today"
            ))
        
        # Budget-based opportunities
        daily_budget = self.business.get_daily_budget()
        
        if daily_budget >= 100:
            opportunities.append(LocalInsight(
                title="Start Google Ads for local search",
                description="Appear first when customers search for your services nearby",
                action_required="Create local search ad campaign",
                priority="medium",
                estimated_impact="20-30% increase in enquiries",
                estimated_effort="1 hour setup + ongoing optimization",
                cost=daily_budget * 0.7,  # 70% of daily budget
                timeline="this_week"
            ))
        
        if daily_budget >= 50:
            opportunities.append(LocalInsight(
                title="Facebook local audience ads",
                description="Target customers within your service area with special offers",
                action_required="Create Facebook ad campaign for local audience",
                priority="medium", 
                estimated_impact="15-25% increase in customer acquisition",
                estimated_effort="30 minutes setup + daily monitoring",
                cost=daily_budget * 0.3,  # 30% of daily budget
                timeline="this_week"
            ))
        
        # Category-specific opportunities
        category_opportunities = await self._get_category_opportunities()
        opportunities.extend(category_opportunities)
        
        # Sort by priority and impact
        priority_order = {"high": 3, "medium": 2, "low": 1}
        opportunities.sort(key=lambda x: priority_order[x.priority], reverse=True)
        
        return opportunities[:5]  # Top 5 opportunities
    
    async def _get_category_opportunities(self) -> List[LocalInsight]:
        """Get category-specific opportunities"""
        opportunities = []
        
        if self.business.category == BusinessCategory.RESTAURANT:
            opportunities.extend([
                LocalInsight(
                    title="Online food delivery integration",
                    description="Join Swiggy/Zomato to reach customers who order online",
                    action_required="Register on delivery platforms and optimize listings",
                    priority="medium",
                    estimated_impact="40-60% increase in orders",
                    estimated_effort="2 hours setup + ongoing management",
                    cost=0.0,  # Commission-based
                    timeline="this_week"
                ),
                LocalInsight(
                    title="Daily food photography",
                    description="Food photos get 3x more engagement on social media",
                    action_required="Take and post daily food photos with good lighting",
                    priority="medium",
                    estimated_impact="25-40% increase in social media reach",
                    estimated_effort="15 minutes daily",
                    cost=0.0,
                    timeline="daily"
                )
            ])
        
        elif self.business.category == BusinessCategory.SALON:
            opportunities.extend([
                LocalInsight(
                    title="Before/After transformation posts",
                    description="Transformation content gets 5x more shares than regular posts",
                    action_required="Take before/after photos (with permission) and post regularly",
                    priority="high",
                    estimated_impact="50-70% increase in social engagement",
                    estimated_effort="5 minutes per customer",
                    cost=0.0,
                    timeline="daily"
                ),
                LocalInsight(
                    title="Online appointment booking",
                    description="Allow customers to book appointments online 24/7",
                    action_required="Set up online booking system (free options available)",
                    priority="medium",
                    estimated_impact="30-45% increase in bookings",
                    estimated_effort="1 hour setup",
                    cost=0.0,
                    timeline="this_week"
                )
            ])
        
        elif self.business.category == BusinessCategory.RETAIL:
            opportunities.extend([
                LocalInsight(
                    title="Product catalog on WhatsApp",
                    description="Share product photos and prices instantly with customers",
                    action_required="Create WhatsApp Business catalog with your products",
                    priority="high",
                    estimated_impact="35-50% increase in inquiries",
                    estimated_effort="2 hours initial setup",
                    cost=0.0,
                    timeline="this_week"
                ),
                LocalInsight(
                    title="Customer review collection",
                    description="Display customer reviews to build trust and attract new buyers",
                    action_required="Ask satisfied customers for reviews and display them prominently",
                    priority="medium",
                    estimated_impact="20-30% increase in conversion",
                    estimated_effort="10 minutes per customer",
                    cost=0.0,
                    timeline="ongoing"
                )
            ])
        
        return opportunities
    
    async def _optimize_budget_allocation(self) -> Dict:
        """Optimize marketing budget allocation"""
        logger.info("Optimizing budget allocation")
        
        total_budget = self.business.monthly_marketing_budget
        
        if self.business.budget_tier == BudgetTier.BOOTSTRAP:
            allocation = {
                "organic_content": {"percentage": 70, "amount": total_budget * 0.7, "focus": "Daily social media posts, GMB optimization"},
                "google_ads": {"percentage": 20, "amount": total_budget * 0.2, "focus": "Local search ads"},
                "tools_software": {"percentage": 10, "amount": total_budget * 0.1, "focus": "Free tools, basic subscriptions"},
                "paid_promotion": {"percentage": 0, "amount": 0, "focus": "Focus on organic growth"}
            }
        elif self.business.budget_tier == BudgetTier.GROWTH:
            allocation = {
                "paid_advertising": {"percentage": 50, "amount": total_budget * 0.5, "focus": "Google + Facebook ads"},
                "content_creation": {"percentage": 25, "amount": total_budget * 0.25, "focus": "Professional content, photography"},
                "tools_software": {"percentage": 15, "amount": total_budget * 0.15, "focus": "Automation tools, analytics"},
                "promotions": {"percentage": 10, "amount": total_budget * 0.1, "focus": "Offers, contests, collaborations"}
            }
        else:  # SCALE
            allocation = {
                "paid_advertising": {"percentage": 60, "amount": total_budget * 0.6, "focus": "Multi-platform advertising"},
                "content_creation": {"percentage": 20, "amount": total_budget * 0.2, "focus": "Professional videos, photography"},
                "tools_software": {"percentage": 15, "amount": total_budget * 0.15, "focus": "Premium automation, CRM"},
                "partnerships": {"percentage": 5, "amount": total_budget * 0.05, "focus": "Influencer partnerships, collaborations"}
            }
        
        return {
            "budget_tier": self.business.budget_tier.value,
            "total_monthly_budget": total_budget,
            "recommended_allocation": allocation,
            "roi_expectation": self._calculate_expected_roi(allocation)
        }
    
    def _calculate_expected_roi(self, allocation: Dict) -> Dict:
        """Calculate expected ROI for budget allocation"""
        # Simplified ROI calculation based on industry averages
        base_roi = 200  # 200% ROI baseline
        
        # Adjust based on budget efficiency
        if self.business.budget_tier == BudgetTier.BOOTSTRAP:
            roi_multiplier = 1.5  # Higher ROI on organic methods
        elif self.business.budget_tier == BudgetTier.GROWTH:
            roi_multiplier = 1.2  # Balanced approach
        else:
            roi_multiplier = 1.0  # Standard ROI
        
        expected_roi = base_roi * roi_multiplier
        
        return {
            "expected_monthly_roi": f"{expected_roi}%",
            "break_even_timeline": "2-3 months",
            "confidence_level": "high" if self.business.budget_tier == BudgetTier.BOOTSTRAP else "medium"
        }
    
    async def _get_immediate_actions(self) -> List[LocalRecommendation]:
        """Get actions that can be done today"""
        logger.info("Getting immediate actions")
        
        actions = []
        
        # Free immediate actions
        free_actions = [
            LocalRecommendation(
                action="Optimize Google My Business listing",
                reason="Free visibility boost in local search results",
                cost=0.0,
                expected_roi=300.0,
                timeline="2 hours",
                difficulty="easy",
                automation_possible=False
            ),
            LocalRecommendation(
                action="Post daily content on social media",
                reason="Stay visible to your audience and attract new customers",
                cost=0.0,
                expected_roi=150.0,
                timeline="15 minutes daily",
                difficulty="easy",
                automation_possible=True
            ),
            LocalRecommendation(
                action="Ask satisfied customers for reviews",
                reason="Reviews influence 90% of purchase decisions",
                cost=0.0,
                expected_roi=250.0,
                timeline="5 minutes per customer",
                difficulty="easy",
                automation_possible=True
            )
        ]
        
        actions.extend(free_actions)
        
        # Budget-based actions
        daily_budget = self.business.get_daily_budget()
        
        if daily_budget >= 50:
            actions.append(LocalRecommendation(
                action="Start Facebook local ads",
                reason="Target customers within 5km radius with your offers",
                cost=daily_budget * 0.5,
                expected_roi=200.0,
                timeline="30 minutes setup",
                difficulty="medium",
                automation_possible=True
            ))
        
        if daily_budget >= 100:
            actions.append(LocalRecommendation(
                action="Launch Google search ads",
                reason="Appear first when locals search for your services",
                cost=daily_budget * 0.7,
                expected_roi=250.0,
                timeline="1 hour setup",
                difficulty="medium",
                automation_possible=True
            ))
        
        # Category-specific immediate actions
        if self.business.category == BusinessCategory.RESTAURANT:
            actions.append(LocalRecommendation(
                action="Upload today's menu photos",
                reason="Fresh food photos increase orders by 40%",
                cost=0.0,
                expected_roi=180.0,
                timeline="10 minutes",
                difficulty="easy",
                automation_possible=False
            ))
        
        # Sort by ROI and ease
        actions.sort(key=lambda x: (x.expected_roi, -x.cost), reverse=True)
        
        return actions[:5]
    
    async def _get_automation_recommendations(self) -> List[Dict]:
        """Get recommendations for automation based on business needs"""
        logger.info("Getting automation recommendations")
        
        automations = []
        
        # Social media automation
        automations.append({
            "type": "social_media_posting",
            "description": "Automatically post content at optimal times",
            "tasks_automated": ["daily_posts", "story_updates", "offer_announcements"],
            "time_saved": "2 hours/day",
            "setup_effort": "30 minutes",
            "monthly_cost": 0.0,  # Included in subscription
            "automation_percentage": 85
        })
        
        # Google My Business automation  
        automations.append({
            "type": "google_my_business",
            "description": "Auto-update business info, post updates, respond to reviews",
            "tasks_automated": ["business_posts", "review_responses", "info_updates"],
            "time_saved": "1 hour/day",
            "setup_effort": "15 minutes",
            "monthly_cost": 0.0,
            "automation_percentage": 80
        })
        
        # WhatsApp automation
        automations.append({
            "type": "whatsapp_customer_service",
            "description": "Auto-respond to common queries, send reminders",
            "tasks_automated": ["inquiry_responses", "appointment_reminders", "follow_ups"],
            "time_saved": "3 hours/day",
            "setup_effort": "45 minutes",
            "monthly_cost": 0.0,
            "automation_percentage": 70
        })
        
        # Category-specific automation
        if self.business.category == BusinessCategory.RESTAURANT:
            automations.append({
                "type": "delivery_platform_optimization",
                "description": "Auto-update menu prices and availability across platforms",
                "tasks_automated": ["menu_updates", "price_sync", "availability_status"],
                "time_saved": "45 minutes/day",
                "setup_effort": "1 hour",
                "monthly_cost": 0.0,
                "automation_percentage": 90
            })
        
        elif self.business.category == BusinessCategory.SALON:
            automations.append({
                "type": "appointment_management",
                "description": "Auto-confirm appointments, send reminders, handle rescheduling",
                "tasks_automated": ["booking_confirmation", "reminder_messages", "reschedule_handling"],
                "time_saved": "1.5 hours/day",
                "setup_effort": "45 minutes",
                "monthly_cost": 0.0,
                "automation_percentage": 85
            })
        
        # Calculate total impact
        total_time_saved = sum(float(auto["time_saved"].split()[0]) for auto in automations)
        total_automation = sum(auto["automation_percentage"] for auto in automations) / len(automations)
        
        return {
            "available_automations": automations,
            "total_time_saved_daily": f"{total_time_saved} hours",
            "overall_automation_percentage": f"{total_automation:.0f}%",
            "monthly_value": f"₹{total_time_saved * 30 * 500:,.0f}",  # ₹500/hour value
            "setup_timeline": "1-2 hours total"
        }
    
    async def get_weekly_performance_summary(self) -> Dict:
        """Generate weekly performance insights"""
        return {
            "growth_metrics": {
                "new_customers": "Estimated +12 customers this week",
                "revenue_impact": f"Estimated +₹{self.business.monthly_marketing_budget * 2:,.0f} additional revenue",
                "time_saved": "18 hours saved through automation"
            },
            "top_performing_actions": [
                "Google My Business posts (5x more views)",
                "WhatsApp customer service (95% response rate)",
                "Daily social media content (40% more engagement)"
            ],
            "areas_for_improvement": [
                "Increase Google review collection",
                "Expand content variety",
                "Optimize ad spend allocation"
            ],
            "next_week_focus": [
                "Launch customer referral program",
                "Create video content",
                "Analyze competitor pricing"
            ]
        }

# Utility functions
def create_local_intelligence_engine(business: LocalBusiness) -> LocalIntelligenceEngine:
    """Factory function to create local intelligence engine"""
    return LocalIntelligenceEngine(business)

async def get_quick_insights(business: LocalBusiness) -> Dict:
    """Get quick insights for a business (cached version)"""
    engine = LocalIntelligenceEngine(business)
    return await engine.get_daily_insights()