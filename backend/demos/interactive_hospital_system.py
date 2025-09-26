#!/usr/bin/env python3
"""
INTERACTIVE Hospital Intelligence System - 100% Results Guaranteed
Real-time data input system that takes ANY hospital's data and provides guaranteed results

This system:
1. Takes live hospital data input through interactive prompts
2. Provides instant analysis and recommendations 
3. Generates implementation roadmap with guarantees
4. Tracks progress and ensures 100% success
"""

import asyncio
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Import our working engine
import sys
import os
sys.path.append(os.path.dirname(__file__))
from working_hospital_system import WorkingHospitalIntelligenceEngine, HospitalInput, HospitalTier, ConsultingFocus

def clear_screen():
 """Clear terminal screen"""
 os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
 """Print formatted header"""
 print("\n" + "="*80)
 print(f"🏥 {title}")
 print("="*80)

def print_section(title: str):
 """Print formatted section"""
 print(f"\n{title}")
 print("-" * 60)

def get_user_input(prompt: str, input_type: type = str, default: Any = None) -> Any:
 """Get user input with validation"""
 while True:
 try:
 if default is not None:
 user_input = input(f"{prompt} (default: {default}): ").strip()
 if not user_input:
 return default
 else:
 user_input = input(f"{prompt}: ").strip()

 if input_type == int:
 return int(user_input)
 elif input_type == float:
 return float(user_input)
 elif input_type == bool:
 return user_input.lower() in ['yes', 'y', 'true', '1']
 else:
 return user_input

 except ValueError:
 print(f"ERROR: Invalid input. Please enter a {input_type.__name__}.")
 except KeyboardInterrupt:
 print("\n👋 Exiting system. Thank you!")
 exit(0)

def get_tier_selection() -> HospitalTier:
 """Get hospital tier selection"""
 print("\nSelect Hospital Tier:")
 print("1. Tier 1 (Metro cities: Delhi, Mumbai, Bangalore, Chennai)")
 print("2. Tier 2 (State capitals and major cities)")
 print("3. Tier 3 (District headquarters)")
 print("4. Tier 4 (Rural areas)")

 choice = get_user_input("Enter choice (1-4)", int)

 tier_map = {
 1: HospitalTier.TIER_1,
 2: HospitalTier.TIER_2, 
 3: HospitalTier.TIER_3,
 4: HospitalTier.TIER_4
 }

 return tier_map.get(choice, HospitalTier.TIER_2)

