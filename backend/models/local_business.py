"""
Local Business Model
Simple, focused model for individual small businesses
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class BusinessCategory(Enum):
    """Common local business categories"""
    RESTAURANT = "restaurant"
    SALON = "salon" 
    RETAIL = "retail"
    PHARMACY = "pharmacy"
    GROCERY = "grocery"
    CLINIC = "clinic"
    MECHANIC = "mechanic"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FITNESS = "fitness"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    SERVICES = "services"
    OTHER = "other"

class BudgetTier(Enum):
    """Budget categories for local businesses"""
    BOOTSTRAP = "bootstrap"  # ₹5k or less
    GROWTH = "growth"       # ₹5k - ₹15k
    SCALE = "scale"         # ₹15k+

@dataclass
class LocalBusiness:
    """Simplified model for local businesses"""
    
    # Basic Business Info
    name: str
    category: BusinessCategory
    description: str = ""
    
    # Location & Service Area
    address: str = ""
    city: str = ""
    state: str = ""
    pincode: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    service_radius_km: float = 5.0  # Default 5km service radius
    
    # Budget & Pricing
    monthly_marketing_budget: float = 5000.0  # INR
    budget_tier: BudgetTier = BudgetTier.BOOTSTRAP
    average_order_value: Optional[float] = None
    
    # Business Hours
    operating_hours: Dict[str, str] = field(default_factory=lambda: {
        "monday": "09:00-18:00",
        "tuesday": "09:00-18:00", 
        "wednesday": "09:00-18:00",
        "thursday": "09:00-18:00",
        "friday": "09:00-18:00",
        "saturday": "09:00-18:00",
        "sunday": "closed"
    })
    
    # Contact Information
    phone: str = ""
    whatsapp_number: Optional[str] = None
    email: str = ""
    website: Optional[str] = None
    
    # Social Media Integration
    google_my_business_id: Optional[str] = None
    facebook_page_id: Optional[str] = None
    instagram_account_id: Optional[str] = None
    youtube_channel_id: Optional[str] = None
    
    # Current Performance Metrics
    monthly_revenue: Optional[float] = None
    monthly_customers: Optional[int] = None
    google_rating: Optional[float] = None
    google_review_count: Optional[int] = None
    
    # Target Audience
    target_customer_age_range: str = "25-45"
    target_customer_gender: str = "all"
    target_customer_income: str = "middle_class"
    primary_language: str = "hindi"
    secondary_language: str = "english"
    
    # Business Goals
    primary_goal: str = "increase_customers"
    monthly_growth_target: float = 20.0  # percentage
    
    # Automation Preferences
    preferred_posting_times: List[str] = field(default_factory=lambda: ["09:00", "14:00", "19:00"])
    content_themes: List[str] = field(default_factory=list)
    automation_level: str = "medium"  # low, medium, high
    
    # System Fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        """Set default values based on category"""
        self._set_category_defaults()
        self._determine_budget_tier()
    
    def _set_category_defaults(self):
        """Set category-specific defaults"""
        category_defaults = {
            BusinessCategory.RESTAURANT: {
                "content_themes": ["food_photos", "daily_specials", "customer_reviews", "behind_scenes"],
                "preferred_posting_times": ["08:00", "12:00", "19:00"],
                "target_customer_age_range": "20-50"
            },
            BusinessCategory.SALON: {
                "content_themes": ["before_after", "styling_tips", "product_features", "customer_transformations"],
                "preferred_posting_times": ["09:00", "15:00", "18:00"],
                "target_customer_age_range": "18-45"
            },
            BusinessCategory.RETAIL: {
                "content_themes": ["new_arrivals", "offers", "product_demos", "customer_testimonials"],
                "preferred_posting_times": ["10:00", "14:00", "17:00"],
                "target_customer_age_range": "25-55"
            },
            BusinessCategory.PHARMACY: {
                "content_themes": ["health_tips", "medicine_info", "offers", "wellness_advice"],
                "preferred_posting_times": ["08:00", "13:00", "20:00"],
                "target_customer_age_range": "30-65"
            },
            BusinessCategory.FITNESS: {
                "content_themes": ["workout_tips", "transformations", "nutrition_advice", "class_schedules"],
                "preferred_posting_times": ["06:00", "12:00", "18:00"],
                "target_customer_age_range": "18-40"
            }
        }
        
        if self.category in category_defaults:
            defaults = category_defaults[self.category]
            if not self.content_themes:
                self.content_themes = defaults.get("content_themes", [])
            if self.preferred_posting_times == ["09:00", "14:00", "19:00"]:
                self.preferred_posting_times = defaults.get("preferred_posting_times", self.preferred_posting_times)
            if self.target_customer_age_range == "25-45":
                self.target_customer_age_range = defaults.get("target_customer_age_range", "25-45")
    
    def _determine_budget_tier(self):
        """Determine budget tier based on monthly budget"""
        if self.monthly_marketing_budget <= 5000:
            self.budget_tier = BudgetTier.BOOTSTRAP
        elif self.monthly_marketing_budget <= 15000:
            self.budget_tier = BudgetTier.GROWTH
        else:
            self.budget_tier = BudgetTier.SCALE
    
    def get_service_area_bounds(self):
        """Get geographical bounds of service area"""
        if not (self.latitude and self.longitude):
            return None
            
        # Approximate km to degrees conversion
        km_to_lat = 1 / 111.0
        km_to_lng = 1 / (111.0 * abs(self.latitude / 90))
        
        return {
            "north": self.latitude + (self.service_radius_km * km_to_lat),
            "south": self.latitude - (self.service_radius_km * km_to_lat),
            "east": self.longitude + (self.service_radius_km * km_to_lng),
            "west": self.longitude - (self.service_radius_km * km_to_lng)
        }
    
    def is_within_budget(self, cost: float) -> bool:
        """Check if a cost fits within monthly budget"""
        return cost <= self.monthly_marketing_budget
    
    def get_daily_budget(self) -> float:
        """Get daily marketing budget"""
        return self.monthly_marketing_budget / 30
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "location": {
                "address": self.address,
                "city": self.city,
                "state": self.state,
                "pincode": self.pincode,
                "coordinates": {
                    "lat": self.latitude,
                    "lng": self.longitude
                } if self.latitude and self.longitude else None,
                "service_radius_km": self.service_radius_km
            },
            "budget": {
                "monthly_marketing_budget": self.monthly_marketing_budget,
                "budget_tier": self.budget_tier.value,
                "daily_budget": self.get_daily_budget()
            },
            "contact": {
                "phone": self.phone,
                "whatsapp": self.whatsapp_number,
                "email": self.email,
                "website": self.website
            },
            "social_media": {
                "google_my_business": self.google_my_business_id,
                "facebook": self.facebook_page_id,
                "instagram": self.instagram_account_id,
                "youtube": self.youtube_channel_id
            },
            "performance": {
                "monthly_revenue": self.monthly_revenue,
                "monthly_customers": self.monthly_customers,
                "google_rating": self.google_rating,
                "google_review_count": self.google_review_count
            },
            "automation": {
                "content_themes": self.content_themes,
                "preferred_posting_times": self.preferred_posting_times,
                "automation_level": self.automation_level
            },
            "goals": {
                "primary_goal": self.primary_goal,
                "monthly_growth_target": self.monthly_growth_target
            }
        }

@dataclass 
class LocalCompetitor:
    """Model for local competitor analysis"""
    name: str
    category: BusinessCategory
    distance_km: float
    google_rating: Optional[float] = None
    google_review_count: Optional[int] = None
    estimated_monthly_revenue: Optional[float] = None
    price_range: str = "moderate"  # budget, moderate, premium
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
@dataclass
class LocalCustomer:
    """Model for local customer insights"""
    age_group: str
    gender: str
    income_level: str
    preferred_language: str
    peak_activity_hours: List[str] = field(default_factory=list)
    common_search_terms: List[str] = field(default_factory=list)
    preferred_communication: str = "whatsapp"  # whatsapp, phone, email
    
# Factory functions for common business setups
def create_restaurant_business(name: str, location: str, budget: float = 10000) -> LocalBusiness:
    """Create a restaurant business with optimal defaults"""
    return LocalBusiness(
        name=name,
        category=BusinessCategory.RESTAURANT,
        address=location,
        monthly_marketing_budget=budget,
        content_themes=["food_photos", "daily_specials", "customer_reviews"],
        preferred_posting_times=["08:00", "12:00", "19:00"],
        primary_goal="increase_customers"
    )

def create_salon_business(name: str, location: str, budget: float = 8000) -> LocalBusiness:
    """Create a salon business with optimal defaults"""
    return LocalBusiness(
        name=name,
        category=BusinessCategory.SALON,
        address=location,
        monthly_marketing_budget=budget,
        content_themes=["before_after", "styling_tips", "offers"],
        preferred_posting_times=["09:00", "15:00", "18:00"],
        target_customer_gender="female",
        primary_goal="increase_bookings"
    )

def create_retail_business(name: str, location: str, budget: float = 6000) -> LocalBusiness:
    """Create a retail business with optimal defaults"""
    return LocalBusiness(
        name=name,
        category=BusinessCategory.RETAIL,
        address=location,
        monthly_marketing_budget=budget,
        content_themes=["new_arrivals", "offers", "product_demos"],
        preferred_posting_times=["10:00", "14:00", "17:00"],
        primary_goal="increase_sales"
    )