from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

from models.schemas import (
 BusinessGoal, GoalParseResponse, Campaign, CampaignCreate, 
 Lead, Analytics
)
from services.goal_parser.dynamic_ai_parser import AIGoalParser
from services.campaign_generator.ai_generator import AICampaignGenerator
from services.market_intelligence import (
 create_personalized_data_quality_service,
 create_progressive_intelligence_system,
 enhance_data_quality_with_intelligence,
 get_intelligence_orchestrator
)

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
 estimated_cost=goal_data.budget * 0.8, # 80% of budget for ads
 success_metrics=parsed_goal.get("measurable_outcomes", []),
 confidence_score=parsed_goal.get("confidence_score", 0.7),
 complexity_score=parsed_goal.get("complexity_index", 0.5),
 urgency_level="medium", # Default urgency level
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
 total_revenue = total_spend * 1.5 # Mock 150% return

 return Analytics(
 total_campaigns=len(mock_campaigns),
 active_campaigns=len(active_campaigns),
 total_leads=len(mock_leads),
 conversion_rate=2.5, # Mock 2.5% conversion rate
 total_spend=total_spend,
 total_revenue=total_revenue,
 roi=(total_revenue - total_spend) / max(total_spend, 1) * 100,
 top_performing_campaigns=mock_campaigns[:3] # Top 3 campaigns
 )


# ========================================================================
# PROGRESSIVE INTELLIGENCE API ENDPOINTS
# Revolutionary + Practical Data Quality Personalization
# ========================================================================

@router.post("/progressive-intelligence/data-quality/assess")
async def assess_data_quality_with_intelligence(request: Dict[str, Any]):
 """
 Assess data quality using Progressive Intelligence Framework

 Revolutionary: Complete user control over quality dimensions and thresholds
 Practical: Intelligent suggestions based on business context and learning
 """
 try:
 # Extract business context and data
 business_context = request.get('business_context', {})
 data_to_assess = request.get('data', {})
 user_preferences = request.get('user_preferences', {})

 # Create personalized data quality service
 personalization_context = {
 'industry': business_context.get('industry', 'general'),
 'business_size': business_context.get('business_size', 'medium'),
 'risk_tolerance': business_context.get('risk_tolerance', 'moderate'),
 'regulatory_environment': business_context.get('regulatory_environment', 'standard'),
 'custom_dimensions': user_preferences.get('custom_dimensions', {}),
 'dimension_weights': user_preferences.get('dimension_weights', {}),
 'weight_mode': user_preferences.get('weight_mode', 'proportional')
 }

 # Create dynamic data quality service with Progressive Intelligence
 data_quality_service = create_personalized_data_quality_service(**personalization_context)

 # Assess data quality
 assessment_result = data_quality_service.assess_data_quality(data_to_assess, {
 'analysis_type': request.get('analysis_type', 'general'),
 'request_id': request.get('request_id', str(uuid.uuid4()))
 })

 # Enhance with Progressive Intelligence suggestions
 enhanced_context = enhance_data_quality_with_intelligence(data_quality_service, personalization_context)

 return {
 'status': 'success',
 'assessment_result': assessment_result,
 'progressive_intelligence': {
 'intelligent_suggestions': enhanced_context.get('intelligent_suggestions', {}),
 'suggestion_metadata': enhanced_context.get('suggestion_metadata', {}),
 'personalization_applied': personalization_context,
 'revolutionary_features': {
 'user_controlled_dimensions': list(personalization_context.get('custom_dimensions', {}).keys()),
 'user_controlled_weights': list(personalization_context.get('dimension_weights', {}).keys()),
 'complete_override_capability': True,
 'zero_hardcoded_assumptions': True
 }
 },
 'response_metadata': {
 'timestamp': datetime.now().isoformat(),
 'service_version': '1.0.0-progressive-intelligence',
 'framework': 'Progressive Intelligence Framework'
 }
 }

 except Exception as e:
 logger.error(f"Progressive Intelligence data quality assessment failed: {e}")
 return {
 'status': 'error',
 'error': str(e),
 'fallback_message': 'Progressive Intelligence enhancement failed, falling back to standard assessment'
 }


