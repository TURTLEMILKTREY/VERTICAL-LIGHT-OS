from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import uuid

from models.schemas import (
    BusinessGoal, GoalParseResponse, Campaign, CampaignCreate, 
    Lead, Analytics
)
from services.goal_parser.dynamic_ai_parser import AIGoalParser
from services.campaign_generator.ai_generator import AICampaignGenerator

router = APIRouter(prefix="/api", tags=["api"])

# Mock data for development
mock_campaigns: List[Campaign] = []
mock_leads: List[Lead] = []

# Initialize AI services
ai_goal_parser = AIGoalParser()
ai_campaign_generator = AICampaignGenerator()

@router.post("/parse-goal", response_model=GoalParseResponse)
async def parse_goal(goal_data: BusinessGoal):
    """Parse business goal using AI and return marketing strategy"""
    try:
        # Use AI parser to analyze the goal
        parsed_goal = ai_goal_parser.parse_goal(
            goal_text=goal_data.goal,
            business_type=goal_data.business_type,
            target_audience=goal_data.target_audience,
            budget=goal_data.budget,
            timeline=goal_data.timeline
        )
        
        # Generate strategy recommendations
        strategy_recommendations = ai_goal_parser.generate_strategy_recommendations(parsed_goal)
        
        # Create comprehensive response
        primary_strategy = strategy_recommendations
        
        return GoalParseResponse(
            parsed_goal=f"{parsed_goal['primary_intent'].replace('_', ' ').title()}: {goal_data.goal}",
            strategy=f"AI-recommended strategy focusing on {parsed_goal['primary_intent'].replace('_', ' ')}",
            recommended_channels=primary_strategy["channels"],
            estimated_cost=goal_data.budget * 0.8,  # 80% of budget for ads
            success_metrics=parsed_goal.get("measurable_outcomes", []),
            confidence_score=parsed_goal.get("confidence_score", 0.7),
            complexity_score=parsed_goal.get("complexity_index", 0.5),
            urgency_level="medium",  # Default urgency level
            risk_factors=parsed_goal.get("risk_factors", []),
            optimization_opportunities=strategy_recommendations.get("optimization_opportunities", [])
        )
        
    except Exception:
        # Fallback to simple parsing
        strategy = f"Strategic approach for {goal_data.business_type} targeting {goal_data.target_audience}"
        
        channels = ["Google Ads", "Facebook Ads", "Email Marketing"]
        if goal_data.budget > 5000:
            channels.extend(["LinkedIn Ads", "Content Marketing"])
        
        return GoalParseResponse(
            parsed_goal=goal_data.goal,
            strategy=strategy,
            recommended_channels=channels,
            estimated_cost=goal_data.budget * 0.8,
            success_metrics=["Click-through rate", "Conversion rate", "Cost per acquisition", "Return on ad spend"]
        )

@router.get("/campaigns", response_model=List[Campaign])
async def get_campaigns():
    """Get all campaigns"""
    return mock_campaigns

@router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign_data: CampaignCreate):
    """Create a new campaign"""
    now = datetime.now()
    campaign = Campaign(
        id=str(uuid.uuid4()),
        name=campaign_data.name,
        status="active",
        goal=campaign_data.goal,
        budget=campaign_data.budget,
        created_at=now,
        updated_at=now
    )
    mock_campaigns.append(campaign)
    return campaign

@router.post("/campaigns/ai-generate")
async def generate_ai_campaign(goal_data: BusinessGoal) -> Dict[str, Any]:
    """Generate an AI-powered marketing campaign"""
    try:
        # Generate comprehensive AI campaign
        ai_campaign = ai_campaign_generator.generate_campaign(
            goal_text=goal_data.goal,
            business_type=goal_data.business_type,
            target_audience=goal_data.target_audience,
            budget=goal_data.budget,
            timeline=goal_data.timeline
        )
        
        # Create campaign object for storage
        now = datetime.now()
        campaign = Campaign(
            id=ai_campaign["id"],
            name=ai_campaign["name"],
            status=ai_campaign["status"],
            goal=ai_campaign["objective"],
            budget=ai_campaign["budget"],
            created_at=now,
            updated_at=now
        )
        mock_campaigns.append(campaign)
        
        # Return full AI campaign details
        return {
            "campaign": campaign,
            "ai_details": ai_campaign,
            "message": "AI-powered campaign generated successfully"
        }
        
    except Exception:
        # Fallback to simple campaign creation
        fallback_campaign = await create_campaign(CampaignCreate(
            name=f"AI Campaign - {goal_data.business_type}",
            goal=goal_data.goal,
            budget=goal_data.budget,
            target_audience=goal_data.target_audience,
            channels=["Google Ads", "Facebook Ads"]
        ))
        
        return {
            "campaign": fallback_campaign,
            "ai_details": {"analysis": "fallback_mode", "confidence": 0.5},
            "message": "Campaign created with basic configuration"
        }

@router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Get a specific campaign"""
    campaign = next((c for c in mock_campaigns if c.id == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.get("/leads", response_model=List[Lead])
async def get_leads():
    """Get all leads"""
    return mock_leads

@router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    """Get a specific lead"""
    lead = next((l for l in mock_leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.get("/analytics", response_model=Analytics)
async def get_analytics():
    """Get analytics dashboard data"""
    active_campaigns = [c for c in mock_campaigns if c.status == "active"]
    total_spend = sum(c.spend or 0 for c in mock_campaigns)
    total_revenue = total_spend * 1.5  # Mock 150% return
    
    return Analytics(
        total_campaigns=len(mock_campaigns),
        active_campaigns=len(active_campaigns),
        total_leads=len(mock_leads),
        conversion_rate=2.5,  # Mock 2.5% conversion rate
        total_spend=total_spend,
        total_revenue=total_revenue,
        roi=(total_revenue - total_spend) / max(total_spend, 1) * 100,
        top_performing_campaigns=mock_campaigns[:3]  # Top 3 campaigns
    )
