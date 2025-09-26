#!/usr/bin/env python3
"""
Hospital Intelligence Engine - Complete Demo
Demonstrates AI-powered consulting for Indian hospitals

This script shows the complete workflow:
1. Hospital profile creation with Indian market context
2. Comprehensive performance analysis
3. McKinsey-style strategic recommendations 
4. Consulting proposal generation
5. ROI calculation and business case

Perfect for demonstrating to potential hospital clients.
"""

import asyncio
import json
from datetime import datetime, date
from decimal import Decimal

# Setup paths for module imports
import os
import sys
backend_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, backend_path)

from models.hospital_schemas_simple import *
from services.hospital_intelligence_engine import HospitalIntelligenceEngine

def create_demo_hospital() -> HospitalProfile:
 """Create a realistic demo hospital profile"""

 print("🏥 Creating Demo Hospital Profile...")

 # Apollo-style hospital in Tier-2 city
 location = HospitalLocation(
 address="MG Road, Koramangala",
 city="Bangalore",
 state="Karnataka",
 pincode="560034",
 tier=HospitalTier.TIER_1
 )

 # Financial metrics showing improvement opportunities
 financial_metrics = HospitalFinancialMetrics(
 annual_revenue=Decimal("1200000000"), # ₹120 Crores
 operating_margin=0.09, # 9% - could be better
 ebitda_margin=0.14,
 debt_to_equity=0.8,
 days_in_ar=48, # High - clear opportunity
 collection_rate=0.84, # Low - needs improvement
 government_scheme_percentage=0.30,
 private_insurance_percentage=0.35,
 self_pay_percentage=0.35, # Balanced payer mix
 fiscal_year="FY2024-25"
 )

 # Operational metrics with efficiency gaps
 operational_metrics = HospitalOperationalMetrics(
 bed_count=350,
 occupancy_rate=0.74, # Below optimal
 average_length_of_stay=3.8,
 bed_turnover_rate=71,
 ed_visits_annual=42000,
 door_to_doc_time_minutes=22,
 or_count=12,
 or_utilization_rate=0.69, # Room for improvement
 doctor_to_bed_ratio=0.14,
 nurse_to_bed_ratio=0.9,
 reporting_period="Q3 FY2024-25"
 )

 # Quality metrics with mixed performance
 quality_metrics = HospitalQualityMetrics(
 hospital_acquired_infection_rate=0.028,
 medication_error_rate=0.015,
 mortality_rate=0.019,
 readmission_rate_30_day=0.088,
 overall_satisfaction_score=81.2, # Good but improvable
 nabh_score=780, # NABH accredited
 jci_accredited=False,
 reporting_period="Q3 FY2024-25"
 )

 # Key stakeholders
 stakeholders = [
 HospitalStakeholder(
 name="Dr. Vikram Rathi",
 designation="Chief Executive Officer",
 role_in_project="Executive Sponsor",
 influence_level="high",
 support_level="champion",
 decision_authority=["strategic_decisions", "budget_approval"]
 ),
 HospitalStakeholder(
 name="Ms. Anita Desai", 
 designation="Chief Financial Officer",
 role_in_project="Financial Lead",
 influence_level="high",
 support_level="supporter",
 decision_authority=["financial_planning", "ROI_validation"]
 ),
 HospitalStakeholder(
 name="Dr. Rajesh Kumar",
 designation="Chief Medical Officer",
 role_in_project="Clinical Champion",
 influence_level="high",
 support_level="supporter",
 decision_authority=["clinical_protocols", "quality_initiatives"]
 )
 ]

 # Complete hospital profile
 hospital = HospitalProfile(
 hospital_id="DEMO_BLR_001",
 name="HealthFirst Multispecialty Hospital",
 location=location,
 hospital_type=HospitalType.SUPER_SPECIALTY,
 established_year=2012,
 bed_count=350,
 service_lines=[
 "Cardiology", "Cardiac Surgery", "Oncology", "Neurology",
 "Orthopedics", "Gastroenterology", "Critical Care",
 "Emergency Medicine", "General Surgery", "Pediatrics",
 "Obstetrics & Gynecology", "Radiology", "Pathology"
 ],
 has_emr=True,
 has_his=True,
 financial_metrics=financial_metrics,
 operational_metrics=operational_metrics,
 quality_metrics=quality_metrics,
 current_challenges=[
 "Revenue cycle inefficiencies leading to extended AR days",
 "Suboptimal bed and OR utilization during weekdays",
 "Patient satisfaction scores trailing top-tier hospitals",
 "Manual processes causing operational bottlenecks",
 "Need for advanced analytics and AI integration"
 ],
 strategic_priorities=[
 "Achieve top-quartile financial performance",
 "Optimize capacity utilization across all departments",
 "Enhance patient experience and satisfaction scores",
 "Implement AI-driven operational excellence",
 "Expand specialist services and market share"
 ],
 key_stakeholders=stakeholders
 )

 print(f"Demo Hospital Created: {hospital.name}")
 print(f" 📍 Location: {hospital.location.city}, {hospital.location.state}")
 print(f" 🏨 Type: {hospital.hospital_type.value} | Beds: {hospital.bed_count}")
 print(f" Revenue: ₹{hospital.financial_metrics.annual_revenue:,}")
 print(f" Occupancy: {hospital.operational_metrics.occupancy_rate:.1%}")

 return hospital

