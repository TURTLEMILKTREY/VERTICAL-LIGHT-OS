#!/usr/bin/env python3

import asyncio
from services.lifecycle_benchmarking_engine import LifecycleAwareBenchmarkingEngine

async def test_integration():
 """Test integration with lifecycle engine"""

 print("LIFECYCLE-AWARE HOSPITAL INTELLIGENCE SYSTEM")
 print("="*50)

 # Sample hospital data
 hospital_data = {
 "name": "Test Medical Center",
 "established_year": 2019,
 "tier": "tier_2", 
 "bed_count": 150,
 "annual_revenue": 350000000,
 "revenue_growth_rate": 0.28,
 "bed_growth_rate": 0.15,
 "patient_growth_rate": 0.22,
 "service_expansion_rate": 2.0,
 "occupancy_rate": 0.72,
 "operating_margin": 0.11,
 "days_in_ar": 42,
 "collection_rate": 0.86,
 "patient_satisfaction_score": 78.5,
 "staff_turnover_rate": 0.18,
 "competition_density": "medium",
 "market_maturity": "growing"
 }

 # Initialize engine
 engine = LifecycleAwareBenchmarkingEngine()

 print("Running lifecycle analysis...")
 result = await engine.analyze_hospital_lifecycle(hospital_data)

 print("Analysis complete!")
 print(f"Lifecycle Stage: {result.hospital_profile.lifecycle_stage.value}")
 print(f"Velocity Tier: {result.velocity_benchmarks.velocity_tier.value}")
 print(f"Velocity Score: {result.velocity_score:.1f}/100")
 print(f"Stage Readiness: {result.stage_readiness_score:.1%}")

 # Generate report
 report = engine.generate_lifecycle_report(result)
 print("\n" + report)

 return result

if __name__ == "__main__":
 result = asyncio.run(test_integration())
 print("\nIntegration test successful!")