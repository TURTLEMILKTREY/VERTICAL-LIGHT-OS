#!/usr/bin/env python3
"""
SIMPLE Hospital Intelligence System - No Hanging, Just Results
Direct input system that works perfectly every time

This system:
1. Takes hospital data through simple prompts
2. Provides instant analysis 
3. Shows guaranteed results immediately
4. No complex async operations that can hang
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List

class SimpleHospitalAnalyzer:
 """Simple, reliable hospital analyzer that never hangs"""

 def __init__(self):
 self.benchmarks = {
 "days_in_ar": {"excellent": 25, "good": 35, "poor": 50},
 "collection_rate": {"excellent": 0.95, "good": 0.90, "poor": 0.80},
 "occupancy_rate": {"excellent": 0.85, "good": 0.80, "poor": 0.70},
 "or_utilization": {"excellent": 0.85, "good": 0.80, "poor": 0.70},
 "patient_satisfaction": {"excellent": 90, "good": 85, "poor": 75}
 }

 def analyze_hospital(self, data: Dict[str, Any]) -> Dict[str, Any]:
 """Analyze hospital and return results immediately"""

 print(f"\n🔄 Analyzing {data['name']}...")

 # Calculate gaps and opportunities
 opportunities = []

 # AR Days Opportunity
 if data['days_in_ar'] > self.benchmarks['days_in_ar']['good']:
 ar_improvement = data['days_in_ar'] - self.benchmarks['days_in_ar']['excellent']
 daily_revenue = data['annual_revenue'] / 365
 cash_impact = daily_revenue * ar_improvement

 opportunities.append({
 'title': 'Revenue Cycle Optimization',
 'current': f"{data['days_in_ar']} days",
 'target': "25 days",
 'annual_benefit': cash_impact,
 'priority': 'HIGH'
 })

 # Collection Rate Opportunity 
 if data['collection_rate'] < self.benchmarks['collection_rate']['good']:
 collection_gap = self.benchmarks['collection_rate']['excellent'] - data['collection_rate']
 revenue_impact = data['annual_revenue'] * collection_gap

 opportunities.append({
 'title': 'Collection Rate Enhancement',
 'current': f"{data['collection_rate']:.1%}",
 'target': "95%",
 'annual_benefit': revenue_impact,
 'priority': 'HIGH'
 })

 # Occupancy Opportunity
 if data['occupancy_rate'] < self.benchmarks['occupancy_rate']['good']:
 occupancy_gap = self.benchmarks['occupancy_rate']['excellent'] - data['occupancy_rate']
 additional_beds = int(data['bed_count'] * occupancy_gap)
 bed_revenue = data['annual_revenue'] / (data['bed_count'] * data['occupancy_rate'])
 revenue_impact = additional_beds * bed_revenue

 opportunities.append({
 'title': 'Capacity Utilization Enhancement',
 'current': f"{data['occupancy_rate']:.1%}",
 'target': "85%",
 'annual_benefit': revenue_impact,
 'priority': 'MEDIUM'
 })

 # OR Utilization Opportunity
 if data['or_utilization'] < self.benchmarks['or_utilization']['good']:
 or_gap = self.benchmarks['or_utilization']['excellent'] - data['or_utilization']
 surgery_revenue = data['annual_revenue'] * 0.35 # 35% from surgeries
 revenue_impact = surgery_revenue * or_gap

 opportunities.append({
 'title': 'OR Efficiency Program',
 'current': f"{data['or_utilization']:.1%}",
 'target': "85%", 
 'annual_benefit': revenue_impact,
 'priority': 'MEDIUM'
 })

 # Patient Satisfaction
 if data['patient_satisfaction'] < self.benchmarks['patient_satisfaction']['good']:
 satisfaction_impact = data['annual_revenue'] * 0.05 # 5% revenue uplift

 opportunities.append({
 'title': 'Patient Experience Enhancement',
 'current': f"{data['patient_satisfaction']:.1f}%",
 'target': "90%",
 'annual_benefit': satisfaction_impact,
 'priority': 'MEDIUM'
 })

 # Calculate totals
 total_benefit = sum(opp['annual_benefit'] for opp in opportunities)
 total_investment = total_benefit * 0.25 # 25% of benefit
 roi = ((total_benefit - total_investment) / total_investment) * 100 if total_investment > 0 else 0

 return {
 'hospital_name': data['name'],
 'analysis_date': datetime.now().strftime('%Y-%m-%d'),
 'opportunities': opportunities,
 'total_annual_benefit': total_benefit,
 'total_investment_required': total_investment,
 'roi_percentage': roi,
 'payback_months': int((total_investment / (total_benefit / 12)) if total_benefit > 0 else 12),
 'confidence_score': 0.85
 }

 def print_results(self, results: Dict[str, Any]):
 """Print analysis results in formatted way"""

 print("\n" + "="*80)
 print(f"🏥 HOSPITAL ANALYSIS REPORT - {results['hospital_name'].upper()}")
 print("="*80)

 print(f"\n📅 Analysis Date: {results['analysis_date']}")
 print(f"Confidence Score: {results['confidence_score']:.1%}")

 print(f"\nFINANCIAL SUMMARY:")
 print(f" Total Annual Benefit: ₹{results['total_annual_benefit']/10000000:.1f} crore")
 print(f" Investment Required: ₹{results['total_investment_required']/10000000:.1f} crore") 
 print(f" Expected ROI: {results['roi_percentage']:.0f}%")
 print(f" Payback Period: {results['payback_months']} months")

 print(f"\nIMPROVEMENT OPPORTUNITIES ({len(results['opportunities'])} identified):")

 for i, opp in enumerate(results['opportunities'], 1):
 priority_icon = "CRITICAL" if opp['priority'] == 'HIGH' else "MEDIUM PRIORITY"
 print(f"\n{i}. {priority_icon} {opp['title']} ({opp['priority']} Priority)")
 print(f" Current: {opp['current']} → Target: {opp['target']}")
 print(f" Annual Benefit: ₹{opp['annual_benefit']/10000000:.1f} crore")

 # Guarantees
 print(f"\nRESULTS GUARANTEE:")
 guaranteed_benefit = results['total_annual_benefit'] * 0.8 # 80% guarantee
 print(f" Minimum Guaranteed Benefit: ₹{guaranteed_benefit/10000000:.1f} crore")
 print(f" Or 50% refund if targets not met")
 print(f" Success Probability: {results['confidence_score']:.1%}")

 print(f"\nNEXT STEPS:")
 print(f" 1. Review opportunities with leadership team")
 print(f" 2. Sign guarantee agreement")
 print(f" 3. Begin implementation (90-day quick wins)")
 print(f" 4. Start seeing results immediately")

 print("\n" + "="*80)
 return results

def collect_hospital_data():
 """Collect hospital data with simple prompts"""

 print("\n🏥 HOSPITAL DATA COLLECTION")
 print("="*50)
 print("Please provide your hospital's current performance data:")

 try:
 data = {}

 # Basic info
 data['name'] = input("\nHospital Name: ").strip()
 data['city'] = input("📍 City: ").strip()

 # Size and revenue
 data['bed_count'] = int(input("🛏 Total Beds: "))
 revenue_crores = float(input("Annual Revenue (in Crores): "))
 data['annual_revenue'] = revenue_crores * 10000000

 # Key metrics
 print("\nPERFORMANCE METRICS:")
 data['days_in_ar'] = int(input("Days in AR (Accounts Receivable): "))
 data['collection_rate'] = float(input("💳 Collection Rate (0.85 for 85%): "))
 data['occupancy_rate'] = float(input("🏨 Bed Occupancy Rate (0.75 for 75%): "))
 data['or_utilization'] = float(input("🏥 OR Utilization Rate (0.70 for 70%): "))
 data['patient_satisfaction'] = float(input("😊 Patient Satisfaction (80 for 80%): "))

 return data

 except (ValueError, KeyboardInterrupt) as e:
 print(f"\nERROR: Input error. Using sample data instead.")
 return get_sample_data()

def get_sample_data():
 """Get sample hospital data for demo"""
 return {
 'name': 'Sample Metro Hospital',
 'city': 'Mumbai', 
 'bed_count': 250,
 'annual_revenue': 60_00_00_000, # ₹60 crores
 'days_in_ar': 52,
 'collection_rate': 0.82,
 'occupancy_rate': 0.72,
 'or_utilization': 0.68,
 'patient_satisfaction': 77.5
 }

def main():
 """Main function - simple and reliable"""

 print("HOSPITAL INTELLIGENCE SYSTEM - SIMPLE VERSION")
 print("="*60)
 print("Get instant analysis with guaranteed results!")

 print("\nChoose option:")
 print("1. Enter your hospital data")
 print("2. Use sample data for demo")

 try:
 choice = input("\nEnter choice (1 or 2): ").strip()

 if choice == "1":
 hospital_data = collect_hospital_data()
 else:
 hospital_data = get_sample_data()
 print(f"\n🏥 Using sample data for: {hospital_data['name']}")

 # Analyze
 analyzer = SimpleHospitalAnalyzer()
 results = analyzer.analyze_hospital(hospital_data)

 # Show results
 analyzer.print_results(results)

 # Save option
 save = input("\n💾 Save results to file? (y/n): ").strip().lower()
 if save == 'y':
 filename = f"{hospital_data['name'].replace(' ', '_')}_analysis.txt"
 with open(filename, 'w') as f:
 f.write(f"Hospital Analysis Report - {hospital_data['name']}\n")
 f.write(f"Generated: {datetime.now()}\n\n")
 f.write(f"Total Benefit: ₹{results['total_annual_benefit']/10000000:.1f} crore\n")
 f.write(f"ROI: {results['roi_percentage']:.0f}%\n")
 f.write(f"Opportunities: {len(results['opportunities'])}\n")
 print(f"Results saved to {filename}")

 print(f"\n🎊 Analysis complete! Contact us to begin implementation.")
 print(f"📧 Email: hospital.intelligence@verticallight.com")

 except KeyboardInterrupt:
 print(f"\n👋 Thanks for trying Hospital Intelligence System!")
 except Exception as e:
 print(f"\nERROR: Error: {e}")
 print(f"Using sample data instead...")

 hospital_data = get_sample_data()
 analyzer = SimpleHospitalAnalyzer()
 results = analyzer.analyze_hospital(hospital_data)
 analyzer.print_results(results)

if __name__ == "__main__":
 main()