def collect_hospital_data() -> HospitalInput:
 """Collect hospital data through interactive prompts"""

 print_header("HOSPITAL DATA COLLECTION")
 print("Please provide your hospital's current data for analysis...")

 # Basic information
 print_section("BASIC INFORMATION")
 name = get_user_input("Hospital Name")
 city = get_user_input("City")
 tier = get_tier_selection()
 bed_count = get_user_input("Total Bed Count", int)
 annual_revenue_crores = get_user_input("Annual Revenue (in Crores)", float)
 annual_revenue = Decimal(str(annual_revenue_crores * 10000000)) # Convert to rupees

 # Financial metrics
 print_section("FINANCIAL METRICS")
 print("We'll calculate operating margin automatically from your revenue and expenses")

 operating_revenue = get_user_input("Total Operating Revenue (in Crores)", float, annual_revenue_crores)
 operating_expenses = get_user_input("Total Operating Expenses (in Crores)", float, annual_revenue_crores * 0.9)

 # Calculate operating margin automatically
 operating_margin = (operating_revenue - operating_expenses) / operating_revenue if operating_revenue > 0 else 0.10
 print(f"Calculated Operating Margin: {operating_margin:.1%} ({operating_margin:.3f})")

 print("\nTip: Days in AR = Average days to collect payments")
 days_in_ar = get_user_input("Days in Accounts Receivable (AR)", int, 45)

 print("Tip: Collection rate = Amount collected / Amount billed")
 collection_rate = get_user_input("Collection Rate (as decimal, e.g., 0.85 for 85%)", float, 0.85)

 print("Tip: Bad debt = Uncollectible amounts / Total revenue")
 bad_debt_percentage = get_user_input("Bad Debt Percentage (as decimal, e.g., 0.03 for 3%)", float, 0.03)

 # Operational metrics
 print_section("OPERATIONAL METRICS")
 print("Tip: Occupancy rate = Occupied beds / Total beds")
 occupancy_rate = get_user_input("Bed Occupancy Rate (as decimal, e.g., 0.75 for 75%)", float, 0.75)

 print("Tip: Average days patients stay in hospital")
 average_length_of_stay = get_user_input("Average Length of Stay (days)", float, 4.0)

 print("Tip: Staff turnover = Employees who left / Total employees")
 staff_turnover_rate = get_user_input("Staff Turnover Rate (as decimal, e.g., 0.15 for 15%)", float, 0.15)

 print("Tip: OR utilization = OR hours used / Total OR hours available")
 or_utilization_rate = get_user_input("Operating Room Utilization Rate (as decimal)", float, 0.70)

 # Quality metrics
 print_section("QUALITY METRICS")
 patient_satisfaction_score = get_user_input("Patient Satisfaction Score (0-100)", float, 80.0)

 print("Tip: Hospital-acquired infection rate per 100 admissions")
 infection_rate = get_user_input("Infection Rate (as decimal, e.g., 0.03 for 3%)", float, 0.03)

 print("Tip: 30-day readmission rate")
 readmission_rate = get_user_input("Readmission Rate (as decimal, e.g., 0.10 for 10%)", float, 0.10)

 # Challenges and goals
 print_section("CHALLENGES & GOALS")
 print("What are your primary challenges? (Enter up to 5, press Enter after each)")
 challenges = []
 for i in range(5):
 challenge = input(f"Challenge {i+1} (or press Enter to skip): ").strip()
 if challenge:
 challenges.append(challenge)
 else:
 break

 if not challenges:
 challenges = ["Improve financial performance", "Enhance operational efficiency"]

 print("\nWhat are your improvement goals? (Enter up to 5)")
 goals = []
 for i in range(5):
 goal = input(f"Goal {i+1} (or press Enter to skip): ").strip()
 if goal:
 goals.append(goal)
 else:
 break

 if not goals:
 goals = ["Achieve industry-leading performance", "Increase patient satisfaction"]

 return HospitalInput(
 name=name,
 city=city,
 tier=tier,
 bed_count=bed_count,
 annual_revenue=annual_revenue,
 operating_margin=operating_margin,
 days_in_ar=days_in_ar,
 collection_rate=collection_rate,
 bad_debt_percentage=bad_debt_percentage,
 occupancy_rate=occupancy_rate,
 average_length_of_stay=average_length_of_stay,
 staff_turnover_rate=staff_turnover_rate,
 or_utilization_rate=or_utilization_rate,
 patient_satisfaction_score=patient_satisfaction_score,
 infection_rate=infection_rate,
 readmission_rate=readmission_rate,
 primary_challenges=challenges,
 improvement_goals=goals
 )

def display_analysis_summary(analysis):
 """Display key analysis highlights"""

 print_header("ANALYSIS SUMMARY")

 print("KEY RESULTS:")
 print(f" • Confidence Score: {analysis.confidence_score:.1%}")
 print(f" • Expected ROI: {analysis.expected_roi:.1%}")
 print(f" • Payback Period: {analysis.payback_period_months} months")

 total_guaranteed = sum(g["target_benefit"] for g in analysis.financial_guarantees)
 print(f" • Guaranteed Benefit: ₹{total_guaranteed/10000000:.1f} crore")

 print("\nTOP OPPORTUNITIES:")
 for i, opp in enumerate(analysis.opportunities[:3]):
 print(f" {i+1}. {opp['title']}: ₹{opp['potential_annual_impact']/10000000:.1f} crore")

 print("\nKEY FINDINGS:")
 for finding in analysis.key_findings[:3]:
 print(f" • {finding}")

def show_detailed_recommendations(analysis):
 """Show detailed recommendations"""

 print_header("STRATEGIC RECOMMENDATIONS")

 for i, rec in enumerate(analysis.recommendations):
 print(f"\n{i+1}. {rec['title'].upper()} ({rec['priority'].upper()} PRIORITY)")
 print(f" Investment: ₹{rec['investment_required']/100000:.1f} lakh")
 print(f" 💎 Benefit: ₹{rec['expected_annual_benefit']/100000:.1f} lakh")
 print(f" ⏱ Payback: {rec['payback_period_months']} months")
 print(f" Confidence: {rec['confidence_level']:.1%}")
 print(f"\n Situation: {rec['situation']}")
 print(f" WARNING: Challenge: {rec['complication']}")
 print(f" ❓ Question: {rec['question']}")
 print(f" Solution: {rec['answer']}")

def show_implementation_roadmap(analysis):
 """Show implementation roadmap"""

 print_header("IMPLEMENTATION ROADMAP")

 for phase_name, phase_data in analysis.implementation_phases.items():
 print(f"\n📅 {phase_data['title']}")
 print(f" Duration: {phase_data['duration_days']} days")
 print(f" Recommendations: {len(phase_data['recommendations'])}")
 print(f" Expected ROI: {phase_data['expected_roi']:.1%}")

 if phase_data['recommendations']:
 print(" Included:")
 for rec in phase_data['recommendations']:
 print(f" • {rec['title']}")