async def run_complete_analysis(hospital: HospitalProfile):
 """Run complete hospital analysis and generate recommendations"""

 print("\n" + "="*80)
 print("HOSPITAL INTELLIGENCE ENGINE - COMPREHENSIVE ANALYSIS")
 print("="*80)

 # Initialize the AI engine
 print("Initializing Hospital Intelligence Engine...")
 engine = HospitalIntelligenceEngine()
 print("Engine initialized successfully")

 # Create analysis request
 print("\nPreparing Analysis Request...")
 analysis_request = HospitalAnalysisRequest(
 hospital_profile=hospital,
 analysis_scope=[
 ConsultingFocus.FINANCIAL_OPTIMIZATION,
 ConsultingFocus.OPERATIONAL_EFFICIENCY,
 ConsultingFocus.QUALITY_IMPROVEMENT,
 ConsultingFocus.TECHNOLOGY_OPTIMIZATION
 ],
 requested_deliverables=[
 "Executive Summary with Key Findings",
 "Performance Benchmarking vs Peers",
 "Strategic Recommendations (McKinsey SCQA)",
 "Implementation Roadmap",
 "ROI Analysis and Business Case"
 ]
 )

 # Run comprehensive analysis
 print("Running Comprehensive Analysis...")
 print(" Analyzing financial performance...")
 print(" Evaluating operational efficiency...")
 print(" Assessing quality metrics...")
 print(" Benchmarking against peer hospitals...")
 print(" Identifying improvement opportunities...")

 analysis_response = await engine.analyze_hospital_performance(analysis_request)

 print("Analysis Complete!")
 print(f" Confidence Score: {analysis_response.confidence_score:.1%}")
 print(f" Opportunities Identified: {len(analysis_response.opportunities)}")
 print(f" Strategic Recommendations: {len(analysis_response.recommendations)}")

 return analysis_response

def display_executive_summary(analysis: HospitalAnalysisResponse):
 """Display executive summary in business format"""

 print("\n" + "="*80)
 print("EXECUTIVE SUMMARY - KEY FINDINGS")
 print("="*80)

 summary = analysis.executive_summary

 print("🏥 HOSPITAL OVERVIEW")
 print("-" * 40)
 overview = summary['hospital_overview']
 print(f"Hospital: {overview['name']}")
 print(f"Location: {overview['location']}")
 print(f"Type: {overview['type']} | Beds: {overview['beds']}")
 print(f"Annual Revenue: ₹{overview['annual_revenue']:,.0f}")

 print("\nPERFORMANCE BENCHMARKS")
 print("-" * 40)
 perf = summary['performance_summary']
 print(f"Overall Performance: {perf['overall_percentile']:.0f}th percentile")
 print(f"Financial Performance: {perf['financial_percentile']:.0f}th percentile")
 print(f"Operational Efficiency: {perf['operational_percentile']:.0f}th percentile")
 print(f"Quality Metrics: {perf['quality_percentile']:.0f}th percentile")

 print("\nKEY FINDINGS")
 print("-" * 40)
 findings = summary['key_findings']
 print(f"Total Improvement Opportunities: {findings['total_opportunities_identified']}")
 print(f"Annual Impact Potential: ₹{findings['total_annual_impact_potential']:,.0f}")
 print(f"High Priority Recommendations: {findings['high_priority_recommendations']}")
 print(f"Estimated ROI: {findings['estimated_roi']:.1f}%")

 print("\nTOP STRATEGIC PRIORITIES")
 print("-" * 40)
 for i, priority in enumerate(summary['top_priorities'], 1):
 print(f"{i}. {priority['title']}")
 print(f" Category: {priority['category']}")
 print(f" Expected Benefit: ₹{priority['expected_benefit']:,.0f}")
 print(f" Payback: {priority['payback_months']} months")
 print()