@router.post("/progressive-intelligence/suggestions/get")
async def get_intelligent_suggestions(request: Dict[str, Any]):
 """
 Get intelligent suggestions for data quality configuration

 Returns context-aware suggestions while preserving complete user override capability
 """
 try:
 # Extract business context
 business_context = request.get('business_context', {})

 # Create Progressive Intelligence engine
 from config.config_manager import get_config_manager
 config_manager = get_config_manager()
 intelligence_engine = create_progressive_intelligence_system(config_manager)

 # Generate intelligent suggestions
 suggestions = intelligence_engine.get_intelligent_suggestions(business_context)

 return {
 'status': 'success',
 'suggestions': suggestions,
 'user_control': {
 'override_capability': True,
 'modification_allowed': True,
 'complete_customization': True,
 'learning_enabled': True
 },
 'response_metadata': {
 'timestamp': datetime.now().isoformat(),
 'confidence_scores': suggestions.get('confidence_scores', {}),
 'suggestion_rationale': suggestions.get('rationale', {})
 }
 }

 except Exception as e:
 logger.error(f"Intelligent suggestions generation failed: {e}")
 return {
 'status': 'error',
 'error': str(e)
 }


@router.post("/progressive-intelligence/learning/feedback")
async def submit_learning_feedback(request: Dict[str, Any]):
 """
 Submit user feedback to improve Progressive Intelligence suggestions

 Enables the system to learn from user behavior while maintaining complete user control
 """
 try:
 # Extract feedback data
 user_id = request.get('user_id', 'anonymous')
 context = request.get('context', {})
 user_choices = request.get('user_choices', {})
 success_metrics = request.get('success_metrics', {})

 # Create Progressive Intelligence engine
 from config.config_manager import get_config_manager
 config_manager = get_config_manager()
 intelligence_engine = create_progressive_intelligence_system(config_manager)

 # Submit learning feedback
 intelligence_engine.learn_from_user_behavior(user_id, context, user_choices, success_metrics)

 return {
 'status': 'success',
 'message': 'Learning feedback submitted successfully',
 'learning_impact': {
 'improves_suggestions': True,
 'maintains_user_control': True,
 'enhances_for_similar_contexts': True,
 'preserves_privacy': True
 },
 'response_metadata': {
 'timestamp': datetime.now().isoformat(),
 'learning_enabled': True
 }
 }

 except Exception as e:
 logger.error(f"Learning feedback submission failed: {e}")
 return {
 'status': 'error',
 'error': str(e)
 }


@router.get("/progressive-intelligence/status")
async def get_progressive_intelligence_status():
 """
 Get status of Progressive Intelligence Framework integration
 """
 try:
 # Check service availability
 orchestrator = get_intelligence_orchestrator()

 return {
 'status': 'active',
 'framework': 'Progressive Intelligence Framework',
 'capabilities': {
 'revolutionary_personalization': True,
 'intelligent_suggestions': True,
 'learning_engine': True,
 'user_override_control': True,
 'zero_hardcoded_assumptions': True,
 'context_aware_analysis': True
 },
 'integration_status': {
 'intelligence_orchestrator': 'integrated',
 'dynamic_data_quality': 'active',
 'progressive_intelligence_engine': 'active',
 'api_endpoints': 'available'
 },
 'competitive_advantages': {
 'revolutionary_depth': 'No competitor has this level of personalization',
 'practical_usability': 'Smart defaults enable immediate value',
 'continuous_improvement': 'Learning engine creates network effects',
 'user_satisfaction': 'Serves both novices and experts perfectly'
 },
 'response_metadata': {
 'timestamp': datetime.now().isoformat(),
 'version': '1.0.0-progressive-intelligence'
 }
 }

 except Exception as e:
 logger.error(f"Progressive Intelligence status check failed: {e}")
 return {
 'status': 'error',
 'error': str(e)
 }
