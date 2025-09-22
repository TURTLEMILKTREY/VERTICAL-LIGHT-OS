"""
Social Media Automation Service
Automated posting, engagement, and content management for local businesses
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import random
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.local_business import LocalBusiness, BusinessCategory

logger = logging.getLogger(__name__)

@dataclass
class SocialMediaPost:
    """Social media post structure"""
    platform: str  # facebook, instagram, google_my_business
    content: str
    media_urls: List[str]
    hashtags: List[str]
    scheduled_time: datetime
    post_type: str  # photo, video, text, story
    target_audience: Optional[Dict[str, Any]] = None
    
@dataclass
class PostingResult:
    """Result of posting operation"""
    platform: str
    success: bool
    post_id: Optional[str] = None
    error_message: Optional[str] = None
    engagement_estimate: Optional[Dict[str, int]] = None

class SocialMediaAutomation:
    """
    Automated social media management for local businesses
    Handles content creation, scheduling, and engagement
    """
    
    def __init__(self, business: LocalBusiness):
        self.business = business
        self.content_templates = self._load_content_templates()
        self.posting_history = []
        
    async def generate_daily_content(self) -> List[SocialMediaPost]:
        """Generate content for today based on business category and schedule"""
        logger.info(f"Generating daily content for {self.business.name}")
        
        posts = []
        current_time = datetime.now()
        
        # Get optimal posting times for today
        posting_times = self._get_optimal_posting_times(current_time)
        
        for time_slot in posting_times:
            # Generate content for each time slot
            content_type = self._select_content_type(time_slot)
            post = await self._create_post(content_type, time_slot)
            if post:
                posts.append(post)
        
        return posts
    
    def _get_optimal_posting_times(self, date: datetime) -> List[datetime]:
        """Get optimal posting times for the business"""
        base_times = self.business.preferred_posting_times
        optimal_times = []
        
        for time_str in base_times:
            hour, minute = map(int, time_str.split(':'))
            post_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Skip past times
            if post_time > datetime.now():
                optimal_times.append(post_time)
        
        return optimal_times
    
    def _select_content_type(self, time_slot: datetime) -> str:
        """Select appropriate content type based on time and business"""
        hour = time_slot.hour
        
        if self.business.category == BusinessCategory.RESTAURANT:
            if 7 <= hour <= 9:
                return "breakfast_special"
            elif 11 <= hour <= 14:
                return "lunch_menu"
            elif 18 <= hour <= 21:
                return "dinner_special"
            else:
                return "general_food_content"
                
        elif self.business.category == BusinessCategory.SALON:
            if 9 <= hour <= 12:
                return "morning_services"
            elif 14 <= hour <= 17:
                return "transformation_showcase"
            else:
                return "styling_tips"
                
        elif self.business.category == BusinessCategory.RETAIL:
            if 10 <= hour <= 12:
                return "new_arrivals"
            elif 14 <= hour <= 17:
                return "product_showcase"
            elif 17 <= hour <= 20:
                return "special_offers"
            else:
                return "customer_testimonials"
        
        return "general_content"
    
    async def _create_post(self, content_type: str, scheduled_time: datetime) -> Optional[SocialMediaPost]:
        """Create a social media post"""
        try:
            template = self._get_content_template(content_type)
            if not template:
                return None
            
            # Generate personalized content
            content = self._personalize_content(template, content_type)
            hashtags = self._generate_hashtags(content_type)
            
            # Determine platforms to post on
            platforms = self._get_active_platforms()
            
            # Create post for primary platform (will be duplicated for others)
            primary_platform = platforms[0] if platforms else "facebook"
            
            post = SocialMediaPost(
                platform=primary_platform,
                content=content,
                media_urls=self._get_media_suggestions(content_type),
                hashtags=hashtags,
                scheduled_time=scheduled_time,
                post_type=self._get_post_type(content_type)
            )
            
            return post
            
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return None
    
    def _get_content_template(self, content_type: str) -> Optional[Dict[str, Any]]:
        """Get content template based on type"""
        category_templates = self.content_templates.get(self.business.category.value, {})
        return category_templates.get(content_type)
    
    def _personalize_content(self, template: Dict[str, Any], content_type: str) -> str:
        """Personalize content template with business information"""
        content = template.get('text', '')
        
        # Replace placeholders
        replacements = {
            '{business_name}': self.business.name,
            '{location}': self.business.city,
            '{phone}': self.business.phone,
            '{time}': self._get_contextual_time(),
            '{special_offer}': self._generate_offer_text(),
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content
    
    def _generate_hashtags(self, content_type: str) -> List[str]:
        """Generate relevant hashtags"""
        base_hashtags = [
            f"#{self.business.city.lower().replace(' ', '')}",
            f"#{self.business.category.value}",
            "#local",
            "#smallbusiness"
        ]
        
        category_hashtags = {
            BusinessCategory.RESTAURANT: ["#food", "#delicious", "#fresh", "#homemade", "#tasty"],
            BusinessCategory.SALON: ["#beauty", "#makeover", "#styling", "#haircare", "#skincare"],
            BusinessCategory.RETAIL: ["#shopping", "#quality", "#fashion", "#deals", "#newcollection"],
            BusinessCategory.FITNESS: ["#fitness", "#health", "#workout", "#strength", "#wellness"],
            BusinessCategory.PHARMACY: ["#health", "#medicine", "#wellness", "#care", "#pharmacy"]
        }
        
        specific_hashtags = category_hashtags.get(self.business.category, [])
        
        # Combine and limit to 10 hashtags
        all_hashtags = base_hashtags + random.sample(specific_hashtags, min(6, len(specific_hashtags)))
        
        return all_hashtags[:10]
    
    def _get_media_suggestions(self, content_type: str) -> List[str]:
        """Get media suggestions for the content type"""
        # In real implementation, this would integrate with business's photo library
        # For now, provide guidance on what photos to take
        
        media_suggestions = {
            "breakfast_special": ["Today's breakfast special photo", "Fresh ingredients photo"],
            "lunch_menu": ["Lunch dishes photo", "Customer enjoying meal"],
            "dinner_special": ["Evening special photo", "Restaurant ambiance"],
            "transformation_showcase": ["Before/after photos", "Styling process video"],
            "new_arrivals": ["New product photos", "Product arrangement"],
            "special_offers": ["Offer graphics", "Product with price tags"]
        }
        
        return media_suggestions.get(content_type, ["Business photo", "Product/service photo"])
    
    def _get_post_type(self, content_type: str) -> str:
        """Determine post type based on content"""
        video_content_types = ["transformation_showcase", "product_demo", "behind_scenes"]
        
        if content_type in video_content_types:
            return "video"
        else:
            return "photo"
    
    def _get_active_platforms(self) -> List[str]:
        """Get list of active social media platforms"""
        platforms = []
        
        if self.business.facebook_page_id:
            platforms.append("facebook")
        if self.business.instagram_account_id:
            platforms.append("instagram")
        if self.business.google_my_business_id:
            platforms.append("google_my_business")
            
        return platforms or ["facebook"]  # Default to Facebook if none configured
    
    def _get_contextual_time(self) -> str:
        """Get contextual time greeting"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "Good night"
    
    def _generate_offer_text(self) -> str:
        """Generate offer text based on budget and category"""
        if self.business.monthly_marketing_budget < 5000:
            offers = [
                "Special discount for our valued customers!",
                "Limited time offer - visit us today!",
                "Exclusive deal for local customers!"
            ]
        else:
            offers = [
                "20% off on all services today!",
                "Buy 2 Get 1 Free offer!",
                "Flat 15% discount on purchases above ₹1000!"
            ]
        
        return random.choice(offers)
    
    async def schedule_posts(self, posts: List[SocialMediaPost]) -> List[PostingResult]:
        """Schedule posts across platforms"""
        logger.info(f"Scheduling {len(posts)} posts")
        
        results = []
        
        for post in posts:
            platforms = self._get_active_platforms()
            
            for platform in platforms:
                try:
                    result = await self._post_to_platform(post, platform)
                    results.append(result)
                    
                    # Add delay between posts to avoid spam detection
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error posting to {platform}: {e}")
                    results.append(PostingResult(
                        platform=platform,
                        success=False,
                        error_message=str(e)
                    ))
        
        return results
    
    async def _post_to_platform(self, post: SocialMediaPost, platform: str) -> PostingResult:
        """Post to specific platform (simulated for now)"""
        # In real implementation, integrate with actual APIs
        
        logger.info(f"Posting to {platform}: {post.content[:50]}...")
        
        # Simulate API call delay
        await asyncio.sleep(1)
        
        # Simulate successful posting
        engagement_estimate = self._estimate_engagement(post, platform)
        
        return PostingResult(
            platform=platform,
            success=True,
            post_id=f"{platform}_{datetime.now().timestamp()}",
            engagement_estimate=engagement_estimate
        )
    
    def _estimate_engagement(self, post: SocialMediaPost, platform: str) -> Dict[str, int]:
        """Estimate engagement based on historical data and content quality"""
        base_engagement = {
            "facebook": {"likes": 15, "comments": 3, "shares": 2},
            "instagram": {"likes": 25, "comments": 5, "saves": 3},
            "google_my_business": {"views": 50, "clicks": 8, "calls": 2}
        }
        
        platform_base = base_engagement.get(platform, {"likes": 10, "comments": 2})
        
        # Adjust based on content quality factors
        multiplier = 1.0
        
        # Good hashtags boost engagement
        if len(post.hashtags) >= 8:
            multiplier += 0.3
        
        # Visual content performs better
        if post.post_type in ["photo", "video"]:
            multiplier += 0.4
        
        # Timing matters
        hour = post.scheduled_time.hour
        if (9 <= hour <= 11) or (17 <= hour <= 20):  # Peak hours
            multiplier += 0.5
        
        # Apply multiplier
        estimated = {}
        for metric, value in platform_base.items():
            estimated[metric] = int(value * multiplier)
        
        return estimated
    
    async def auto_engage_with_audience(self) -> Dict[str, Any]:
        """Automatically engage with audience (comments, messages)"""
        logger.info("Auto-engaging with audience")
        
        # Simulate engagement activities
        engagement_summary = {
            "comments_responded": 8,
            "messages_replied": 12,
            "new_followers": 3,
            "mentions_acknowledged": 5,
            "reviews_thanked": 2
        }
        
        # In real implementation:
        # - Respond to comments with appropriate replies
        # - Handle basic customer inquiries
        # - Thank customers for reviews
        # - Like and respond to mentions
        
        return {
            "success": True,
            "engagement_summary": engagement_summary,
            "automated_responses": [
                "Responded to 'What are your hours?' with business hours",
                "Thanked customer for 5-star review",
                "Provided location details to inquiry",
                "Acknowledged positive mention with thanks"
            ]
        }
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze social media performance"""
        logger.info("Analyzing social media performance")
        
        # Simulate performance analysis
        return {
            "weekly_summary": {
                "posts_published": 14,
                "total_reach": 1250,
                "total_engagement": 89,
                "new_followers": 8,
                "profile_visits": 45
            },
            "top_performing_posts": [
                {"content": "Today's special thali", "engagement": 25},
                {"content": "Customer transformation", "engagement": 22},
                {"content": "New arrivals showcase", "engagement": 18}
            ],
            "optimal_posting_times": ["09:00", "14:00", "19:00"],
            "audience_insights": {
                "age_group": "25-45 years",
                "gender": "60% Female, 40% Male",
                "location": f"85% from {self.business.city}",
                "peak_activity": "Evening 6-8 PM"
            },
            "recommendations": [
                "Post more transformation content - gets highest engagement",
                "Increase evening posts during 6-8 PM peak hours",
                "Use more local hashtags to reach nearby customers",
                "Add customer testimonials - builds trust"
            ]
        }
    
    def _load_content_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load content templates for different business categories"""
        return {
            "restaurant": {
                "breakfast_special": {
                    "text": "{time}! Start your day with our delicious breakfast special at {business_name}! 🌅\n\nFresh, hot, and made with love. Perfect for fuel before your busy day!\n\nCall {phone} to reserve your table! 📞",
                    "media_type": "photo",
                    "call_to_action": "Visit us today!"
                },
                "lunch_menu": {
                    "text": "Lunch time at {business_name}! 🍽️\n\nTry our today's special - made fresh with the finest ingredients. Perfect for your lunch break!\n\n{special_offer}\n\nLocated in {location}. Call {phone} for takeaway!",
                    "media_type": "photo",
                    "call_to_action": "Order now!"
                },
                "dinner_special": {
                    "text": "End your day with a perfect dinner at {business_name}! ✨\n\nOur chef's special tonight is something you don't want to miss. Cozy ambiance, great food, wonderful experience!\n\nBook your table: {phone}",
                    "media_type": "photo", 
                    "call_to_action": "Book now!"
                }
            },
            "salon": {
                "transformation_showcase": {
                    "text": "Amazing transformation at {business_name}! ✨💇‍♀️\n\nFrom everyday look to stunning style - our experts know how to bring out your best!\n\n{special_offer}\n\nBook your appointment: {phone}",
                    "media_type": "photo",
                    "call_to_action": "Book your makeover!"
                },
                "styling_tips": {
                    "text": "Pro tip from {business_name}! 💡\n\nDid you know? [Insert styling tip based on season/trend]\n\nFor personalized styling advice, visit us in {location} or call {phone}!",
                    "media_type": "photo",
                    "call_to_action": "Get expert advice!"
                }
            },
            "retail": {
                "new_arrivals": {
                    "text": "Fresh arrivals at {business_name}! 🛍️\n\nNew collection just in - trending styles, great quality, amazing prices!\n\n{special_offer}\n\nVisit our store in {location} or call {phone}!",
                    "media_type": "photo",
                    "call_to_action": "Shop now!"
                },
                "special_offers": {
                    "text": "Special offer at {business_name}! 🎉\n\n{special_offer}\n\nLimited time only! Don't miss out on these amazing deals.\n\nStore location: {location}\nCall: {phone}",
                    "media_type": "photo",
                    "call_to_action": "Visit today!"
                }
            }
        }

# Utility functions
async def create_daily_social_media_plan(business: LocalBusiness) -> Dict[str, Any]:
    """Create complete daily social media plan"""
    automation = SocialMediaAutomation(business)
    
    posts = await automation.generate_daily_content()
    results = await automation.schedule_posts(posts)
    engagement = await automation.auto_engage_with_audience()
    
    return {
        "posts_created": len(posts),
        "posts_scheduled": len([r for r in results if r.success]),
        "posting_results": results,
        "engagement_activity": engagement,
        "estimated_daily_reach": sum(post.engagement_estimate.get('views', 50) for post in posts if hasattr(post, 'engagement_estimate')),
        "time_saved": "2 hours",
        "next_optimization": "Analyze performance after 24 hours"
    }