def display_opportunities(analysis: HospitalAnalysisResponse):
 """Display improvement opportunities with impact analysis"""

 print("\n" + "="*80)
 print("IMPROVEMENT OPPORTUNITIES - IMPACT ANALYSIS")
 print("="*80)

 total_impact = sum(opp.potential_annual_impact for opp in analysis.opportunities)

 print(f"Total Annual Impact Potential: ₹{total_impact:,.0f}")
 print(f"Number of Opportunities: {len(analysis.opportunities)}")
 print()

 for i, opp in enumerate(analysis.opportunities, 1):
 print(f"OPPORTUNITY {i}: {opp.title}")
 print(f" Category: {opp.category.value}")
 print(f" Description: {opp.description}")
 print(f" Annual Impact: ₹{opp.potential_annual_impact:,}")
 print(f" Implementation: {opp.estimated_timeline_months} months | {opp.implementation_complexity} complexity")
 print(f" Confidence: {opp.confidence_level:.1%} | Priority Score: {opp.priority_score:.2f}")
 print("-" * 60)

def display_recommendations(analysis: HospitalAnalysisResponse):
 """Display McKinsey SCQA recommendations"""

 print("\n" + "="*80)
 print("STRATEGIC RECOMMENDATIONS - McKINSEY SCQA FRAMEWORK")
 print("="*80)

 for i, rec in enumerate(analysis.recommendations, 1):
 print(f"\nRECOMMENDATION {i}: {rec.title}")
 print(f"Priority: {rec.priority.upper()} | Category: {rec.category.value}")
 print()

 print("📍 SITUATION:")
 print(f" {rec.situation}")
 print()

 print("WARNING: COMPLICATION:")
 print(f" {rec.complication}")
 print()

 print("❓ QUESTION:")
 print(f" {rec.question}")
 print()

 print("ANSWER (Recommendation):")
 print(f" {rec.answer}")
 print()

 print("💵 FINANCIAL IMPACT:")
 print(f" Investment Required: ₹{rec.investment_required:,}")
 print(f" Expected Annual Benefit: ₹{rec.expected_annual_benefit:,}")
 print(f" Payback Period: {rec.payback_period_months} months")
 print(f" ROI: {(float(rec.expected_annual_benefit)/float(rec.investment_required)*100):.1f}%")

 print("\n" + "="*60)

