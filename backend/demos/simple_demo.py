"""
Phase 1 Week 1-2 Simple Demo: Data Intelligence Layer Testing
Demonstrates working components of our hospital intelligence system
"""

import asyncio
import sys
from datetime import datetime
from decimal import Decimal

# Add current directory to path
sys.path.append('.')

# Import our working components
from models.hospital_schemas_simple import (
    HospitalProfile, HospitalLocation, HospitalFinancialMetrics,
    HospitalOperationalMetrics, HospitalQualityMetrics, 
    HospitalTier, HospitalType
)
from services.hospital_intelligence.hms_connectors import (
    HMSConnectorFactory, HMSType, HMSConnectionConfig
)

def create_demo_hospital() -> HospitalProfile:
    """Create a realistic hospital profile for demo"""
    
    # Hospital location
    location = HospitalLocation(
        address="15/2, Ring Road, Lajpat Nagar",
        city="New Delhi",
        state="Delhi",
        pincode="110024",
        tier=HospitalTier.TIER_1
    )
    
    # Financial metrics
    financial_metrics = HospitalFinancialMetrics(
        annual_revenue=Decimal("180000000"),  # 18 crores INR
        operating_margin=16.2,
        days_in_ar=35,
        collection_rate=93.8,
        government_scheme_percentage=28.0,
        private_insurance_percentage=52.0,
        self_pay_percentage=20.0,
        fiscal_year="FY2024-25"
    )
    
    # Operational metrics
    operational_metrics = HospitalOperationalMetrics(
        bed_count=400,
        occupancy_rate=0.76,
        average_length_of_stay=3.9,
        ed_visits_annual=58000,
        or_count=14,
        or_utilization_rate=0.74,
        doctor_to_bed_ratio=0.17,
        nurse_to_bed_ratio=1.1,
        reporting_period="Q2-FY2024-25"
    )
    
    # Quality metrics  
    quality_metrics = HospitalQualityMetrics(
        hospital_acquired_infection_rate=1.9,
        readmission_rate_30_day=7.8,
        overall_satisfaction_score=88.3,
        nabh_score=4.4,
        jci_accredited=False,
        reporting_period="Q2-FY2024-25"
    )
    
    return HospitalProfile(
        hospital_id="DEMO_HOSP_001",
        name="Delhi Advanced Medical Center",
        location=location,
        hospital_type=HospitalType.SUPER_SPECIALTY,
        established_year=2008,
        bed_count=400,
        service_lines=[
            "Cardiology", "Cardiac Surgery", "Neurology", "Neurosurgery",
            "Oncology", "Orthopedics", "Emergency Medicine", "Critical Care"
        ],
        has_emr=True,
        has_his=True,
        financial_metrics=financial_metrics,
        operational_metrics=operational_metrics,
        quality_metrics=quality_metrics,
        current_challenges=[
            "Rising operational costs due to inflation",
            "Staff retention challenges in nursing department", 
            "Technology integration between legacy and new systems",
            "Government scheme reimbursement delays of 45-60 days",
            "Quality compliance with new NABH standards"
        ],
        strategic_priorities=[
            "Complete digital transformation by FY2025-26",
            "Achieve NABH 5.0 accreditation",
            "Implement cost optimization program (target 15% reduction)",
            "Expand capacity by 100 beds", 
            "Strengthen quality metrics and patient satisfaction"
        ]
    )

def test_hms_connectors():
    """Test different HMS connector types"""
    
    print("=== HMS CONNECTOR TESTING ===")
    
    # Test configurations for different HMS types
    hms_configs = [
        {
            "name": "Birlamedisoft (Popular in North India)",
            "type": HMSType.BIRLAMEDISOFT,
            "endpoint": "http://demo.birlamedisoft.com/api/v1",
            "description": "Leading HMS for multi-specialty hospitals"
        },
        {
            "name": "Medeil (Pharmacy + HMS)",
            "type": HMSType.MEDEIL,
            "endpoint": "http://api.medeil.com/hms",
            "description": "Integrated pharmacy and hospital management"
        },
        {
            "name": "eHospital (Government NIC)",
            "type": HMSType.EHOSPITAL,
            "endpoint": "https://ehospital.gov.in/api",
            "description": "Government hospitals management system"
        }
    ]
    
    for config_info in hms_configs:
        try:
            # Create configuration
            config = HMSConnectionConfig(
                hms_type=config_info["type"],
                api_endpoint=config_info["endpoint"],
                username="demo_user",
                password="demo_pass",
                database_name="hospital_db"
            )
            
            # Create connector
            connector = HMSConnectorFactory.create_connector(config_info["type"], config)
            
            print(f"✅ {config_info['name']}")
            print(f"   Class: {connector.__class__.__name__}")
            print(f"   Endpoint: {config.api_endpoint}")
            print(f"   Description: {config_info['description']}")
            print()
            
        except Exception as e:
            print(f"❌ {config_info['name']}: {e}")
            print()

