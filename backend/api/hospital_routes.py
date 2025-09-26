#!/usr/bin/env python3
"""
Hospital Intelligence API Endpoints
FastAPI endpoints for AI-powered hospital consulting services

Provides RESTful API access to:
- Hospital performance analysis
- McKinsey-style consulting recommendations 
- Consulting proposal generation
- Benchmark comparisons
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
from datetime import datetime

# Import hospital intelligence engine and models
from services.hospital_intelligence_engine import HospitalIntelligenceEngine
from models.hospital_schemas_simple import (
 HospitalProfile, HospitalAnalysisRequest, HospitalAnalysisResponse,
 ConsultingProposal, ServiceTier, ConsultingFocus
)

logger = logging.getLogger(__name__)

# Create API router for hospital endpoints
hospital_router = APIRouter(prefix="/api/v1/hospital", tags=["Hospital Intelligence"])

# Global engine instance (in production, consider dependency injection)
_hospital_engine: Optional[HospitalIntelligenceEngine] = None

def get_hospital_engine() -> HospitalIntelligenceEngine:
 """Get or create hospital intelligence engine instance"""
 global _hospital_engine
 if _hospital_engine is None:
 _hospital_engine = HospitalIntelligenceEngine()
 logger.info("Hospital Intelligence Engine initialized")
 return _hospital_engine

@hospital_router.post("/analyze", response_model=HospitalAnalysisResponse)
async def analyze_hospital_performance(
 request: HospitalAnalysisRequest,
 engine: HospitalIntelligenceEngine = Depends(get_hospital_engine)
) -> HospitalAnalysisResponse:
 """
 Comprehensive hospital performance analysis

 Analyzes hospital across financial, operational, and quality dimensions
 Returns McKinsey-style recommendations and improvement opportunities
 """
 try:
 logger.info(f"Starting analysis for hospital: {request.hospital_profile.name}")

 # Validate input
 if not request.hospital_profile.hospital_id:
 raise HTTPException(status_code=400, detail="Hospital ID is required")

 if not request.analysis_scope:
 # Default to all focus areas if none specified
 request.analysis_scope = [
 ConsultingFocus.FINANCIAL_OPTIMIZATION,
 ConsultingFocus.OPERATIONAL_EFFICIENCY,
 ConsultingFocus.QUALITY_IMPROVEMENT
 ]

 # Run analysis
 analysis_response = await engine.analyze_hospital_performance(request)

 logger.info(f"Analysis completed for {request.hospital_profile.name}")
 return analysis_response

 except Exception as e:
 logger.error(f"Error in hospital analysis: {e}")
 raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@hospital_router.post("/proposal", response_model=ConsultingProposal)
async def generate_consulting_proposal(
 hospital_profile: HospitalProfile,
 analysis_response: HospitalAnalysisResponse,
 service_tier: ServiceTier = ServiceTier.STANDARD,
 engine: HospitalIntelligenceEngine = Depends(get_hospital_engine)
) -> ConsultingProposal:
 """
 Generate McKinsey-style consulting proposal

 Creates comprehensive proposal based on hospital analysis
 Includes investment, timeline, ROI, and deliverables
 """
 try:
 logger.info(f"Generating proposal for {hospital_profile.name}")

 proposal = await engine.generate_consulting_proposal(
 hospital_profile=hospital_profile,
 analysis_response=analysis_response,
 desired_service_tier=service_tier
 )

 logger.info(f"Proposal generated: {proposal.proposal_id}")
 return proposal

 except Exception as e:
 logger.error(f"Error generating proposal: {e}")
 raise HTTPException(status_code=500, detail=f"Proposal generation failed: {str(e)}")

@hospital_router.post("/quick-analysis")
async def quick_hospital_analysis(
 hospital_profile: HospitalProfile,
 focus_areas: Optional[List[ConsultingFocus]] = None,
 engine: HospitalIntelligenceEngine = Depends(get_hospital_engine)
):
 """
 Quick hospital analysis endpoint

 Simplified endpoint that takes just hospital profile
 Returns analysis and proposal in single response
 """
 try:
 # Set default focus areas if not provided
 if not focus_areas:
 focus_areas = [
 ConsultingFocus.FINANCIAL_OPTIMIZATION,
 ConsultingFocus.OPERATIONAL_EFFICIENCY,
 ConsultingFocus.QUALITY_IMPROVEMENT
 ]

 # Create analysis request
 analysis_request = HospitalAnalysisRequest(
 hospital_profile=hospital_profile,
 analysis_scope=focus_areas,
 requested_deliverables=[
 "Executive Summary",
 "Performance Benchmarking",
 "Strategic Recommendations"
 ]
 )

 # Run analysis
 analysis_response = await engine.analyze_hospital_performance(analysis_request)

 # Generate proposal
 proposal = await engine.generate_consulting_proposal(
 hospital_profile=hospital_profile,
 analysis_response=analysis_response,
 desired_service_tier=ServiceTier.STANDARD
 )

 # Return combined response
 return {
 "analysis": analysis_response,
 "proposal": proposal,
 "summary": {
 "hospital_name": hospital_profile.name,
 "analysis_date": datetime.now().isoformat(),
 "opportunities_count": len(analysis_response.opportunities),
 "total_impact": sum(opp.potential_annual_impact for opp in analysis_response.opportunities),
 "recommendations_count": len(analysis_response.recommendations),
 "proposal_investment": proposal.total_investment,
 "expected_roi": proposal.expected_roi,
 "payback_months": proposal.payback_period_months
 }
 }

 except Exception as e:
 logger.error(f"Error in quick analysis: {e}")
 raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

@hospital_router.get("/health")
async def health_check():
 """Health check endpoint for hospital intelligence service"""
 try:
 engine = get_hospital_engine()
 return {
 "status": "healthy",
 "service": "Hospital Intelligence Engine",
 "timestamp": datetime.now().isoformat(),
 "version": "1.0.0",
 "engine_initialized": engine is not None
 }
 except Exception as e:
 raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@hospital_router.get("/service-tiers")
async def get_service_tiers():
 """Get available consulting service tiers and their descriptions"""
 return {
 "service_tiers": {
 ServiceTier.BASIC: {
 "name": "Basic Diagnostic",
 "description": "Focused assessment with quick-win recommendations",
 "duration_months": "3-4",
 "ideal_for": "Small hospitals seeking specific improvements",
 "base_rate_per_bed": 2000 # INR
 },
 ServiceTier.STANDARD: {
 "name": "Comprehensive Consulting", 
 "description": "Full analysis with implementation support",
 "duration_months": "6-9",
 "ideal_for": "Mid-size hospitals with multiple improvement areas",
 "base_rate_per_bed": 3500 # INR
 },
 ServiceTier.PREMIUM: {
 "name": "Transformation Partnership",
 "description": "End-to-end transformation with change management",
 "duration_months": "9-15",
 "ideal_for": "Large hospitals seeking comprehensive transformation",
 "base_rate_per_bed": 6000 # INR
 },
 ServiceTier.ENTERPRISE: {
 "name": "Strategic Partnership",
 "description": "Long-term strategic partnership with capability building",
 "duration_months": "12-18",
 "ideal_for": "Hospital chains and large healthcare systems",
 "base_rate_per_bed": 10000 # INR
 }
 },
 "focus_areas": {
 ConsultingFocus.FINANCIAL_OPTIMIZATION: "Revenue cycle, cost management, profitability",
 ConsultingFocus.OPERATIONAL_EFFICIENCY: "Bed utilization, OR efficiency, workflow optimization",
 ConsultingFocus.QUALITY_IMPROVEMENT: "Patient satisfaction, clinical outcomes, safety",
 ConsultingFocus.TECHNOLOGY_OPTIMIZATION: "EMR optimization, automation, digital health",
 ConsultingFocus.REGULATORY_COMPLIANCE: "NABH, JCI, government schemes compliance",
 ConsultingFocus.STRATEGIC_PLANNING: "Growth strategy, market expansion, partnerships"
 }
 }

@hospital_router.get("/benchmarks/{hospital_type}/{city_tier}")
async def get_benchmark_data(
 hospital_type: str,
 city_tier: str,
 bed_count_range: Optional[str] = None
):
 """
 Get benchmark data for similar hospitals

 Provides industry benchmarks for hospital performance comparison
 """
 try:
 # This would typically query a benchmark database
 # For now, return simulated benchmark data

 benchmark_data = {
 "hospital_type": hospital_type,
 "city_tier": city_tier,
 "bed_count_range": bed_count_range or "100-300",
 "peer_count": 45,
 "benchmarks": {
 "financial": {
 "median_operating_margin": 0.12,
 "median_days_in_ar": 38,
 "median_collection_rate": 0.87
 },
 "operational": {
 "median_occupancy_rate": 0.78,
 "median_alos": 3.8,
 "median_or_utilization": 0.72
 },
 "quality": {
 "median_satisfaction_score": 82.5,
 "median_infection_rate": 0.025,
 "median_readmission_rate": 0.09
 }
 },
 "percentile_thresholds": {
 "top_quartile": 75,
 "median": 50,
 "bottom_quartile": 25
 }
 }

 return benchmark_data

 except Exception as e:
 logger.error(f"Error fetching benchmark data: {e}")
 raise HTTPException(status_code=500, detail=f"Benchmark data fetch failed: {str(e)}")

# Include the router in your main FastAPI app
# app.include_router(hospital_router)