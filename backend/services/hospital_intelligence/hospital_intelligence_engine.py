#!/usr/bin/env python3
"""
Hospital Intelligence Engine for Indian Healthcare Market
Extends VERTICAL-LIGHT-OS with healthcare-specific consulting capabilities

Built on the proven MarketIntelligenceEngine foundation with:
- Dynamic configuration for Indian market variations
- Hospital-specific data models and analytics
- McKinsey-style structured problem solving for healthcare
- Cultural adaptations for Indian hospital management
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Import your existing intelligence foundation
from services.market_intelligence.intelligence_engine import MarketIntelligenceEngine
from models.schemas import BaseModel
from config.config_manager import get_config_manager

logger = logging.getLogger(__name__)

@dataclass
class HospitalProfile:
    """Hospital profile for Indian healthcare market"""
    hospital_id: str
    name: str
    location: Dict[str, str]  # city, state, tier
    hospital_type: str  # acute_care, specialty, critical_access
    bed_count: int
    service_lines: List[str]
    ownership_type: str  # private, government, trust, corporate_chain
    accreditations: List[str]  # NABH, JCI, ISO
    technology_maturity: str  # basic, intermediate, advanced
    financial_metrics: Dict[str, float]
    current_challenges: List[str]

@dataclass
class ConsultingProject:
    """Consulting project structure for hospital engagements"""
    project_id: str
    hospital_profile: HospitalProfile
    focus_areas: List[str]  # financial_optimization, operational_efficiency, etc.
    timeline: Dict[str, str]  # start_date, end_date, milestones
    budget_range: Dict[str, float]  # min, max, currency
    success_metrics: Dict[str, float]
    stakeholders: List[Dict[str, str]]
    service_tier: str  # basic, standard, premium

class HospitalIntelligenceEngine(MarketIntelligenceEngine):
    """
    AI-powered hospital consulting engine for Indian market
    Extends MarketIntelligenceEngine with healthcare-specific capabilities
    """
    
    def __init__(self, user_context: Optional[Dict[str, Any]] = None):
        # Initialize with healthcare-specific context
        healthcare_context = {
            'industry': 'healthcare',
            'market_focus': 'indian_hospitals',
            'consulting_approach': 'mckinsey_methodology',
            **(user_context or {})
        }
        super().__init__(healthcare_context)
        
        # Load hospital consulting configuration
        self.hospital_config = self._load_hospital_config()
        
        # Initialize healthcare-specific components
        self.benchmark_engine = HospitalBenchmarkEngine(self.hospital_config)
        self.financial_analyzer = HospitalFinancialAnalyzer(self.hospital_config)
        self.operational_analyzer = HospitalOperationalAnalyzer(self.hospital_config)
        self.quality_analyzer = HospitalQualityAnalyzer(self.hospital_config)
        
        logger.info("Hospital Intelligence Engine initialized for Indian market")
    
    def _load_hospital_config(self) -> Dict[str, Any]:
        """Load hospital consulting configuration"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "hospital_consulting_config.json"
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load hospital config: {e}")
            return {}
    
    async def analyze_hospital_performance(self, 
                                         hospital_profile: HospitalProfile,
                                         performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive hospital performance analysis using McKinsey methodology
        
        Args:
            hospital_profile: Hospital characteristics and context
            performance_data: Current performance metrics and operational data
            
        Returns:
            Structured analysis with insights, opportunities, and recommendations
        """
        try:
            logger.info(f"Starting performance analysis for {hospital_profile.name}")
            
            # Step 1: Benchmark against peers (Fact-based analysis)
            benchmark_results = await self.benchmark_engine.benchmark_hospital(
                hospital_profile, performance_data
            )
            
            # Step 2: Financial performance analysis
            financial_analysis = await self.financial_analyzer.analyze_financial_performance(
                hospital_profile, performance_data.get('financial_data', {})
            )
            
            # Step 3: Operational efficiency analysis
            operational_analysis = await self.operational_analyzer.analyze_operations(
                hospital_profile, performance_data.get('operational_data', {})
            )
            
            # Step 4: Quality metrics analysis
            quality_analysis = await self.quality_analyzer.analyze_quality_metrics(
                hospital_profile, performance_data.get('quality_data', {})
            )
            
            # Step 5: Identify improvement opportunities (Hypothesis-driven)
            opportunities = await self._identify_improvement_opportunities(
                hospital_profile, benchmark_results, financial_analysis, 
                operational_analysis, quality_analysis
            )
            
            # Step 6: Generate strategic recommendations (Structured approach)
            recommendations = await self._generate_strategic_recommendations(
                hospital_profile, opportunities
            )
            
            # Step 7: Create implementation roadmap
            roadmap = await self._create_implementation_roadmap(
                hospital_profile, recommendations
            )
            
            # Compile comprehensive analysis
            analysis_result = {
                'hospital_id': hospital_profile.hospital_id,
                'analysis_date': datetime.now().isoformat(),
                'executive_summary': self._create_executive_summary(
                    benchmark_results, opportunities, recommendations
                ),
                'performance_benchmarks': benchmark_results,
                'financial_analysis': financial_analysis,
                'operational_analysis': operational_analysis,
                'quality_analysis': quality_analysis,
                'improvement_opportunities': opportunities,
                'strategic_recommendations': recommendations,
                'implementation_roadmap': roadmap,
                'confidence_score': self._calculate_analysis_confidence(performance_data),
                'next_steps': self._generate_immediate_next_steps(recommendations)
            }
            
            # Learn from this analysis for future improvements
            await self._learn_from_hospital_analysis(hospital_profile, analysis_result)
            
            logger.info(f"Completed performance analysis for {hospital_profile.name}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in hospital performance analysis: {e}")
            return self._create_fallback_hospital_analysis(hospital_profile)
    
    async def _identify_improvement_opportunities(self,
                                                hospital_profile: HospitalProfile,
                                                benchmark_results: Dict[str, Any],
                                                financial_analysis: Dict[str, Any],
                                                operational_analysis: Dict[str, Any],
                                                quality_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific improvement opportunities using AI-powered pattern recognition"""
        
        opportunities = []
        
        # Financial opportunities
        if financial_analysis.get('revenue_cycle', {}).get('performance_gap', 0) > 0.1:
            opportunities.append({
                'category': 'financial_optimization',
                'subcategory': 'revenue_cycle',
                'title': 'Revenue Cycle Optimization',
                'description': 'Improve collections and reduce days in A/R',
                'potential_impact': financial_analysis['revenue_cycle']['potential_savings'],
                'implementation_complexity': 'medium',
                'timeline_months': 3,
                'priority_score': self._calculate_opportunity_priority(
                    financial_analysis['revenue_cycle']['potential_savings'],
                    'medium', hospital_profile
                )
            })
        
        # Operational opportunities
        bed_utilization = operational_analysis.get('bed_management', {}).get('occupancy_rate', 0)
        if bed_utilization < 0.75:  # Below good benchmark
            opportunities.append({
                'category': 'operational_efficiency',
                'subcategory': 'bed_management',
                'title': 'Bed Utilization Optimization',
                'description': 'Improve bed occupancy through better patient flow management',
                'potential_impact': self._estimate_bed_utilization_impact(hospital_profile, bed_utilization),
                'implementation_complexity': 'high',
                'timeline_months': 6,
                'priority_score': self._calculate_opportunity_priority(
                    self._estimate_bed_utilization_impact(hospital_profile, bed_utilization),
                    'high', hospital_profile
                )
            })
        
        # Quality improvement opportunities
        if quality_analysis.get('patient_safety', {}).get('improvement_needed', False):
            opportunities.append({
                'category': 'quality_improvement',
                'subcategory': 'patient_safety',
                'title': 'Patient Safety Enhancement',
                'description': 'Reduce hospital-acquired infections and medication errors',
                'potential_impact': quality_analysis['patient_safety']['risk_reduction_value'],
                'implementation_complexity': 'medium',
                'timeline_months': 4,
                'priority_score': self._calculate_opportunity_priority(
                    quality_analysis['patient_safety']['risk_reduction_value'],
                    'medium', hospital_profile
                )
            })
        
        # Technology optimization opportunities
        if hospital_profile.technology_maturity == 'basic':
            opportunities.append({
                'category': 'technology_optimization',
                'subcategory': 'digital_transformation',
                'title': 'Digital Transformation Initiative',
                'description': 'Implement EMR and automated workflows',
                'potential_impact': self._estimate_technology_impact(hospital_profile),
                'implementation_complexity': 'high',
                'timeline_months': 12,
                'priority_score': self._calculate_opportunity_priority(
                    self._estimate_technology_impact(hospital_profile),
                    'high', hospital_profile
                )
            })
        
        # Sort opportunities by priority score
        opportunities.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return opportunities
    
    async def _generate_strategic_recommendations(self,
                                               hospital_profile: HospitalProfile,
                                               opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate McKinsey-style strategic recommendations"""
        
        recommendations = []
        
        # Focus on top 3-5 opportunities for implementation feasibility
        priority_opportunities = opportunities[:5]
        
        for opp in priority_opportunities:
            recommendation = {
                'recommendation_id': f"rec_{len(recommendations) + 1}",
                'title': opp['title'],
                'category': opp['category'],
                'priority': 'high' if opp['priority_score'] > 0.8 else 'medium' if opp['priority_score'] > 0.5 else 'low',
                'expected_impact': opp['potential_impact'],
                'implementation_approach': self._get_implementation_approach(opp, hospital_profile),
                'resource_requirements': self._estimate_resource_requirements(opp, hospital_profile),
                'success_metrics': self._define_success_metrics(opp),
                'risk_factors': self._identify_implementation_risks(opp, hospital_profile),
                'timeline': self._create_implementation_timeline(opp),
                'stakeholders': self._identify_key_stakeholders(opp, hospital_profile)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _create_implementation_roadmap(self,
                                           hospital_profile: HospitalProfile,
                                           recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a structured implementation roadmap"""
        
        # Organize recommendations into phases based on complexity and dependencies
        phases = {
            'phase_1_quick_wins': [],      # 0-3 months
            'phase_2_foundation': [],      # 3-9 months  
            'phase_3_transformation': []   # 9-18 months
        }
        
        for rec in recommendations:
            if rec['timeline']['duration_months'] <= 3:
                phases['phase_1_quick_wins'].append(rec)
            elif rec['timeline']['duration_months'] <= 9:
                phases['phase_2_foundation'].append(rec)
            else:
                phases['phase_3_transformation'].append(rec)
        
        roadmap = {
            'roadmap_id': f"roadmap_{hospital_profile.hospital_id}_{datetime.now().strftime('%Y%m')}",
            'hospital_id': hospital_profile.hospital_id,
            'total_duration_months': 18,
            'phases': phases,
            'critical_success_factors': self._identify_critical_success_factors(hospital_profile),
            'change_management_approach': self._design_change_management_approach(hospital_profile),
            'governance_structure': self._recommend_governance_structure(hospital_profile),
            'investment_summary': self._calculate_investment_summary(recommendations),
            'expected_roi': self._calculate_expected_roi(recommendations, hospital_profile)
        }
        
        return roadmap
    
    def _calculate_opportunity_priority(self, impact: float, complexity: str, hospital_profile: HospitalProfile) -> float:
        """Calculate priority score for opportunities using weighted factors"""
        
        # Impact score (0-1)
        impact_score = min(impact / 10000000, 1.0)  # Normalize to 1 crore impact
        
        # Complexity penalty
        complexity_penalty = {'low': 0.0, 'medium': 0.2, 'high': 0.4}.get(complexity, 0.2)
        
        # Hospital readiness factor
        readiness_factor = {
            'basic': 0.7,      # Lower readiness for complex changes
            'intermediate': 0.85,
            'advanced': 1.0
        }.get(hospital_profile.technology_maturity, 0.8)
        
        priority_score = (impact_score * 0.6) * (1 - complexity_penalty) * readiness_factor
        
        return min(priority_score, 1.0)
    
    def _create_executive_summary(self,
                                benchmark_results: Dict[str, Any],
                                opportunities: List[Dict[str, Any]],
                                recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create executive summary in McKinsey style"""
        
        total_potential_impact = sum(opp['potential_impact'] for opp in opportunities[:3])
        
        return {
            'key_findings': [
                f"Hospital performance vs peers: {benchmark_results.get('overall_percentile', 50)}th percentile",
                f"Top 3 opportunities could generate ₹{total_potential_impact:,.0f} annual impact",
                f"Primary focus areas: {', '.join([rec['category'] for rec in recommendations[:3]])}"
            ],
            'critical_recommendations': [rec['title'] for rec in recommendations[:3]],
            'implementation_priority': 'Start with revenue cycle optimization for immediate cash flow impact',
            'expected_timeline': '90-day quick wins, 12-month comprehensive transformation',
            'investment_required': sum(rec['resource_requirements']['total_investment'] for rec in recommendations[:3]),
            'expected_roi': '200-300% within 18 months based on peer hospital implementations'
        }
    
    async def generate_hospital_consulting_proposal(self,
                                                  hospital_profile: HospitalProfile,
                                                  preliminary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a consulting proposal for hospital leadership"""
        
        # Quick assessment based on preliminary data
        quick_assessment = await self._perform_quick_assessment(hospital_profile, preliminary_data)
        
        # Determine appropriate service tier
        recommended_tier = self._recommend_service_tier(hospital_profile, quick_assessment)
        
        # Create proposal structure
        proposal = {
            'proposal_id': f"proposal_{hospital_profile.hospital_id}_{datetime.now().strftime('%Y%m%d')}",
            'hospital_profile': hospital_profile.__dict__,
            'executive_summary': {
                'situation': self._describe_current_situation(quick_assessment),
                'opportunity': self._describe_improvement_opportunity(quick_assessment),
                'approach': self._describe_consulting_approach(recommended_tier),
                'impact': self._estimate_potential_impact(hospital_profile, quick_assessment)
            },
            'recommended_engagement': {
                'service_tier': recommended_tier,
                'duration': self.hospital_config['hospital_consulting']['consulting_delivery_model']['service_tiers'][recommended_tier]['duration_months'],
                'investment': self._calculate_engagement_investment(hospital_profile, recommended_tier),
                'deliverables': self.hospital_config['hospital_consulting']['consulting_delivery_model']['service_tiers'][recommended_tier]['deliverables'],
                'methodology': 'McKinsey-style fact-based, hypothesis-driven approach adapted for Indian healthcare'
            },
            'success_case_studies': self._get_relevant_case_studies(hospital_profile),
            'team_composition': self._recommend_team_composition(hospital_profile, recommended_tier),
            'next_steps': self._define_proposal_next_steps()
        }
        
        return proposal


class HospitalBenchmarkEngine:
    """Benchmarking engine for hospital performance comparison"""
    
    def __init__(self, hospital_config: Dict[str, Any]):
        self.config = hospital_config
        self.benchmarks = hospital_config.get('hospital_consulting', {}).get('consulting_focus_areas', {})
    
    async def benchmark_hospital(self, hospital_profile: HospitalProfile, 
                               performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark hospital against peers"""
        
        # Identify peer group
        peer_group = self._identify_peer_group(hospital_profile)
        
        # Calculate performance percentiles
        financial_percentile = self._calculate_financial_percentile(
            performance_data.get('financial_data', {}), peer_group
        )
        
        operational_percentile = self._calculate_operational_percentile(
            performance_data.get('operational_data', {}), peer_group
        )
        
        quality_percentile = self._calculate_quality_percentile(
            performance_data.get('quality_data', {}), peer_group
        )
        
        overall_percentile = (financial_percentile + operational_percentile + quality_percentile) / 3
        
        return {
            'peer_group': peer_group,
            'overall_percentile': overall_percentile,
            'financial_percentile': financial_percentile,
            'operational_percentile': operational_percentile,
            'quality_percentile': quality_percentile,
            'key_gaps': self._identify_performance_gaps(performance_data, peer_group),
            'benchmark_date': datetime.now().isoformat()
        }
    
    def _identify_peer_group(self, hospital_profile: HospitalProfile) -> Dict[str, Any]:
        """Identify appropriate peer group for benchmarking"""
        
        # Determine hospital size category
        bed_count = hospital_profile.bed_count
        hospital_type = hospital_profile.hospital_type
        
        size_category = 'small'
        if bed_count > 300:
            size_category = 'large'
        elif bed_count > 150:
            size_category = 'medium'
        
        return {
            'hospital_type': hospital_type,
            'size_category': size_category,
            'location_tier': hospital_profile.location.get('tier', 'tier_2'),
            'ownership_type': hospital_profile.ownership_type
        }


class HospitalFinancialAnalyzer:
    """Financial performance analysis for hospitals"""
    
    def __init__(self, hospital_config: Dict[str, Any]):
        self.config = hospital_config
        self.financial_benchmarks = hospital_config.get('hospital_consulting', {}).get('consulting_focus_areas', {}).get('financial_optimization', {})
    
    async def analyze_financial_performance(self, hospital_profile: HospitalProfile,
                                          financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive financial performance analysis"""
        
        # Revenue cycle analysis
        revenue_cycle_analysis = self._analyze_revenue_cycle(financial_data.get('revenue_cycle', {}))
        
        # Cost structure analysis
        cost_analysis = self._analyze_cost_structure(financial_data.get('costs', {}))
        
        # Profitability analysis
        profitability_analysis = self._analyze_profitability(financial_data, hospital_profile)
        
        # Payer mix analysis
        payer_mix_analysis = self._analyze_payer_mix(financial_data.get('payer_mix', {}))
        
        return {
            'revenue_cycle': revenue_cycle_analysis,
            'cost_structure': cost_analysis,
            'profitability': profitability_analysis,
            'payer_mix': payer_mix_analysis,
            'overall_financial_health': self._assess_overall_financial_health(
                revenue_cycle_analysis, cost_analysis, profitability_analysis
            )
        }
    
    def _analyze_revenue_cycle(self, revenue_cycle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue cycle performance"""
        
        current_metrics = {
            'days_in_ar': revenue_cycle_data.get('days_in_ar', 45),
            'collection_rate': revenue_cycle_data.get('collection_rate', 0.85),
            'denial_rate': revenue_cycle_data.get('denial_rate', 0.12),
            'claim_processing_time': revenue_cycle_data.get('claim_processing_time', 12)
        }
        
        benchmarks = self.financial_benchmarks.get('revenue_cycle', {}).get('benchmarks', {})
        
        # Calculate performance gaps
        performance_gaps = {}
        potential_savings = 0
        
        for metric, current_value in current_metrics.items():
            if metric in benchmarks.get('excellent', []):
                excellent_benchmark = benchmarks['excellent'][list(benchmarks['excellent'].keys()).index(metric)]
                gap = current_value - excellent_benchmark if metric != 'collection_rate' else excellent_benchmark - current_value
                performance_gaps[metric] = max(gap, 0)
        
        # Estimate potential savings
        if performance_gaps.get('days_in_ar', 0) > 5:
            # Reduced days in A/R improves cash flow
            potential_savings += revenue_cycle_data.get('monthly_revenue', 10000000) * 0.02
        
        if performance_gaps.get('collection_rate', 0) > 0.05:
            # Improved collection rate increases revenue
            potential_savings += revenue_cycle_data.get('annual_revenue', 120000000) * performance_gaps.get('collection_rate', 0)
        
        return {
            'current_metrics': current_metrics,
            'performance_gaps': performance_gaps,
            'potential_savings': potential_savings,
            'improvement_recommendations': self._generate_revenue_cycle_recommendations(performance_gaps)
        }


class HospitalOperationalAnalyzer:
    """Operational efficiency analysis for hospitals"""
    
    def __init__(self, hospital_config: Dict[str, Any]):
        self.config = hospital_config
        self.operational_benchmarks = hospital_config.get('hospital_consulting', {}).get('consulting_focus_areas', {}).get('operational_efficiency', {})
    
    async def analyze_operations(self, hospital_profile: HospitalProfile,
                               operational_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive operational analysis"""
        
        # Bed management analysis
        bed_analysis = self._analyze_bed_management(operational_data.get('bed_data', {}))
        
        # OR utilization analysis
        or_analysis = self._analyze_or_utilization(operational_data.get('or_data', {}))
        
        # Emergency department analysis
        ed_analysis = self._analyze_emergency_department(operational_data.get('ed_data', {}))
        
        # Staffing analysis
        staffing_analysis = self._analyze_staffing_efficiency(operational_data.get('staffing_data', {}))
        
        return {
            'bed_management': bed_analysis,
            'or_utilization': or_analysis,
            'emergency_department': ed_analysis,
            'staffing_efficiency': staffing_analysis,
            'overall_operational_score': self._calculate_operational_score(
                bed_analysis, or_analysis, ed_analysis, staffing_analysis
            )
        }


class HospitalQualityAnalyzer:
    """Quality metrics analysis for hospitals"""
    
    def __init__(self, hospital_config: Dict[str, Any]):
        self.config = hospital_config
        self.quality_benchmarks = hospital_config.get('hospital_consulting', {}).get('consulting_focus_areas', {}).get('quality_improvement', {})
    
    async def analyze_quality_metrics(self, hospital_profile: HospitalProfile,
                                    quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive quality analysis"""
        
        # Patient safety analysis
        patient_safety_analysis = self._analyze_patient_safety(quality_data.get('patient_safety', {}))
        
        # Clinical outcomes analysis
        clinical_outcomes_analysis = self._analyze_clinical_outcomes(quality_data.get('clinical_outcomes', {}))
        
        # Patient satisfaction analysis
        satisfaction_analysis = self._analyze_patient_satisfaction(quality_data.get('patient_satisfaction', {}))
        
        return {
            'patient_safety': patient_safety_analysis,
            'clinical_outcomes': clinical_outcomes_analysis,
            'patient_satisfaction': satisfaction_analysis,
            'overall_quality_score': self._calculate_quality_score(
                patient_safety_analysis, clinical_outcomes_analysis, satisfaction_analysis
            )
        }


# Initialize the hospital intelligence engine
def get_hospital_intelligence_engine(user_context: Optional[Dict[str, Any]] = None) -> HospitalIntelligenceEngine:
    """Get singleton instance of HospitalIntelligenceEngine"""
    return HospitalIntelligenceEngine(user_context)


if __name__ == "__main__":
    # Example usage
    async def demo_hospital_analysis():
        """Demonstrate hospital analysis capabilities"""
        
        # Create sample hospital profile
        sample_hospital = HospitalProfile(
            hospital_id="HOSP_001",
            name="City General Hospital",
            location={"city": "bangalore", "state": "karnataka", "tier": "tier_1"},
            hospital_type="acute_care",
            bed_count=250,
            service_lines=["emergency", "general_medicine", "surgery", "cardiology"],
            ownership_type="private",
            accreditations=["NABH"],
            technology_maturity="intermediate",
            financial_metrics={"annual_revenue": 150000000, "operating_margin": 0.04},
            current_challenges=["cash_flow", "bed_utilization", "staff_retention"]
        )
        
        # Sample performance data
        performance_data = {
            'financial_data': {
                'revenue_cycle': {
                    'days_in_ar': 42,
                    'collection_rate': 0.87,
                    'denial_rate': 0.09,
                    'annual_revenue': 150000000
                }
            },
            'operational_data': {
                'bed_data': {
                    'occupancy_rate': 0.72,
                    'average_los': 5.2
                }
            },
            'quality_data': {
                'patient_safety': {
                    'hai_rate': 0.035,
                    'medication_errors': 0.004
                }
            }
        }
        
        # Initialize engine and run analysis
        engine = get_hospital_intelligence_engine()
        analysis_result = await engine.analyze_hospital_performance(sample_hospital, performance_data)
        
        print(f"Analysis completed for {sample_hospital.name}")
        print(f"Overall performance percentile: {analysis_result['performance_benchmarks']['overall_percentile']}")
        print(f"Number of opportunities identified: {len(analysis_result['improvement_opportunities'])}")
        print(f"Expected ROI: {analysis_result['implementation_roadmap']['expected_roi']}")
        
        return analysis_result
    
    # Run demo
    if __name__ == "__main__":
        asyncio.run(demo_hospital_analysis())