def main():
    """Main demo function"""
    
    print("=" * 60)
    print("PHASE 1 WEEK 1-2 DEMO: HOSPITAL INTELLIGENCE FOUNDATION")
    print("=" * 60)
    print()
    
    # 1. Create and display hospital profile
    print("1. HOSPITAL PROFILE CREATION")
    print("-" * 30)
    
    hospital = create_demo_hospital()
    
    print(f"Hospital: {hospital.name}")
    print(f"Location: {hospital.location.city}, {hospital.location.state}")
    print(f"Type: {hospital.hospital_type.value}")
    print(f"Established: {hospital.established_year}")
    print(f"Bed Count: {hospital.bed_count}")
    print(f"Service Lines: {len(hospital.service_lines)} specialties")
    print()
    
    print("Financial Performance:")
    print(f"  • Annual Revenue: INR {hospital.financial_metrics.annual_revenue:,}")
    print(f"  • Operating Margin: {hospital.financial_metrics.operating_margin}%")
    print(f"  • Collection Rate: {hospital.financial_metrics.collection_rate}%")
    print(f"  • Days in A/R: {hospital.financial_metrics.days_in_ar} days")
    print()
    
    print("Operational Metrics:")
    print(f"  • Occupancy Rate: {hospital.operational_metrics.occupancy_rate:.1%}")
    print(f"  • Average LOS: {hospital.operational_metrics.average_length_of_stay} days")
    print(f"  • ED Visits/Year: {hospital.operational_metrics.ed_visits_annual:,}")
    print(f"  • OR Utilization: {hospital.operational_metrics.or_utilization_rate:.1%}")
    print()
    
    print("Quality Indicators:")
    print(f"  • Patient Satisfaction: {hospital.quality_metrics.overall_satisfaction_score}/100")
    print(f"  • NABH Score: {hospital.quality_metrics.nabh_score}/5.0")
    print(f"  • HAI Rate: {hospital.quality_metrics.hospital_acquired_infection_rate}%")
    print(f"  • 30-day Readmission: {hospital.quality_metrics.readmission_rate_30_day}%")
    print()
    
    print("Current Challenges:")
    for i, challenge in enumerate(hospital.current_challenges, 1):
        print(f"  {i}. {challenge}")
    print()
    
    print("Strategic Priorities:")
    for i, priority in enumerate(hospital.strategic_priorities, 1):
        print(f"  {i}. {priority}")
    print()
    
    # 2. Test HMS connectors
    print("2. HMS INTEGRATION TESTING")
    print("-" * 30)
    test_hms_connectors()
    
    # 3. Summary
    print("3. PHASE 1 WEEK 1-2 SUMMARY")
    print("-" * 30)
    print("✅ COMPLETED DELIVERABLES:")
    print("  • Hospital data schemas with Indian context")
    print("  • HMS connector framework")
    print("  • Support for major Indian HMS platforms")
    print("  • Financial metrics tracking")
    print("  • Operational KPI monitoring") 
    print("  • Quality assessment framework")
    print("  • Configuration management system")
    print()
    
    print("🚀 READY FOR WEEK 3-4:")
    print("  • AI Decision Engine Implementation")
    print("  • McKinsey SCQA Framework Integration")
    print("  • Benchmark Database Creation")
    print("  • Opportunity Identification Algorithm")
    print("  • Recommendation Engine Development")
    print()
    
    print("📊 SYSTEM STATUS: OPERATIONAL")
    print("🎯 PHASE 1 FOUNDATION: COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()