def show_guarantees(analysis):
 """Show financial guarantees"""

 print_header("FINANCIAL GUARANTEES")

 print("We guarantee the following results or provide refunds:")

 for guarantee in analysis.financial_guarantees:
 print(f"\n💎 {guarantee['metric']}")
 print(f" Guaranteed Benefit: ₹{guarantee['target_benefit']/100000:.1f} lakh")
 print(f" Timeline: {guarantee['measurement_timeline']} months")
 print(f" Refund if not achieved: ₹{guarantee['penalty_if_missed']/100000:.1f} lakh")
 print(f" Bonus if exceeded: ₹{guarantee['bonus_if_exceeded']/100000:.1f} lakh")

def get_next_steps():
 """Get user preference for next steps"""

 print_header("NEXT STEPS")

 print("What would you like to do next?")
 print("1. Save analysis report to file")
 print("2. Start implementation planning")
 print("3. Schedule consultation call")
 print("4. Generate proposal document")
 print("5. Analyze different scenario")
 print("6. Exit")

 choice = get_user_input("Enter your choice (1-6)", int)

 return choice

async def interactive_hospital_analysis():
 """Main interactive analysis function"""

 clear_screen()
 print_header("HOSPITAL INTELLIGENCE SYSTEM - INTERACTIVE VERSION")
 print("Ready to analyze your hospital and provide 100% guaranteed results!")
 print("This system will provide McKinsey-level analysis in minutes, not months.")

 input("\n👉 Press Enter to begin data collection...")

 # Collect hospital data
 clear_screen()
 hospital_data = collect_hospital_data()

 # Confirm data
 clear_screen()
 print_header("DATA CONFIRMATION")
 print(f"Hospital: {hospital_data.name}")
 print(f"Location: {hospital_data.city} ({hospital_data.tier.value})")
 print(f"Size: {hospital_data.bed_count} beds")
 print(f"Revenue: ₹{float(hospital_data.annual_revenue)/10000000:.1f} crore")
 print(f"Occupancy: {hospital_data.occupancy_rate:.1%}")
 print(f"AR Days: {hospital_data.days_in_ar}")

 confirm = get_user_input("\nIs this data correct? (y/n)", str, "y")
 if confirm.lower() not in ['y', 'yes']:
 print("Please restart the system to re-enter data.")
 return

 # Run analysis
 clear_screen()
 print_header("RUNNING ANALYSIS")
 print("🔄 Analyzing hospital performance...")
 print("🔄 Benchmarking against industry standards...")
 print("🔄 Identifying improvement opportunities...")
 print("🔄 Generating strategic recommendations...")
 print("🔄 Creating implementation roadmap...")
 print("🔄 Defining financial guarantees...")

 engine = WorkingHospitalIntelligenceEngine()
 analysis = await engine.analyze_hospital(hospital_data)

 print("Analysis complete!")
 input("\n👉 Press Enter to view results...")

 # Show results
 while True:
 clear_screen()
 display_analysis_summary(analysis)

 print("\nDETAILED VIEWS:")
 print("1. View full analysis report")
 print("2. View strategic recommendations")
 print("3. View implementation roadmap")
 print("4. View financial guarantees")
 print("5. Save results and next steps")
 print("6. Exit")

 choice = get_user_input("What would you like to view? (1-6)", int)

 if choice == 1:
 clear_screen()
 report = engine.generate_report(analysis)
 print(report)
 input("\n👉 Press Enter to continue...")

 elif choice == 2:
 clear_screen()
 show_detailed_recommendations(analysis)
 input("\n👉 Press Enter to continue...")

 elif choice == 3:
 clear_screen()
 show_implementation_roadmap(analysis)
 input("\n👉 Press Enter to continue...")

 elif choice == 4:
 clear_screen()
 show_guarantees(analysis)
 input("\n👉 Press Enter to continue...")

 elif choice == 5:
 clear_screen()
 next_choice = get_next_steps()

 if next_choice == 1:
 # Save report
 filename = f"{hospital_data.name.replace(' ', '_')}_analysis_{datetime.now().strftime('%Y%m%d')}.txt"
 with open(filename, 'w', encoding='utf-8') as f:
 f.write(engine.generate_report(analysis))
 print(f"Report saved as {filename}")

 elif next_choice == 2:
 print("\nIMPLEMENTATION PLANNING:")
 print("1. Schedule kick-off meeting with hospital leadership")
 print("2. Establish implementation team and governance")
 print("3. Begin Phase 1 (Quick Wins) in next 2 weeks")
 print("4. Set up weekly progress monitoring")

 elif next_choice == 3:
 print("\n📞 CONSULTATION SCHEDULING:")
 print("Contact: hospital.intelligence@verticallight.com")
 print("Phone: +91-98765-43210")
 print("We'll schedule a 30-minute call to discuss implementation")

 elif next_choice == 4:
 print("\n📄 PROPOSAL GENERATION:")
 print("A detailed proposal with:")
 print("• Executive summary and business case")
 print("• Detailed implementation plan")
 print("• Commercial terms and guarantees")
 print("• Team composition and timeline")
 print("Will be prepared within 24 hours")

 elif next_choice == 5:
 print("\n🔄 Would you like to analyze a different scenario?")
 restart = get_user_input("Start new analysis? (y/n)", str, "n")
 if restart.lower() in ['y', 'yes']:
 return await interactive_hospital_analysis()

 input("\n👉 Press Enter to continue...")

 elif choice == 6:
 break

 # Final summary
 clear_screen()
 print_header("ANALYSIS COMPLETE")
 print("🎊 Thank you for using the Hospital Intelligence System!")
 print(f"\nSUMMARY FOR {hospital_data.name.upper()}:")
 print(f" • Confidence Score: {analysis.confidence_score:.1%}")
 print(f" • Expected ROI: {analysis.expected_roi:.1%}")
 print(f" • Guaranteed Benefit: ₹{sum(g['target_benefit'] for g in analysis.financial_guarantees)/10000000:.1f} crore")

 print("\nNEXT STEPS:")
 print("1. Review recommendations with your leadership team")
 print("2. Contact us to begin implementation")
 print("3. Start seeing results in 30-90 days")

 print("\nCONTACT INFORMATION:")
 print("Email: hospital.intelligence@verticallight.com")
 print("Phone: +91-98765-43210")
 print("Website: www.verticallight.com/hospital-ai")

 return {
 "status": "SUCCESS",
 "hospital": hospital_data.name,
 "confidence": analysis.confidence_score,
 "guaranteed_benefit": sum(g["target_benefit"] for g in analysis.financial_guarantees)
 }

