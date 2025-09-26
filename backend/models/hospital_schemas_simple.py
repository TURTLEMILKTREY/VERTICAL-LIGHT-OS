#!/usr/bin/env python3
"""
Simplified Hospital Data Models for Indian Healthcare Consulting
Compatible with VERTICAL-LIGHT-OS and Pydantic v2

Focus on core functionality for hospital consulting AI system
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field
from decimal import Decimal

# Core Enums for Hospital Classification
class HospitalTier(str, Enum):
 TIER_1 = "tier_1" # Metro cities
 TIER_2 = "tier_2" # State capitals 
 TIER_3 = "tier_3" # District headquarters
 TIER_4 = "tier_4" # Rural areas

class HospitalType(str, Enum):
 ACUTE_CARE = "acute_care"
 SPECIALTY = "specialty"
 MULTI_SPECIALTY = "multi_specialty" # ← ADDED: Very common in India
 SUPER_SPECIALTY = "super_specialty"
 CRITICAL_ACCESS = "critical_access"
 TEACHING = "teaching"
 GOVERNMENT = "government"
 COMMUNITY = "community"

class ServiceTier(str, Enum):
 BASIC = "basic"
 STANDARD = "standard" 
 PREMIUM = "premium"
 ENTERPRISE = "enterprise"

class ConsultingFocus(str, Enum):
 FINANCIAL_OPTIMIZATION = "financial_optimization"
 OPERATIONAL_EFFICIENCY = "operational_efficiency"
 QUALITY_IMPROVEMENT = "quality_improvement"
 TECHNOLOGY_OPTIMIZATION = "technology_optimization"
 REGULATORY_COMPLIANCE = "regulatory_compliance"
 STRATEGIC_PLANNING = "strategic_planning"

# Core Data Models
class HospitalLocation(BaseModel):
 """Hospital location with Indian context"""
 address: str
 city: str
 state: str
 pincode: str
 tier: HospitalTier
 latitude: Optional[float] = None
 longitude: Optional[float] = None

class HospitalFinancialMetrics(BaseModel):
 """Core financial metrics for hospital performance"""
 annual_revenue: Decimal = Field(..., description="Annual revenue in INR")
 operating_margin: float = Field(..., description="Operating margin percentage")
 ebitda_margin: Optional[float] = None
 debt_to_equity: Optional[float] = None

 # Revenue cycle
 days_in_ar: Optional[int] = Field(None, description="Days in Accounts Receivable")
 collection_rate: Optional[float] = None

 # Payer mix for Indian market
 government_scheme_percentage: Optional[float] = None
 private_insurance_percentage: Optional[float] = None
 self_pay_percentage: Optional[float] = None

 fiscal_year: str = Field(..., description="e.g., FY2024-25")

class HospitalOperationalMetrics(BaseModel):
 """Key operational performance indicators"""
 bed_count: int = Field(..., description="Total bed count")
 occupancy_rate: float = Field(..., description="Bed occupancy rate 0-1")
 average_length_of_stay: float = Field(..., description="ALOS in days")

 # Emergency department
 ed_visits_annual: Optional[int] = None
 door_to_doc_time_minutes: Optional[float] = None

 # Operating rooms
 or_count: Optional[int] = None
 or_utilization_rate: Optional[float] = None

 # Staffing
 doctor_to_bed_ratio: Optional[float] = None
 nurse_to_bed_ratio: Optional[float] = None

 reporting_period: str

class HospitalQualityMetrics(BaseModel):
 """Quality and safety indicators"""
 hospital_acquired_infection_rate: Optional[float] = None
 medication_error_rate: Optional[float] = None
 mortality_rate: Optional[float] = None
 readmission_rate_30_day: Optional[float] = None

 # Patient satisfaction (0-100)
 overall_satisfaction_score: Optional[float] = None

 # Indian accreditation
 nabh_score: Optional[float] = None
 jci_accredited: Optional[bool] = None

 reporting_period: str

class HospitalStakeholder(BaseModel):
 """Key stakeholder in hospital consulting project"""
 name: str
 designation: str
 role_in_project: str
 contact_email: Optional[str] = None
 contact_phone: Optional[str] = None
 influence_level: str # high, medium, low
 support_level: str # champion, supporter, neutral, skeptical, blocker
 decision_authority: List[str] = Field(default_factory=list)

class HospitalProfile(BaseModel):
 """Core hospital profile for consulting assessment"""
 hospital_id: str = Field(..., description="Unique identifier")
 name: str
 location: HospitalLocation
 hospital_type: HospitalType

 # Basic info
 established_year: Optional[int] = None
 bed_count: int = Field(..., description="Total licensed beds")
 service_lines: List[str] = Field(default_factory=list)

 # Technology status
 has_emr: bool = Field(default=False, description="Electronic Medical Records")
 has_his: bool = Field(default=False, description="Hospital Information System")

 # Performance data
 financial_metrics: HospitalFinancialMetrics
 operational_metrics: HospitalOperationalMetrics
 quality_metrics: HospitalQualityMetrics

 # Consulting context
 current_challenges: List[str] = Field(default_factory=list)
 strategic_priorities: List[str] = Field(default_factory=list)
 key_stakeholders: List[HospitalStakeholder] = Field(default_factory=list)

 # Metadata
 profile_created_date: datetime = Field(default_factory=datetime.now)
 last_updated: datetime = Field(default_factory=datetime.now)

class ConsultingOpportunity(BaseModel):
 """Improvement opportunity identified during analysis"""
 opportunity_id: str
 category: ConsultingFocus
 title: str
 description: str

 # Impact assessment
 potential_annual_impact: Decimal = Field(..., description="Financial impact in INR")
 confidence_level: float = Field(..., description="Confidence 0-1")
 implementation_complexity: str # low, medium, high

 # Timeline and priority
 estimated_timeline_months: int = Field(..., description="Implementation timeline")
 priority_score: float = Field(..., description="Priority 0-1")

 created_date: datetime = Field(default_factory=datetime.now)

class ConsultingRecommendation(BaseModel):
 """Strategic recommendation following McKinsey SCQA structure"""
 recommendation_id: str
 title: str
 category: ConsultingFocus
 priority: str # critical, high, medium, low

 # SCQA Framework
 situation: str = Field(..., description="Current situation")
 complication: str = Field(..., description="Problems/challenges")
 question: str = Field(..., description="Key question")
 answer: str = Field(..., description="Recommended solution")

 # Implementation
 investment_required: Decimal
 expected_annual_benefit: Decimal
 payback_period_months: Optional[int] = None

 # Change management
 affected_stakeholders: List[str] = Field(default_factory=list)

 created_date: datetime = Field(default_factory=datetime.now)

class ConsultingProject(BaseModel):
 """Hospital consulting engagement project"""
 project_id: str
 hospital_profile: HospitalProfile
 service_tier: ServiceTier

 # Scope
 focus_areas: List[ConsultingFocus]
 specific_objectives: List[str] = Field(default_factory=list)

 # Timeline
 start_date: date
 end_date: date

 # Commercial
 total_investment: Decimal

 # Project tracking
 current_phase: str
 completion_percentage: float = Field(default=0.0, description="0-1")
 identified_opportunities: List[ConsultingOpportunity] = Field(default_factory=list)
 recommendations: List[ConsultingRecommendation] = Field(default_factory=list)

 # Status
 status: str = Field(default="planned") # planned, active, on_hold, completed, cancelled
 created_date: datetime = Field(default_factory=datetime.now)
 last_updated: datetime = Field(default_factory=datetime.now)

class HospitalBenchmarkData(BaseModel):
 """Benchmark comparison data"""
 benchmark_id: str
 hospital_profile: HospitalProfile

 peer_hospital_count: int = Field(..., description="Number of peer hospitals")

 # Performance percentiles (0-100)
 overall_percentile: float
 financial_percentile: float
 operational_percentile: float
 quality_percentile: float

 # Key insights
 strengths: List[str] = Field(default_factory=list)
 improvement_areas: List[str] = Field(default_factory=list)

 benchmark_date: datetime = Field(default_factory=datetime.now)
 confidence_level: float = Field(..., description="Benchmark confidence 0-1")

# API Request/Response Models
class HospitalAnalysisRequest(BaseModel):
 """Request for hospital performance analysis"""
 hospital_profile: HospitalProfile
 analysis_scope: List[ConsultingFocus]
 requested_deliverables: List[str] = Field(default_factory=list)

class HospitalAnalysisResponse(BaseModel):
 """Response with hospital analysis results"""
 analysis_id: str
 hospital_id: str
 analysis_date: datetime

 executive_summary: Dict[str, Any] = Field(default_factory=dict)
 performance_benchmarks: HospitalBenchmarkData
 opportunities: List[ConsultingOpportunity]
 recommendations: List[ConsultingRecommendation]

 confidence_score: float = Field(..., description="Overall confidence 0-1")
 next_steps: List[str] = Field(default_factory=list)

class ConsultingProposal(BaseModel):
 """McKinsey-style consulting proposal"""
 proposal_id: str
 hospital_profile: HospitalProfile

 # Executive summary
 executive_summary: str
 situation_analysis: str
 improvement_opportunity: str
 proposed_approach: str
 expected_outcomes: str

 # Service offering
 recommended_service_tier: ServiceTier
 engagement_duration_months: int = Field(..., description="Project duration")
 total_investment: Decimal
 expected_roi: float
 payback_period_months: int

 # Deliverables
 key_deliverables: List[str] = Field(default_factory=list)
 success_metrics: List[str] = Field(default_factory=list)

 # Commercial terms
 pricing_structure: Dict[str, Decimal] = Field(default_factory=dict)
 payment_terms: str

 # Proposal metadata
 created_date: datetime = Field(default_factory=datetime.now)
 created_by: str
 status: str = Field(default="draft") # draft, submitted, under_review, accepted, rejected

# Indian Healthcare Context Models
class GovernmentScheme(BaseModel):
 """Indian government healthcare scheme"""
 scheme_name: str
 coverage_amount: Decimal
 beneficiary_criteria: List[str]
 reimbursement_rates: Dict[str, float] = Field(default_factory=dict)
 processing_time_days: int
 state_specific: bool = False

class RegulatoryRequirement(BaseModel):
 """Indian healthcare regulatory requirement"""
 requirement_type: str
 applicable_hospital_types: List[HospitalType]
 applicable_states: List[str] = Field(default_factory=list)
 compliance_deadline: Optional[date] = None
 implementation_complexity: str # low, medium, high

# Export all models
__all__ = [
 "HospitalTier", "HospitalType", "ServiceTier", "ConsultingFocus",
 "HospitalLocation", "HospitalFinancialMetrics", "HospitalOperationalMetrics",
 "HospitalQualityMetrics", "HospitalStakeholder", "HospitalProfile",
 "ConsultingOpportunity", "ConsultingRecommendation", "ConsultingProject",
 "HospitalBenchmarkData", "HospitalAnalysisRequest", "HospitalAnalysisResponse",
 "ConsultingProposal", "GovernmentScheme", "RegulatoryRequirement"
]