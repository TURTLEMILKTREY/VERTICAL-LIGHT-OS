"""
LOCAL BUSINESS INTELLIGENCE ENGINE
Purpose: Help individual business owners make practical decisions with limited budget
Target: SMEs with ₹5,000-15,000 monthly marketing budget
"""

class LocalBusinessAssistant:
    """
    Simplified intelligence engine for individual business owners
    Focus: Practical advice, not complex analytics
    """
    
    def __init__(self):
        self.local_data_sources = {
            'google_my_business': True,  # Free API
            'social_media_insights': True,  # Free APIs
            'government_msme_data': True,  # Free government data
            'local_directories': True  # Free/cheap sources
        }
    
    def get_simple_advice(self, business_type: str, location: str, 
                         budget: int, specific_question: str) -> dict:
        """
        Give practical advice for specific business questions
        
        Examples:
        - "Should I expand to online sales?"
        - "Is Instagram marketing worth it for my restaurant?"
        - "Should I hire a delivery person?"
        """
        
        # Use free/cheap data sources only
        local_context = self._get_local_business_context(location, business_type)
        budget_reality = self._assess_budget_options(budget)
        
        if "online" in specific_question.lower():
            return self._online_expansion_advice(business_type, location, budget, local_context)
        elif "marketing" in specific_question.lower():
            return self._marketing_channel_advice(business_type, budget, local_context)
        elif "expand" in specific_question.lower():
            return self._expansion_advice(business_type, location, budget, local_context)
        else:
            return self._general_business_advice(business_type, location, budget)
    
    def _online_expansion_advice(self, business_type: str, location: str, 
                               budget: int, local_context: dict) -> dict:
        """
        Simple yes/no advice on going online
        """
        
        # Use real local data (Google My Business, local competitor analysis)
        online_readiness_score = 0
        
        # Factor 1: Local digital adoption
        if local_context.get('smartphone_penetration', 0) > 0.6:
            online_readiness_score += 30
        
        # Factor 2: Business type suitability
        online_suitable_businesses = [
            'restaurant', 'bakery', 'grocery', 'clothing', 'electronics', 
            'books', 'pharmacy', 'beauty_salon'
        ]
        if any(biz in business_type.lower() for biz in online_suitable_businesses):
            online_readiness_score += 25
        
        # Factor 3: Budget adequacy  
        if budget >= 5000:  # Minimum for basic online setup
            online_readiness_score += 20
        
        # Factor 4: Local competition online presence
        competitors_online = local_context.get('competitors_with_online_presence', 0)
        if competitors_online < 0.5:  # Less than 50% competitors online = opportunity
            online_readiness_score += 25
        
        # Simple recommendation
        if online_readiness_score >= 70:
            return {
                'recommendation': 'YES - Go Online',
                'confidence': f"{online_readiness_score}%",
                'reason': self._get_online_expansion_reason(online_readiness_score),
                'next_steps': [
                    f"1. Set up WhatsApp Business (Free)",
                    f"2. Create Google My Business profile (Free)", 
                    f"3. Budget ₹{min(budget//2, 3000)} for delivery platform registration",
                    f"4. Start with {self._recommend_platform(business_type)}"
                ],
                'expected_timeline': '2-4 weeks to see results',
                'investment_needed': f"₹{self._calculate_online_investment(budget)}",
                'risk_level': 'LOW - Start small, scale gradually'
            }
        else:
            return {
                'recommendation': 'NOT YET - Focus on local first',
                'confidence': f"{100-online_readiness_score}%",
                'reason': self._get_wait_reason(online_readiness_score),
                'alternative_steps': [
                    "1. Strengthen local customer base first",
                    "2. Improve product/service quality", 
                    "3. Build word-of-mouth reputation",
                    "4. Save ₹10,000+ for proper online launch"
                ],
                'revisit_when': 'After 3 months of local growth'
            }
    
    def _marketing_channel_advice(self, business_type: str, budget: int, 
                                local_context: dict) -> dict:
        """
        Recommend specific marketing channels for the budget
        """
        
        channels = []
        remaining_budget = budget
        
        # Priority 1: Google My Business (Free but time investment)
        if remaining_budget >= 1000:  # For professional photos
            channels.append({
                'channel': 'Google My Business',
                'budget': 1000,
                'reason': 'Free visibility when people search locally',
                'expected_result': '20-30% more walk-in customers',
                'time_needed': '2 hours setup + 15 min daily updates'
            })
            remaining_budget -= 1000
        
        # Priority 2: WhatsApp Business
        if remaining_budget >= 2000:
            channels.append({
                'channel': 'WhatsApp Business Marketing',
                'budget': 2000,
                'reason': 'Direct communication with customers',
                'expected_result': '15-25% repeat customer rate',
                'time_needed': '30 min daily customer replies'
            })
            remaining_budget -= 2000
        
        # Priority 3: Local Facebook Groups/Instagram
        if remaining_budget >= 3000:
            channels.append({
                'channel': 'Social Media (Facebook/Instagram)',
                'budget': 3000,
                'reason': 'Build community and showcase products',
                'expected_result': '10-15% new customers monthly',
                'time_needed': '1 hour daily content creation'
            })
            remaining_budget -= 3000
        
        # Priority 4: Paid ads (only if budget allows)
        if remaining_budget >= 5000:
            channels.append({
                'channel': 'Google Ads (Local)',
                'budget': remaining_budget,
                'reason': 'Immediate visibility for high-intent searches',
                'expected_result': '5-10 new customers per week',
                'time_needed': '2 hours weekly campaign management'
            })
        
        return {
            'recommended_channels': channels,
            'total_budget_used': budget - remaining_budget,
            'expected_combined_result': f"{len(channels) * 15}% increase in customers within 2 months",
            'priority_order': 'Start with Google My Business, then add others monthly',
            'warning': 'Track results monthly - stop channels that don\'t work'
        }
    
    def _get_local_business_context(self, location: str, business_type: str) -> dict:
        """
        Gather local intelligence from free sources
        """
        
        # This would integrate with free APIs:
        # - Google My Business API (free)
        # - Government MSME data (free)
        # - Social media insights (free tier)
        # - Local directory data (free)
        
        return {
            'smartphone_penetration': 0.75,  # From government digital India data
            'competitors_with_online_presence': 0.4,  # From Google My Business search
            'local_delivery_services': ['Swiggy', 'Zomato', 'Dunzo'],  # Known platforms
            'peak_business_hours': '6-9 PM',  # From local Google trends
            'seasonal_patterns': {'diwali': 'high', 'monsoon': 'low'}  # Local knowledge base
        }

# Example usage for a real business:
assistant = LocalBusinessAssistant()

# Small bakery owner in Pune with ₹8,000 budget
advice = assistant.get_simple_advice(
    business_type="bakery",
    location="Pune, Maharashtra", 
    budget=8000,
    specific_question="Should I start online delivery?"
)

print("Advice for bakery owner:")
print(f"Recommendation: {advice['recommendation']}")
print(f"Next steps: {advice['next_steps']}")
print(f"Investment needed: {advice['investment_needed']}")
"""