from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class BusinessGoal(BaseModel):
    goal: str
    business_type: str
    target_audience: str
    budget: float
    timeline: str

class GoalParseResponse(BaseModel):
    parsed_goal: str
    strategy: str
    recommended_channels: List[str]
    estimated_cost: float
    success_metrics: List[str]
    # AI-enhanced fields
    confidence_score: Optional[float] = None
    complexity_score: Optional[float] = None
    urgency_level: Optional[str] = None
    risk_factors: Optional[List[str]] = None
    optimization_opportunities: Optional[List[str]] = None

class Campaign(BaseModel):
    id: str
    name: str
    status: str
    goal: str
    budget: float
    spend: Optional[float] = 0.0
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0
    conversions: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

class CampaignCreate(BaseModel):
    name: str
    goal: str
    budget: float
    target_audience: str
    channels: List[str]

class Lead(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    score: float
    status: str
    source: str
    created_at: datetime

class Analytics(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_leads: int
    conversion_rate: float
    total_spend: float
    total_revenue: float
    roi: float
    top_performing_campaigns: List[Campaign]
