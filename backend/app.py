#!/usr/bin/env python3

"""
VERTICAL-LIGHT-OS Hospital Intelligence Platform
==============================================

Main application entry point for the hospital intelligence system.
Clean, scalable architecture with proper separation of concerns.

Production-ready system with:
- Clean project structure
- Proper imports and modules  
- Scalable service architecture
- Developer-friendly organization
"""

import sys
import os
from pathlib import Path

# Add backend to Python path for proper imports
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Import from proper application modules
from applications.hospital_intelligence import (
    WorkingHospitalIntelligenceSystem,
    HospitalAnalysisRequest,
    HospitalIntelligenceReport
)

from applications.hospital_intelligence.working_hospital_system import HospitalTier
from decimal import Decimal
import asyncio


async def main():
    """Main application entry point"""
    
    print("="*80)
    print("VERTICAL-LIGHT-OS HOSPITAL INTELLIGENCE PLATFORM")
    print("="*80)
    print("Developer-Friendly • Scalable • Production-Ready")
    print()
    
    print("PROJECT STRUCTURE:")
    print("├── applications/           # Production applications")
    print("│   └── hospital_intelligence/  # Hospital analysis system")
    print("├── services/              # Core business services")  
    print("│   └── benchmarking/      # Intelligent benchmarking engine")
    print("├── models/                # Data models and schemas")
    print("├── api/                   # REST API endpoints")
    print("├── cli/                   # Command line interfaces")
    print("├── config/                # Configuration management")
    print("└── demos/                 # Demo and test applications")
    print()
    
    # Initialize the hospital intelligence system
    print("Initializing Hospital Intelligence System...")
    system = WorkingHospitalIntelligenceSystem()
    
    # Create sample analysis request
    print("\nRunning sample hospital analysis...")
    
    sample_request = HospitalAnalysisRequest(
        name="Metro Healthcare Center",
        city="Mumbai",
        tier=HospitalTier.TIER_1,
        bed_count=350,
        annual_revenue=Decimal("890000000"),  # ₹89 crores
        
        # Lifecycle context
        established_year=2015,  # 10 years old
        revenue_growth_rate=0.28,  # 28% growth
        patient_volume_growth_rate=0.24,
        bed_expansion_rate=0.15,
        service_expansion_rate=1.8,
        
        # Performance metrics
        operating_margin=0.18,
        days_in_ar=42,
        collection_rate=0.92,
        occupancy_rate=0.82,
        patient_satisfaction_score=87.5,
        staff_turnover_rate=0.12,
        
        # Market context
        competition_density="high",
        market_maturity="mature"
    )
    
    # Execute analysis
    report = await system.analyze_hospital(sample_request)
    
    # Display executive dashboard
    dashboard = system.generate_executive_dashboard(report)
    print(dashboard)
    
    print("\n" + "="*80)
    print("SYSTEM STATUS: OPERATIONAL")
    print("Ready for production hospital intelligence analysis")
    print("="*80)
    
    return report


if __name__ == "__main__":
    print("Starting VERTICAL-LIGHT-OS Hospital Intelligence Platform...")
    
    # Run main application
    try:
        report = asyncio.run(main())
        print(f"\n✓ Successfully analyzed: {report.hospital_name}")
        print(f"✓ Stage: {report.lifecycle_stage.title()}")
        print(f"✓ Velocity Score: {report.velocity_score:.1f}/100")
        
    except Exception as e:
        print(f"\n✗ Error running application: {e}")
        print("Check project structure and dependencies")
        sys.exit(1)