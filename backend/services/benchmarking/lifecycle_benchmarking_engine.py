#!/usr/bin/env python3
"""
Lifecycle-Aware Hospital Benchmarking Engine
Dynamic benchmarking system that considers hospital age, maturity stage, and growth velocity
"""

import asyncio
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import math

class HospitalLifecycleStage(str, Enum):
    """Hospital lifecycle stages based on age and maturity"""
    STARTUP = "startup"           # 0-2 years
    GROWTH = "growth"             # 3-7 years  
    EXPANSION = "expansion"       # 8-15 years
    MATURITY = "maturity"         # 16-25 years
    ESTABLISHED = "established"   # 26+ years

class GrowthVelocityTier(str, Enum):
    """Growth velocity performance tiers"""
    BREAKTHROUGH = "breakthrough"  # Top 10% growth velocity
    ACCELERATING = "accelerating"  # Top 25% growth velocity
    STEADY = "steady"             # Average growth velocity
    SLOW = "slow"                 # Below average growth
    DECLINING = "declining"       # Negative growth trajectory

@dataclass
class HospitalLifecycleProfile:
    """Hospital lifecycle and maturity profile"""
    hospital_id: str
    hospital_name: str
    established_year: int
    current_age_years: int
    lifecycle_stage: HospitalLifecycleStage
    
    # Growth context
    bed_count_growth_rate: float  # Annual % growth in beds
    revenue_growth_rate: float    # Annual % revenue growth
    patient_volume_growth_rate: float  # Annual % patient growth
    service_expansion_rate: float     # New services added per year
    
    # Market context
    city_tier: str
    competition_density: str  # "low", "medium", "high"
    market_maturity: str     # "emerging", "growing", "mature", "saturated"

@dataclass
class GrowthVelocityBenchmarks:
    """Dynamic benchmarks based on growth velocity expectations"""
    stage: HospitalLifecycleStage
    velocity_tier: GrowthVelocityTier
    
    # Financial growth targets (annual % improvement)
    revenue_growth_target: float
    margin_improvement_target: float
    ar_days_reduction_target: float
    collection_rate_improvement: float
    
    # Operational growth targets
    occupancy_growth_target: float
    efficiency_improvement_target: float
    capacity_utilization_growth: float
    
    # Quality advancement targets
    satisfaction_improvement_target: float
    quality_score_advancement: float
    
    # Time-bound milestones (months to achieve targets)
    short_term_milestone: int  # 6-12 months
    medium_term_milestone: int # 12-24 months
    long_term_milestone: int   # 24-36 months

@dataclass
class StageProgressionRoadmap:
    """Roadmap for progressing to next lifecycle stage"""
    current_stage: HospitalLifecycleStage
    next_stage: HospitalLifecycleStage
    progression_timeline_months: int
    
    # Key milestones to achieve progression
    financial_milestones: List[Dict[str, Any]]
    operational_milestones: List[Dict[str, Any]]
    infrastructure_milestones: List[Dict[str, Any]]
    capability_milestones: List[Dict[str, Any]]
    
    # Success probability and risk factors
    progression_probability: float
    risk_factors: List[str]
    enablers: List[str]

@dataclass
class LifecycleBenchmarkResult:
    """Complete lifecycle-aware benchmark analysis"""
    hospital_profile: HospitalLifecycleProfile
    velocity_benchmarks: GrowthVelocityBenchmarks
    progression_roadmap: StageProgressionRoadmap
    
    # Current performance vs lifecycle expectations
    velocity_score: float  # 0-100 score
    stage_readiness_score: float  # Ready for next stage?
    
    # Recommendations
    velocity_acceleration_plan: List[Dict[str, Any]]
    stage_progression_plan: List[Dict[str, Any]]
    
    # Projections
    projected_next_stage_timeline: int
    growth_trajectory_forecast: Dict[str, Any]