async def generate_proposal(hospital: HospitalProfile, analysis: HospitalAnalysisResponse):
 """Generate consulting proposal"""

 print("\n" + "="*80)
 print("📄 GENERATING McKINSEY-STYLE CONSULTING PROPOSAL")
 print("="*80)

 engine = HospitalIntelligenceEngine()

 print("✍ Creating comprehensive proposal...")
 proposal = await engine.generate_consulting_proposal(
 hospital_profile=hospital,
 analysis_response=analysis,
 desired_service_tier=ServiceTier.STANDARD
 )

 print(f"Proposal Generated: {proposal.proposal_id}")

 print("\nPROPOSAL SUMMARY")
 print("-" * 40)
 print(f"Service Tier: {proposal.recommended_service_tier.value}")
 print(f"Engagement Duration: {proposal.engagement_duration_months} months")
 print(f"Total Investment: ₹{proposal.total_investment:,}")
 print(f"Expected ROI: {proposal.expected_roi}%")
 print(f"Payback Period: {proposal.payback_period_months} months")

 print("\nEXECUTIVE SUMMARY")
 print("-" * 40)
 print(proposal.executive_summary.strip())

 print("\nPROPOSED APPROACH")
 print("-" * 40)
 print(proposal.proposed_approach.strip())

 print("\n📦 KEY DELIVERABLES")
 print("-" * 40)
 for deliverable in proposal.key_deliverables:
 print(f"• {deliverable}")

 print("\nPRICING STRUCTURE")
 print("-" * 40)
 pricing = proposal.pricing_structure
 print(f"Total Engagement Fee: ₹{pricing['total_engagement_fee']:,}")
 print(f"Monthly Professional Fees: ₹{pricing['monthly_professional_fees']:,}")
 print(f"Diagnostic Phase (30%): ₹{pricing['diagnostic_phase']:,}")
 print(f"Implementation Phase (60%): ₹{pricing['implementation_phase']:,}")
 print(f"Capability Building (10%): ₹{pricing['capability_building']:,}")

 print(f"\n💳 PAYMENT TERMS")
 print("-" * 40)
 print(proposal.payment_terms)

 return proposal

def display_next_steps(analysis: HospitalAnalysisResponse):
 """Display recommended next steps"""

 print("\n" + "="*80)
 print("RECOMMENDED NEXT STEPS")
 print("="*80)

 for i, step in enumerate(analysis.next_steps, 1):
 print(f"{i}. {step}")

 print("\n📞 TO PROCEED:")
 print("• Schedule stakeholder presentation of findings")
 print("• Discuss proposal terms and engagement timeline")
 print("• Begin detailed diagnostic phase")
 print("• Set up project governance structure")

async def main():
 """Main demo function"""

 print("🇮🇳 HOSPITAL INTELLIGENCE ENGINE - COMPLETE DEMO")
 print("AI-Powered Consulting for Indian Healthcare Market")
 print("Powered by VERTICAL-LIGHT-OS")
 print()

 try:
 # Create demo hospital
 hospital = create_demo_hospital()

 # Run comprehensive analysis
 analysis = await run_complete_analysis(hospital)

 # Display results
 display_executive_summary(analysis)
 display_opportunities(analysis)
 display_recommendations(analysis)

 # Generate proposal
 proposal = await generate_proposal(hospital, analysis)

 # Display next steps
 display_next_steps(analysis)

 print("\n" + "="*80)
 print("DEMO COMPLETED SUCCESSFULLY!")
 print("Hospital Intelligence Engine is fully operational")
 print("McKinsey-style analysis and recommendations generated")
 print("Comprehensive consulting proposal created")
 print("Ready for production deployment")
 print("="*80)

 # Summary statistics
 total_opportunities = len(analysis.opportunities)
 total_impact = sum(opp.potential_annual_impact for opp in analysis.opportunities)

 print(f"\nFINAL SUMMARY:")
 print(f"Hospital: {hospital.name}")
 print(f"Opportunities Identified: {total_opportunities}")
 print(f"Total Annual Impact: ₹{total_impact:,.0f}")
 print(f"Consulting Investment: ₹{proposal.total_investment:,}")
 print(f"Expected ROI: {proposal.expected_roi}%")
 print(f"Payback Period: {proposal.payback_period_months} months")

 return {
 "hospital": hospital,
 "analysis": analysis,
 "proposal": proposal,
 "status": "SUCCESS"
 }

 except Exception as e:
 print(f"\nERROR: Demo failed with error: {e}")
 import traceback
 print(traceback.format_exc())
 return {"status": "FAILED", "error": str(e)}

if __name__ == "__main__":
 """Run the complete demo"""
 result = asyncio.run(main())

 if result["status"] == "SUCCESS":
 print(f"\n🎊 Hospital Intelligence Engine Demo Completed Successfully!")
 print("You now have a fully functional AI-powered hospital consulting system.")
 else:
 print(f"\n💥 Demo failed: {result.get('error', 'Unknown error')}")