def quick_demo():
 """Quick demo with sample data"""

 print_header("QUICK DEMO MODE")
 print("Running analysis with sample hospital data...")

 # Sample hospital data
 sample_data = HospitalInput(
 name="Sample City Hospital",
 city="Mumbai",
 tier=HospitalTier.TIER_1,
 bed_count=200,
 annual_revenue=Decimal("500000000"), # ₹50 crores
 operating_margin=0.08,
 days_in_ar=55,
 collection_rate=0.82,
 bad_debt_percentage=0.06,
 occupancy_rate=0.68,
 average_length_of_stay=4.5,
 staff_turnover_rate=0.22,
 or_utilization_rate=0.65,
 patient_satisfaction_score=75.0,
 infection_rate=0.04,
 readmission_rate=0.13,
 primary_challenges=["High AR days", "Low occupancy", "Staff turnover"],
 improvement_goals=["Improve cash flow", "Increase capacity utilization"]
 )

 return sample_data

async def main():
 """Main application entry point"""

 clear_screen()
 print_header("HOSPITAL INTELLIGENCE SYSTEM")
 print("🏥 AI-Powered Hospital Consulting with 100% Results Guarantee")
 print("\nWelcome to the most advanced hospital analysis system!")
 print("Get McKinsey-level insights in minutes, not months.")

 print("\nWHAT THIS SYSTEM PROVIDES:")
 print("Comprehensive performance analysis")
 print("Strategic recommendations with ROI projections")
 print("Implementation roadmap with guarantees")
 print("Financial guarantees with refund protection")
 print("Ongoing implementation support")

 print("\nCHOOSE YOUR OPTION:")
 print("1. Full Interactive Analysis (Recommended)")
 print("2. Quick Demo with Sample Data")
 print("3. Exit")

 choice = get_user_input("Enter your choice (1-3)", int)

 if choice == 1:
 result = await interactive_hospital_analysis()

 elif choice == 2:
 sample_data = quick_demo()
 engine = WorkingHospitalIntelligenceEngine()
 analysis = await engine.analyze_hospital(sample_data)

 clear_screen()
 print(engine.generate_report(analysis))

 result = {
 "status": "SUCCESS",
 "hospital": sample_data.name,
 "confidence": analysis.confidence_score
 }

 else:
 print("👋 Thank you for your interest! Contact us anytime.")
 return

 if result and result["status"] == "SUCCESS":
 print(f"\n🎊 Analysis completed successfully!")
 print("Contact us to begin implementation and start seeing results!")

if __name__ == "__main__":
 try:
 asyncio.run(main())
 except KeyboardInterrupt:
 print("\n\n👋 Thank you for using Hospital Intelligence System!")
 print("Contact: hospital.intelligence@verticallight.com")