class LifecycleAwareBenchmarkingEngine:
    """
    Advanced benchmarking engine that considers hospital lifecycle stage and growth velocity
    Rather than static benchmarks, provides dynamic targets based on hospital maturity
    """
    
    def __init__(self):
        self.lifecycle_stage_definitions = self._load_stage_definitions()
        self.growth_velocity_models = self._load_velocity_models()
        self.progression_frameworks = self._load_progression_frameworks()
        
    def _load_stage_definitions(self) -> Dict[str, Any]:
        """Load lifecycle stage definitions and characteristics"""
        return {
            "startup": {
                "age_range": (0, 2),
                "focus_areas": ["survival", "market_entry", "basic_operations", "cash_flow"],
                "typical_challenges": ["capital_constraints", "market_awareness", "talent_acquisition"],
                "growth_expectations": {
                    "revenue_growth": (50, 200),  # 50-200% annual growth expected
                    "patient_volume": (30, 150),
                    "service_expansion": (2, 5)   # 2-5 new services per year
                }
            },
            "growth": {
                "age_range": (3, 7),
                "focus_areas": ["capacity_expansion", "service_diversification", "brand_building"],
                "typical_challenges": ["scaling_operations", "quality_consistency", "competition"],
                "growth_expectations": {
                    "revenue_growth": (25, 80),   # 25-80% annual growth
                    "patient_volume": (20, 60),
                    "service_expansion": (1, 3)
                }
            },
            "expansion": {
                "age_range": (8, 15),
                "focus_areas": ["market_leadership", "operational_excellence", "technology_adoption"],
                "typical_challenges": ["market_saturation", "margin_pressure", "regulatory_compliance"],
                "growth_expectations": {
                    "revenue_growth": (10, 30),   # 10-30% annual growth
                    "patient_volume": (8, 25),
                    "service_expansion": (0.5, 2)
                }
            },
            "maturity": {
                "age_range": (16, 25),
                "focus_areas": ["efficiency_optimization", "innovation", "market_consolidation"],
                "typical_challenges": ["growth_deceleration", "competitive_pressure", "cost_management"],
                "growth_expectations": {
                    "revenue_growth": (5, 15),    # 5-15% annual growth
                    "patient_volume": (3, 12),
                    "service_expansion": (0.2, 1)
                }
            },
            "established": {
                "age_range": (26, 100),
                "focus_areas": ["market_dominance", "legacy_management", "transformation"],
                "typical_challenges": ["digital_transformation", "legacy_systems", "next_gen_competition"],
                "growth_expectations": {
                    "revenue_growth": (2, 10),    # 2-10% annual growth
                    "patient_volume": (1, 8),
                    "service_expansion": (0.1, 0.5)
                }
            }
        }
        
    def _load_velocity_models(self) -> Dict[str, Any]:
        """Load growth velocity calculation models"""
        return {
            "breakthrough": {
                "percentile_threshold": 90,  # Top 10% performers
                "revenue_multiplier": 2.0,   # 2x stage average
                "efficiency_multiplier": 1.5,
                "quality_multiplier": 1.3,
                "timeline_acceleration": 0.7  # 30% faster milestones
            },
            "accelerating": {
                "percentile_threshold": 75,  # Top 25% performers
                "revenue_multiplier": 1.5,
                "efficiency_multiplier": 1.2,
                "quality_multiplier": 1.1,
                "timeline_acceleration": 0.8
            },
            "steady": {
                "percentile_threshold": 50,  # Median performers
                "revenue_multiplier": 1.0,
                "efficiency_multiplier": 1.0,
                "quality_multiplier": 1.0,
                "timeline_acceleration": 1.0
            },
            "slow": {
                "percentile_threshold": 25,  # Bottom 25% performers
                "revenue_multiplier": 0.7,
                "efficiency_multiplier": 0.8,
                "quality_multiplier": 0.9,
                "timeline_acceleration": 1.3   # 30% longer timelines
            },
            "declining": {
                "percentile_threshold": 10,  # Bottom 10% performers
                "revenue_multiplier": 0.5,
                "efficiency_multiplier": 0.6,
                "quality_multiplier": 0.7,
                "timeline_acceleration": 1.5   # 50% longer timelines
            }
        }
        
    def _load_progression_frameworks(self) -> Dict[str, Any]:
        """Load stage progression frameworks and requirements"""
        return {
            "startup_to_growth": {
                "minimum_age_months": 18,
                "financial_requirements": {
                    "positive_cash_flow_months": 6,
                    "revenue_stability_coefficient": 0.8,
                    "operating_margin_threshold": 0.05
                },
                "operational_requirements": {
                    "bed_occupancy_minimum": 0.60,
                    "patient_satisfaction_minimum": 7.0,
                    "staff_turnover_maximum": 0.30
                },
                "infrastructure_requirements": {
                    "basic_systems_implemented": True,
                    "quality_certifications": ["basic_license"],
                    "core_services_operational": 3
                }
            },
            "growth_to_expansion": {
                "minimum_age_months": 36,
                "financial_requirements": {
                    "consistent_profitability_months": 12,
                    "revenue_stability_coefficient": 0.85,
                    "operating_margin_threshold": 0.08
                },
                "operational_requirements": {
                    "bed_occupancy_minimum": 0.70,
                    "patient_satisfaction_minimum": 7.5,
                    "staff_turnover_maximum": 0.25
                },
                "infrastructure_requirements": {
                    "advanced_systems_implemented": True,
                    "quality_certifications": ["nabh_entry"],
                    "specialized_services": 2
                }
            },
            "expansion_to_maturity": {
                "minimum_age_months": 96,
                "financial_requirements": {
                    "market_leadership_metrics": True,
                    "revenue_stability_coefficient": 0.90,
                    "operating_margin_threshold": 0.12
                },
                "operational_requirements": {
                    "bed_occupancy_minimum": 0.75,
                    "patient_satisfaction_minimum": 8.0,
                    "staff_turnover_maximum": 0.20
                },
                "infrastructure_requirements": {
                    "comprehensive_systems": True,
                    "quality_certifications": ["nabh_full", "iso"],
                    "center_of_excellence": 1
                }
            }
        }

    async def analyze_hospital_lifecycle(self, hospital_data: Dict[str, Any]) -> LifecycleBenchmarkResult:
        """
        Complete lifecycle-aware benchmarking analysis
        """
        
        print(f"\nAnalyzing lifecycle stage for {hospital_data['name']}...")
        
        # 1. Determine lifecycle profile
        lifecycle_profile = self._create_lifecycle_profile(hospital_data)
        
        # 2. Calculate growth velocity
        velocity_tier = self._calculate_growth_velocity(hospital_data, lifecycle_profile)
        
        # 3. Generate dynamic benchmarks
        velocity_benchmarks = self._generate_velocity_benchmarks(lifecycle_profile, velocity_tier)
        
        # 4. Create progression roadmap
        progression_roadmap = self._create_progression_roadmap(lifecycle_profile, hospital_data)
        
        # 5. Calculate scores and recommendations
        velocity_score = self._calculate_velocity_score(hospital_data, velocity_benchmarks)
        stage_readiness = self._assess_stage_readiness(lifecycle_profile, hospital_data)
        
        # 6. Generate acceleration and progression plans
        acceleration_plan = self._create_velocity_acceleration_plan(
            hospital_data, lifecycle_profile, velocity_benchmarks
        )
        
        progression_plan = self._create_stage_progression_plan(
            lifecycle_profile, progression_roadmap
        )
        
        # 7. Create growth projections
        growth_forecast = self._project_growth_trajectory(
            hospital_data, lifecycle_profile, velocity_tier
        )
        
        result = LifecycleBenchmarkResult(
            hospital_profile=lifecycle_profile,
            velocity_benchmarks=velocity_benchmarks,
            progression_roadmap=progression_roadmap,
            velocity_score=velocity_score,
            stage_readiness_score=stage_readiness,
            velocity_acceleration_plan=acceleration_plan,
            stage_progression_plan=progression_plan,
            projected_next_stage_timeline=progression_roadmap.progression_timeline_months,
            growth_trajectory_forecast=growth_forecast
        )
        
        return result
        
    def _create_lifecycle_profile(self, hospital_data: Dict[str, Any]) -> HospitalLifecycleProfile:
        """Create hospital lifecycle profile"""
        
        # Calculate age and determine stage
        current_year = datetime.now().year
        established_year = hospital_data.get('established_year', current_year - 5)
        age_years = current_year - established_year
        
        stage = self._determine_lifecycle_stage(age_years)
        
        # Calculate growth rates (with fallback values)
        revenue_growth = hospital_data.get('revenue_growth_rate', self._estimate_revenue_growth(hospital_data))
        bed_growth = hospital_data.get('bed_growth_rate', 0.05)  # 5% default
        patient_growth = hospital_data.get('patient_growth_rate', revenue_growth * 0.8)
        service_expansion = hospital_data.get('service_expansion_rate', 1.0)
        
        return HospitalLifecycleProfile(
            hospital_id=hospital_data.get('hospital_id', f"hosp_{hospital_data['name'][:10]}"),
            hospital_name=hospital_data['name'],
            established_year=established_year,
            current_age_years=age_years,
            lifecycle_stage=stage,
            bed_count_growth_rate=bed_growth,
            revenue_growth_rate=revenue_growth,
            patient_volume_growth_rate=patient_growth,
            service_expansion_rate=service_expansion,
            city_tier=hospital_data.get('tier', 'tier_2'),
            competition_density=hospital_data.get('competition_density', 'medium'),
            market_maturity=hospital_data.get('market_maturity', 'growing')
        )
        
    def _determine_lifecycle_stage(self, age_years: int) -> HospitalLifecycleStage:
        """Determine lifecycle stage based on hospital age"""
        
        if age_years <= 2:
            return HospitalLifecycleStage.STARTUP
        elif age_years <= 7:
            return HospitalLifecycleStage.GROWTH
        elif age_years <= 15:
            return HospitalLifecycleStage.EXPANSION
        elif age_years <= 25:
            return HospitalLifecycleStage.MATURITY
        else:
            return HospitalLifecycleStage.ESTABLISHED
            
    def _estimate_revenue_growth(self, hospital_data: Dict[str, Any]) -> float:
        """Estimate revenue growth rate from available data"""
        
        # Use occupancy and pricing trends as proxy
        occupancy = hospital_data.get('occupancy_rate', 0.70)
        market_growth = 0.08  # Default 8% healthcare market growth
        
        if occupancy > 0.85:
            return market_growth + 0.05  # High occupancy suggests strong growth
        elif occupancy < 0.60:
            return market_growth - 0.03  # Low occupancy suggests challenges
        else:
            return market_growth
            
    def _calculate_growth_velocity(self, hospital_data: Dict[str, Any], 
                                 profile: HospitalLifecycleProfile) -> GrowthVelocityTier:
        """Calculate growth velocity tier based on stage-adjusted performance"""
        
        stage_expectations = self.lifecycle_stage_definitions[profile.lifecycle_stage.value]
        expected_revenue_growth = stage_expectations["growth_expectations"]["revenue_growth"]
        
        # Calculate velocity score (0-100)
        actual_growth = profile.revenue_growth_rate * 100
        min_expected, max_expected = expected_revenue_growth
        
        if actual_growth >= max_expected:
            velocity_score = 100
        elif actual_growth <= min_expected:
            velocity_score = 25
        else:
            # Linear interpolation between min and max
            velocity_score = 25 + (75 * (actual_growth - min_expected) / (max_expected - min_expected))
        
        # Adjust for operational performance
        operational_multiplier = self._calculate_operational_multiplier(hospital_data)
        adjusted_score = velocity_score * operational_multiplier
        
        # Determine tier
        if adjusted_score >= 90:
            return GrowthVelocityTier.BREAKTHROUGH
        elif adjusted_score >= 75:
            return GrowthVelocityTier.ACCELERATING
        elif adjusted_score >= 50:
            return GrowthVelocityTier.STEADY
        elif adjusted_score >= 25:
            return GrowthVelocityTier.SLOW
        else:
            return GrowthVelocityTier.DECLINING
            
    def _calculate_operational_multiplier(self, hospital_data: Dict[str, Any]) -> float:
        """Calculate operational performance multiplier"""
        
        factors = []
        
        # Occupancy factor
        occupancy = hospital_data.get('occupancy_rate', 0.70)
        if occupancy >= 0.85:
            factors.append(1.2)
        elif occupancy >= 0.75:
            factors.append(1.1)
        elif occupancy >= 0.65:
            factors.append(1.0)
        else:
            factors.append(0.9)
            
        # Quality factor
        satisfaction = hospital_data.get('patient_satisfaction_score', 75)
        if satisfaction >= 85:
            factors.append(1.1)
        elif satisfaction >= 80:
            factors.append(1.05)
        else:
            factors.append(0.95)
            
        # Efficiency factor
        ar_days = hospital_data.get('days_in_ar', 45)
        if ar_days <= 30:
            factors.append(1.1)
        elif ar_days <= 40:
            factors.append(1.0)
        else:
            factors.append(0.9)
            
        return sum(factors) / len(factors)
        
    def _generate_velocity_benchmarks(self, profile: HospitalLifecycleProfile, 
                                    velocity_tier: GrowthVelocityTier) -> GrowthVelocityBenchmarks:
        """Generate dynamic benchmarks based on lifecycle stage and velocity"""
        
        stage_def = self.lifecycle_stage_definitions[profile.lifecycle_stage.value]
        velocity_model = self.growth_velocity_models[velocity_tier.value]
        
        # Base growth expectations for stage
        base_revenue_growth = sum(stage_def["growth_expectations"]["revenue_growth"]) / 2
        
        # Apply velocity multipliers
        revenue_target = base_revenue_growth * velocity_model["revenue_multiplier"]
        
        # Calculate other targets based on revenue target
        margin_target = min(revenue_target * 0.15, 3.0)  # Max 3% annual improvement
        ar_reduction = max(revenue_target * 0.1, 2.0)    # Min 2 days reduction
        collection_improvement = min(revenue_target * 0.02, 2.0)  # Max 2% improvement
        
        # Operational targets
        occupancy_growth = min(revenue_target * 0.08, 5.0)  # Max 5% improvement
        efficiency_target = min(revenue_target * 0.12, 8.0)  # Max 8% improvement
        
        # Quality targets
        satisfaction_target = min(revenue_target * 0.04, 3.0)  # Max 3 points
        quality_advancement = min(revenue_target * 0.06, 4.0)  # Max 4% improvement
        
        # Timeline adjustments
        base_timeline = 12  # 12 months base
        short_term = int(base_timeline * 0.5 * velocity_model["timeline_acceleration"])
        medium_term = int(base_timeline * 1.5 * velocity_model["timeline_acceleration"])
        long_term = int(base_timeline * 2.5 * velocity_model["timeline_acceleration"])
        
        return GrowthVelocityBenchmarks(
            stage=profile.lifecycle_stage,
            velocity_tier=velocity_tier,
            revenue_growth_target=revenue_target,
            margin_improvement_target=margin_target,
            ar_days_reduction_target=ar_reduction,
            collection_rate_improvement=collection_improvement,
            occupancy_growth_target=occupancy_growth,
            efficiency_improvement_target=efficiency_target,
            capacity_utilization_growth=efficiency_target * 0.8,
            satisfaction_improvement_target=satisfaction_target,
            quality_score_advancement=quality_advancement,
            short_term_milestone=short_term,
            medium_term_milestone=medium_term,
            long_term_milestone=long_term
        )
        
    def _create_progression_roadmap(self, profile: HospitalLifecycleProfile, 
                                  hospital_data: Dict[str, Any]) -> StageProgressionRoadmap:
        """Create roadmap for progressing to next lifecycle stage"""
        
        current_stage = profile.lifecycle_stage
        next_stage = self._get_next_stage(current_stage)
        
        if next_stage is None:
            # Already at established stage
            return StageProgressionRoadmap(
                current_stage=current_stage,
                next_stage=current_stage,
                progression_timeline_months=0,
                financial_milestones=[],
                operational_milestones=[],
                infrastructure_milestones=[],
                capability_milestones=[],
                progression_probability=1.0,
                risk_factors=[],
                enablers=["Market leadership position maintained"]
            )
        
        # Get progression requirements
        progression_key = f"{current_stage.value}_to_{next_stage.value}"
        requirements = self.progression_frameworks.get(progression_key, {})
        
        # Calculate timeline based on current readiness
        readiness_score = self._assess_stage_readiness(profile, hospital_data)
        base_timeline = requirements.get("minimum_age_months", 24)
        timeline = max(base_timeline, int(base_timeline * (2 - readiness_score)))
        
        # Create milestones
        financial_milestones = self._create_financial_milestones(requirements, hospital_data)
        operational_milestones = self._create_operational_milestones(requirements, hospital_data)
        infrastructure_milestones = self._create_infrastructure_milestones(requirements, hospital_data)
        capability_milestones = self._create_capability_milestones(requirements, hospital_data)
        
        # Assess probability and risks
        probability = min(0.95, readiness_score * 0.8 + 0.2)
        risks = self._identify_progression_risks(profile, hospital_data, requirements)
        enablers = self._identify_progression_enablers(profile, hospital_data)
        
        return StageProgressionRoadmap(
            current_stage=current_stage,
            next_stage=next_stage,
            progression_timeline_months=timeline,
            financial_milestones=financial_milestones,
            operational_milestones=operational_milestones,
            infrastructure_milestones=infrastructure_milestones,
            capability_milestones=capability_milestones,
            progression_probability=probability,
            risk_factors=risks,
            enablers=enablers
        )
        
    def _get_next_stage(self, current: HospitalLifecycleStage) -> Optional[HospitalLifecycleStage]:
        """Get next lifecycle stage"""
        stage_order = [
            HospitalLifecycleStage.STARTUP,
            HospitalLifecycleStage.GROWTH,
            HospitalLifecycleStage.EXPANSION,
            HospitalLifecycleStage.MATURITY,
            HospitalLifecycleStage.ESTABLISHED
        ]
        
        try:
            current_index = stage_order.index(current)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass
        
        return None
        
    def _assess_stage_readiness(self, profile: HospitalLifecycleProfile, 
                              hospital_data: Dict[str, Any]) -> float:
        """Assess readiness for next stage (0-1 score)"""
        
        next_stage = self._get_next_stage(profile.lifecycle_stage)
        if not next_stage:
            return 1.0
            
        progression_key = f"{profile.lifecycle_stage.value}_to_{next_stage.value}"
        requirements = self.progression_frameworks.get(progression_key, {})
        
        if not requirements:
            return 0.5
            
        readiness_factors = []
        
        # Financial readiness
        fin_req = requirements.get("financial_requirements", {})
        margin = hospital_data.get('operating_margin', 0.05)
        margin_threshold = fin_req.get("operating_margin_threshold", 0.05)
        fin_score = min(1.0, margin / margin_threshold) if margin_threshold > 0 else 0.5
        readiness_factors.append(fin_score)
        
        # Operational readiness
        ops_req = requirements.get("operational_requirements", {})
        occupancy = hospital_data.get('occupancy_rate', 0.70)
        occupancy_min = ops_req.get("bed_occupancy_minimum", 0.60)
        ops_score = min(1.0, occupancy / occupancy_min) if occupancy_min > 0 else 0.5
        readiness_factors.append(ops_score)
        
        # Age readiness
        min_age = requirements.get("minimum_age_months", 12) / 12
        age_score = min(1.0, profile.current_age_years / min_age) if min_age > 0 else 1.0
        readiness_factors.append(age_score)
        
        return sum(readiness_factors) / len(readiness_factors)
        
    def _create_financial_milestones(self, requirements: Dict[str, Any], 
                                   hospital_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create financial milestones for stage progression"""
        
        milestones = []
        fin_req = requirements.get("financial_requirements", {})
        
        if "operating_margin_threshold" in fin_req:
            current_margin = hospital_data.get('operating_margin', 0.05)
            target_margin = fin_req["operating_margin_threshold"]
            
            milestones.append({
                "milestone": "Achieve Target Operating Margin",
                "current_value": f"{current_margin:.1%}",
                "target_value": f"{target_margin:.1%}",
                "timeline_months": 12,
                "priority": "high" if current_margin < target_margin * 0.8 else "medium"
            })
            
        if "revenue_stability_coefficient" in fin_req:
            milestones.append({
                "milestone": "Establish Revenue Stability",
                "current_value": "Variable",
                "target_value": f"{fin_req['revenue_stability_coefficient']:.1%} consistency",
                "timeline_months": 18,
                "priority": "medium"
            })
            
        return milestones
        
    def _create_operational_milestones(self, requirements: Dict[str, Any], 
                                     hospital_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create operational milestones for stage progression"""
        
        milestones = []
        ops_req = requirements.get("operational_requirements", {})
        
        if "bed_occupancy_minimum" in ops_req:
            current_occupancy = hospital_data.get('occupancy_rate', 0.70)
            target_occupancy = ops_req["bed_occupancy_minimum"]
            
            milestones.append({
                "milestone": "Achieve Target Bed Occupancy",
                "current_value": f"{current_occupancy:.1%}",
                "target_value": f"{target_occupancy:.1%}",
                "timeline_months": 9,
                "priority": "high" if current_occupancy < target_occupancy else "low"
            })
            
        if "patient_satisfaction_minimum" in ops_req:
            current_satisfaction = hospital_data.get('patient_satisfaction_score', 75)
            target_satisfaction = ops_req["patient_satisfaction_minimum"] * 10  # Convert to 100 scale
            
            milestones.append({
                "milestone": "Improve Patient Satisfaction",
                "current_value": f"{current_satisfaction:.1f}%",
                "target_value": f"{target_satisfaction:.1f}%",
                "timeline_months": 15,
                "priority": "medium"
            })
            
        return milestones
        
    def _create_infrastructure_milestones(self, requirements: Dict[str, Any], 
                                        hospital_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create infrastructure milestones for stage progression"""
        
        milestones = []
        infra_req = requirements.get("infrastructure_requirements", {})
        
        if "quality_certifications" in infra_req:
            required_certs = infra_req["quality_certifications"]
            milestones.append({
                "milestone": "Obtain Required Certifications",
                "current_value": "Basic licensing",
                "target_value": ", ".join(required_certs),
                "timeline_months": 24,
                "priority": "high"
            })
            
        if "specialized_services" in infra_req:
            required_services = infra_req["specialized_services"]
            milestones.append({
                "milestone": "Launch Specialized Services",
                "current_value": "General services",
                "target_value": f"{required_services} specialized units",
                "timeline_months": 18,
                "priority": "medium"
            })
            
        return milestones
        
    def _create_capability_milestones(self, requirements: Dict[str, Any], 
                                    hospital_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create capability milestones for stage progression"""
        
        return [
            {
                "milestone": "Develop Advanced Clinical Capabilities",
                "current_value": "Basic clinical services",
                "target_value": "Advanced procedures and protocols",
                "timeline_months": 20,
                "priority": "medium"
            },
            {
                "milestone": "Implement Technology Infrastructure",
                "current_value": "Basic IT systems",
                "target_value": "Integrated digital platform",
                "timeline_months": 15,
                "priority": "high"
            }
        ]
        
    def _identify_progression_risks(self, profile: HospitalLifecycleProfile, 
                                  hospital_data: Dict[str, Any],
                                  requirements: Dict[str, Any]) -> List[str]:
        """Identify risks to stage progression"""
        
        risks = []
        
        # Financial risks
        if hospital_data.get('operating_margin', 0.05) < 0.08:
            risks.append("Low operating margins may constrain growth investments")
            
        # Market risks
        if profile.competition_density == "high":
            risks.append("High market competition may slow patient acquisition")
            
        # Operational risks
        if hospital_data.get('staff_turnover_rate', 0.15) > 0.25:
            risks.append("High staff turnover threatens operational stability")
            
        # Age-related risks
        if profile.current_age_years < 3:
            risks.append("Young hospital age increases execution uncertainty")
            
        return risks[:3]  # Top 3 risks
        
    def _identify_progression_enablers(self, profile: HospitalLifecycleProfile, 
                                     hospital_data: Dict[str, Any]) -> List[str]:
        """Identify factors that enable stage progression"""
        
        enablers = []
        
        # Growth enablers
        if profile.revenue_growth_rate > 0.15:
            enablers.append("Strong revenue growth provides investment capacity")
            
        # Quality enablers
        if hospital_data.get('patient_satisfaction_score', 75) > 80:
            enablers.append("High patient satisfaction supports market expansion")
            
        # Efficiency enablers
        if hospital_data.get('occupancy_rate', 0.70) > 0.80:
            enablers.append("High capacity utilization demonstrates market demand")
            
        # Market enablers
        if profile.city_tier in ["tier_1", "tier_2"]:
            enablers.append("Favorable market location supports growth")
            
        return enablers[:3]  # Top 3 enablers
        
    def _calculate_velocity_score(self, hospital_data: Dict[str, Any], 
                                benchmarks: GrowthVelocityBenchmarks) -> float:
        """Calculate overall growth velocity score (0-100)"""
        
        scores = []
        
        # Revenue growth score
        revenue_growth = hospital_data.get('revenue_growth_rate', 0.08) * 100
        target_growth = benchmarks.revenue_growth_target
        revenue_score = min(100, (revenue_growth / target_growth) * 100) if target_growth > 0 else 50
        scores.append(revenue_score)
        
        # Operational efficiency score
        occupancy = hospital_data.get('occupancy_rate', 0.70) * 100
        target_occupancy = 75 + benchmarks.occupancy_growth_target  # Base + growth
        efficiency_score = min(100, (occupancy / target_occupancy) * 100) if target_occupancy > 0 else 50
        scores.append(efficiency_score)
        
        # Quality score
        satisfaction = hospital_data.get('patient_satisfaction_score', 75)
        target_satisfaction = 75 + benchmarks.satisfaction_improvement_target
        quality_score = min(100, (satisfaction / target_satisfaction) * 100) if target_satisfaction > 0 else 50
        scores.append(quality_score)
        
        return sum(scores) / len(scores)
        
    def _create_velocity_acceleration_plan(self, hospital_data: Dict[str, Any],
                                         profile: HospitalLifecycleProfile,
                                         benchmarks: GrowthVelocityBenchmarks) -> List[Dict[str, Any]]:
        """Create plan to accelerate growth velocity"""
        
        plan = []
        
        # Revenue acceleration
        current_revenue_growth = hospital_data.get('revenue_growth_rate', 0.08) * 100
        if current_revenue_growth < benchmarks.revenue_growth_target:
            plan.append({
                "initiative": "Revenue Growth Acceleration",
                "description": "Implement revenue optimization strategies",
                "current_performance": f"{current_revenue_growth:.1f}% annual growth",
                "target_performance": f"{benchmarks.revenue_growth_target:.1f}% annual growth",
                "timeline": f"{benchmarks.short_term_milestone} months",
                "investment_required": "₹25-50 lakhs",
                "expected_impact": f"+{benchmarks.revenue_growth_target - current_revenue_growth:.1f}% revenue growth",
                "priority": "high"
            })
            
        # Operational efficiency acceleration
        current_occupancy = hospital_data.get('occupancy_rate', 0.70) * 100
        target_occupancy = 75 + benchmarks.occupancy_growth_target
        if current_occupancy < target_occupancy:
            plan.append({
                "initiative": "Capacity Utilization Enhancement",
                "description": "Optimize bed utilization and patient flow",
                "current_performance": f"{current_occupancy:.1f}% occupancy",
                "target_performance": f"{target_occupancy:.1f}% occupancy", 
                "timeline": f"{benchmarks.medium_term_milestone} months",
                "investment_required": "₹15-30 lakhs",
                "expected_impact": f"+{target_occupancy - current_occupancy:.1f}% capacity utilization",
                "priority": "medium"
            })
            
        # Quality enhancement
        current_satisfaction = hospital_data.get('patient_satisfaction_score', 75)
        target_satisfaction = 75 + benchmarks.satisfaction_improvement_target
        if current_satisfaction < target_satisfaction:
            plan.append({
                "initiative": "Patient Experience Excellence",
                "description": "Implement comprehensive patient experience program",
                "current_performance": f"{current_satisfaction:.1f}% satisfaction",
                "target_performance": f"{target_satisfaction:.1f}% satisfaction",
                "timeline": f"{benchmarks.long_term_milestone} months", 
                "investment_required": "₹10-20 lakhs",
                "expected_impact": f"+{target_satisfaction - current_satisfaction:.1f} points satisfaction",
                "priority": "medium"
            })
            
        return plan
        
    def _create_stage_progression_plan(self, profile: HospitalLifecycleProfile,
                                     roadmap: StageProgressionRoadmap) -> List[Dict[str, Any]]:
        """Create plan for stage progression"""
        
        plan = []
        
        # Financial progression
        for milestone in roadmap.financial_milestones:
            plan.append({
                "category": "Financial Development",
                "milestone": milestone["milestone"],
                "current_status": milestone["current_value"],
                "target": milestone["target_value"],
                "timeline": f"{milestone['timeline_months']} months",
                "priority": milestone["priority"],
                "success_factors": ["Consistent revenue growth", "Cost optimization", "Cash flow management"]
            })
            
        # Operational progression  
        for milestone in roadmap.operational_milestones:
            plan.append({
                "category": "Operational Excellence",
                "milestone": milestone["milestone"],
                "current_status": milestone["current_value"],
                "target": milestone["target_value"],
                "timeline": f"{milestone['timeline_months']} months",
                "priority": milestone["priority"],
                "success_factors": ["Process optimization", "Staff development", "Quality systems"]
            })
            
        # Infrastructure progression
        for milestone in roadmap.infrastructure_milestones:
            plan.append({
                "category": "Infrastructure & Capabilities",
                "milestone": milestone["milestone"],
                "current_status": milestone["current_value"],
                "target": milestone["target_value"],
                "timeline": f"{milestone['timeline_months']} months",
                "priority": milestone["priority"],
                "success_factors": ["Technology investment", "Facility expansion", "Equipment upgrades"]
            })
            
        return plan
        
    def _project_growth_trajectory(self, hospital_data: Dict[str, Any],
                                 profile: HospitalLifecycleProfile,
                                 velocity_tier: GrowthVelocityTier) -> Dict[str, Any]:
        """Project future growth trajectory"""
        
        current_revenue = hospital_data.get('annual_revenue', 500000000)  # Default ₹50 crores
        growth_rate = profile.revenue_growth_rate
        velocity_multiplier = self.growth_velocity_models[velocity_tier.value]["revenue_multiplier"]
        
        # Project 5-year trajectory
        projections = {}
        for year in range(1, 6):
            projected_revenue = current_revenue * ((1 + growth_rate * velocity_multiplier) ** year)
            projections[f"year_{year}"] = {
                "revenue": projected_revenue,
                "growth_rate": growth_rate * velocity_multiplier,
                "confidence": max(0.5, 0.9 - (year * 0.1))  # Decreasing confidence over time
            }
            
        # Milestone projections
        next_stage = self._get_next_stage(profile.lifecycle_stage)
        stage_transition = {
            "target_stage": next_stage.value if next_stage else "established",
            "estimated_timeline_months": 24 if next_stage else 0,
            "probability": 0.75 if next_stage else 1.0
        }
        
        return {
            "revenue_projections": projections,
            "stage_transition": stage_transition,
            "velocity_trend": velocity_tier.value,
            "risk_adjusted_confidence": 0.8
        }

    def generate_lifecycle_report(self, analysis: LifecycleBenchmarkResult) -> str:
        """Generate comprehensive lifecycle-aware benchmark report"""
        
        profile = analysis.hospital_profile
        benchmarks = analysis.velocity_benchmarks
        roadmap = analysis.progression_roadmap
        
        report = f"""
{'='*80}
LIFECYCLE-AWARE HOSPITAL BENCHMARKING REPORT
{'='*80}

Hospital: {profile.hospital_name}
Analysis Date: {datetime.now().strftime("%Y-%m-%d")}
Hospital Age: {profile.current_age_years} years

LIFECYCLE PROFILE:
Current Stage: {profile.lifecycle_stage.value.upper().replace('_', ' ')}
Growth Velocity Tier: {benchmarks.velocity_tier.value.upper().replace('_', ' ')}
Velocity Score: {analysis.velocity_score:.1f}/100
Stage Readiness: {analysis.stage_readiness_score:.1%}

GROWTH CONTEXT:
• Revenue Growth Rate: {profile.revenue_growth_rate:.1%} annually
• Market Position: {profile.city_tier.replace('_', ' ').title()} city, {profile.competition_density} competition
• Market Maturity: {profile.market_maturity.title()}

DYNAMIC BENCHMARKS (Stage-Adjusted):
"""
        
        report += f"""
Financial Growth Targets:
• Revenue Growth Target: {benchmarks.revenue_growth_target:.1f}% annually
• Margin Improvement: {benchmarks.margin_improvement_target:.1f}% annually  
• AR Days Reduction: {benchmarks.ar_days_reduction_target:.1f} days annually
• Collection Rate Improvement: {benchmarks.collection_rate_improvement:.1f}% annually

Operational Velocity Targets:
• Occupancy Growth: {benchmarks.occupancy_growth_target:.1f}% annually
• Efficiency Improvement: {benchmarks.efficiency_improvement_target:.1f}% annually
• Capacity Utilization Growth: {benchmarks.capacity_utilization_growth:.1f}% annually

Quality Advancement Targets:
• Satisfaction Improvement: {benchmarks.satisfaction_improvement_target:.1f} points annually
• Quality Score Advancement: {benchmarks.quality_score_advancement:.1f}% annually

MILESTONE TIMELINES:
• Short-term Goals: {benchmarks.short_term_milestone} months
• Medium-term Goals: {benchmarks.medium_term_milestone} months  
• Long-term Goals: {benchmarks.long_term_milestone} months

STAGE PROGRESSION ROADMAP:
"""

        report += f"""
Current Stage: {roadmap.current_stage.value.title()}
Next Stage: {roadmap.next_stage.value.title()}
Progression Timeline: {roadmap.progression_timeline_months} months
Success Probability: {roadmap.progression_probability:.1%}

Key Milestones for Next Stage:
"""
        
        # Add milestones
        all_milestones = (roadmap.financial_milestones + 
                         roadmap.operational_milestones + 
                         roadmap.infrastructure_milestones)[:5]
        
        for i, milestone in enumerate(all_milestones, 1):
            report += f"""
{i}. {milestone['milestone']}
   Current: {milestone['current_value']} → Target: {milestone['target_value']}
   Timeline: {milestone['timeline_months']} months | Priority: {milestone['priority'].upper()}
"""

        report += f"""

VELOCITY ACCELERATION PLAN:
"""
        
        for i, initiative in enumerate(analysis.velocity_acceleration_plan, 1):
            report += f"""
{i}. {initiative['initiative']} ({initiative['priority'].upper()} PRIORITY)
   Current: {initiative['current_performance']}
   Target: {initiative['target_performance']}
   Timeline: {initiative['timeline']}
   Investment: {initiative['investment_required']}
   Impact: {initiative['expected_impact']}
"""

        report += f"""

GROWTH TRAJECTORY FORECAST:
"""
        
        forecast = analysis.growth_trajectory_forecast
        for year, data in forecast["revenue_projections"].items():
            year_num = year.split('_')[1]
            report += f"Year {year_num}: ₹{data['revenue']/10000000:.1f} crores ({data['growth_rate']:.1%} growth, {data['confidence']:.1%} confidence)\n"
            
        report += f"""

RISK FACTORS:
{chr(10).join(f'• {risk}' for risk in roadmap.risk_factors)}

SUCCESS ENABLERS:  
{chr(10).join(f'• {enabler}' for enabler in roadmap.enablers)}

STRATEGIC RECOMMENDATIONS:
"""

        # Add strategic recommendations based on stage and velocity
        if benchmarks.velocity_tier in [GrowthVelocityTier.SLOW, GrowthVelocityTier.DECLINING]:
            report += """
VELOCITY IMPROVEMENT REQUIRED:
• Implement aggressive revenue optimization strategies
• Focus on operational efficiency improvements  
• Consider market positioning adjustments
• Accelerate quality enhancement initiatives
"""
        elif benchmarks.velocity_tier == GrowthVelocityTier.BREAKTHROUGH:
            report += """
MAINTAIN MOMENTUM:
• Sustain current growth strategies
• Prepare for next stage transition
• Invest in scalable infrastructure
• Build competitive moats
"""
        else:
            report += """
ACCELERATION OPPORTUNITIES:
• Optimize current operations for higher velocity
• Identify breakthrough growth opportunities
• Strengthen competitive positioning
• Prepare infrastructure for next stage
"""

        report += f"""

{'='*80}
LIFECYCLE BENCHMARK SUMMARY
{'='*80}

This hospital is in the {profile.lifecycle_stage.value.upper()} stage with {benchmarks.velocity_tier.value.upper()} growth velocity.

IMMEDIATE PRIORITIES (Next {benchmarks.short_term_milestone} months):
1. Focus on velocity acceleration initiatives
2. Address stage progression prerequisites  
3. Optimize operational performance metrics
4. Build capabilities for next stage

SUCCESS PROBABILITY: {roadmap.progression_probability:.1%} for stage progression
VELOCITY CONFIDENCE: {analysis.velocity_score/100:.1%} current performance level

{'='*80}
END OF LIFECYCLE-AWARE BENCHMARK REPORT  
{'='*80}
"""
        
        return report


# DEMO FUNCTION - Lifecycle-Aware Benchmarking
async def demo_lifecycle_benchmarking():
    """
    Demo function showing lifecycle-aware benchmarking system
    """
    
    print("LIFECYCLE-AWARE HOSPITAL BENCHMARKING - DEMONSTRATION")
    print("="*60)
    print("Dynamic benchmarking based on hospital age, stage, and growth velocity.")
    
    # Sample hospital data with lifecycle context
    hospital_data = {
        "name": "MedLife Specialty Hospital",
        "hospital_id": "hosp_medlife_001", 
        "established_year": 2018,  # 7 years old - Growth stage
        "tier": "tier_2",
        "bed_count": 150,
        "annual_revenue": 350000000,  # ₹35 crores
        
        # Growth metrics
        "revenue_growth_rate": 0.28,  # 28% annual growth
        "bed_growth_rate": 0.15,     # 15% bed expansion
        "patient_growth_rate": 0.22,  # 22% patient growth
        "service_expansion_rate": 2.0, # 2 new services per year
        
        # Current performance
        "occupancy_rate": 0.72,
        "operating_margin": 0.11,
        "days_in_ar": 42,
        "collection_rate": 0.86,
        "patient_satisfaction_score": 78.5,
        "staff_turnover_rate": 0.18,
        
        # Market context
        "competition_density": "medium",
        "market_maturity": "growing"
    }
    
    # Initialize lifecycle engine and analyze
    engine = LifecycleAwareBenchmarkingEngine()
    
    print("Running lifecycle-aware analysis...")
    analysis = await engine.analyze_hospital_lifecycle(hospital_data)
    
    print("Analysis complete! Generating lifecycle report...")
    
    # Generate and display report
    report = engine.generate_lifecycle_report(analysis)
    print(report)
    
    # Show next steps
    print("\nLIFECYCLE-AWARE NEXT STEPS:")
    print("1. Focus on growth velocity acceleration vs static benchmarks")
    print("2. Prepare for next lifecycle stage transition")
    print("3. Implement stage-appropriate improvement initiatives")
    print("4. Monitor growth velocity metrics continuously")
    print("5. Adjust targets based on lifecycle progression")
    
    return {
        "status": "SUCCESS",
        "analysis": analysis,
        "lifecycle_stage": analysis.hospital_profile.lifecycle_stage.value,
        "velocity_tier": analysis.velocity_benchmarks.velocity_tier.value,
        "velocity_score": analysis.velocity_score,
        "stage_readiness": analysis.stage_readiness_score
    }

# READY FOR REAL LIFECYCLE-AWARE BENCHMARKING
if __name__ == "__main__":
    print("🏥 LIFECYCLE-AWARE HOSPITAL BENCHMARKING - PRODUCTION READY")
    print("This system benchmarks based on hospital lifecycle stage and growth velocity!")
    print("\nKey Features:")
    print("- Hospital age and lifecycle stage analysis")
    print("- Growth velocity tier assessment")
    print("- Dynamic stage-appropriate benchmarks")
    print("- Stage progression roadmaps")
    print("- Velocity acceleration plans")
    
    result = asyncio.run(demo_lifecycle_benchmarking())
    
    if result["status"] == "SUCCESS":
        print(f"\nSUCCESS: Lifecycle Analysis Complete")
        print(f"Lifecycle Stage: {result['lifecycle_stage'].title()}")
        print(f"Velocity Tier: {result['velocity_tier'].title()}")
        print(f"Velocity Score: {result['velocity_score']:.1f}/100")
        print(f"Stage Readiness: {result['stage_readiness']:.1%}")
        print("\nLifecycle-aware benchmarking system ready for deployment.")
    else:
        print(f"\nERROR: Analysis failed: {result.get('error', 'Unknown error')}")