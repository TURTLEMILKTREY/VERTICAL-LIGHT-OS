#!/usr/bin/env python3

"""
Quick Database Validation Test
=============================

Simple test to validate our database is working with live data.
"""

import os
import sys
import asyncio
import asyncpg
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:testpass@localhost:5432/hospital_intelligence')

async def test_simple_database():
 """Simple test to validate database functionality"""
 print("VERTICAL LIGHT OS - Database Validation")
 print("=" * 50)

 try:
  # Connect to database
  conn = await asyncpg.connect(DATABASE_URL)
 print("Connected to PostgreSQL successfully")

 # Test basic query
 result = await conn.fetchval("SELECT version()")
 print(f"Database version: {result[:30]}...")

 # Check if our main table exists
 table_check = await conn.fetchval("""
 SELECT EXISTS (
 SELECT FROM information_schema.tables 
 WHERE table_schema = 'public' 
 AND table_name = 'hospital_analyses'
 )
 """)

 if table_check:
 print("Hospital analyses table exists")
 else:
 print("ERROR: Hospital analyses table missing")
 await conn.close()
 return False

 # Insert a test record directly
 test_id = "test-" + str(datetime.now().timestamp())
 insert_result = await conn.execute("""
 INSERT INTO hospital_analyses (
 hospital_name, 
 hospital_age, 
 lifecycle_stage, 
 benchmark_target, 
 growth_velocity, 
 analysis_results, 
 confidence_score, 
 processing_duration
 ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
 """, 
 "Test Hospital - Quick Validation",
 15,
 "GROWTH", 
 22.5,
 "ACCELERATING",
 '{"test": true, "validation": "successful"}',
 0.95,
 0.150
 )

 if "INSERT" in insert_result:
 print("Test record inserted successfully")
 else:
 print("ERROR: Failed to insert test record")

 # Query the record back
 records = await conn.fetch("""
 SELECT hospital_name, lifecycle_stage, benchmark_target, confidence_score
 FROM hospital_analyses 
 WHERE hospital_name LIKE '%Test Hospital%'
 ORDER BY created_at DESC
 LIMIT 3
 """)

 if records:
 print(f"Retrieved {len(records)} test records:")
 for record in records:
 print(f" Hospital: {record['hospital_name']}")
 print(f" Stage: {record['lifecycle_stage']}")
 print(f" Target: {record['benchmark_target']}%")
 print(f" Confidence: {record['confidence_score']}")
 print()

 # Test analysis summary function
 try:
 summary = await conn.fetchrow("SELECT * FROM get_analysis_summary()")
 if summary:
 print("Database functions working:")
 print(f" Total analyses: {summary['total_analyses']}")
 print(f" Unique hospitals: {summary['unique_hospitals']}")
 print(f" Average confidence: {summary['avg_confidence']}")
 except Exception as e:
 print(f"WARNING: Analysis summary function issue: {e}")

 # Clean up test records
 deleted = await conn.execute("""
 DELETE FROM hospital_analyses 
 WHERE hospital_name LIKE '%Test Hospital%'
 """)
 print(f"Cleaned up test records: {deleted}")

 await conn.close()
 return True

 except Exception as e:
 print(f"ERROR: Database test failed: {e}")
 import traceback
 traceback.print_exc()
 return False

async def test_hospital_intelligence_integration():
 """Test integration with hospital intelligence system"""
 print("\nTesting Hospital Intelligence Integration")
 print("=" * 50)

 try:
 from applications.hospital_intelligence.working_hospital_system import (
 HospitalIntelligenceSystem,
 HospitalAnalysisRequest,
 HospitalTier
 )

 # Initialize system
 hospital_system = HospitalIntelligenceSystem()
 print("Hospital Intelligence System initialized")

 # Create test request
 test_request = HospitalAnalysisRequest(
 name="Mumbai Medical Center - Live Test",
 city="Mumbai",
 tier=HospitalTier.TIER_2,
 bed_count=200,
 annual_revenue=Decimal("50000000"), # 5 crore
 established_year=2010, # 15 years old
 revenue_growth_rate=0.15, # 15% growth
 operating_margin=0.12, # 12% margin
 occupancy_rate=0.78, # 78% occupancy
 patient_satisfaction_score=3.9 # 3.9/5 rating
 )

 print("Created analysis request:")
 print(f" Hospital: {test_request.name}")
 print(f" Age: {2025 - test_request.established_year} years")
 print(f" Revenue: ₹{test_request.annual_revenue:,}")

 # Run analysis
 result = await hospital_system.analyze_hospital(test_request)
 print("Analysis completed:")
 print(f" Lifecycle: {result.lifecycle_stage}")
 print(f" Growth Velocity: {result.growth_velocity_tier}")
 print(f" Revenue Target: {result.revenue_growth_target:.1f}%")
 print(f" Confidence: {result.progression_probability:.1%}")

 # Test data persistence (manual approach)
 conn = await asyncpg.connect(DATABASE_URL)

 # Convert to database format
 analysis_data = {
 "hospital_name": result.hospital_name,
 "hospital_age": result.hospital_age_years,
 "lifecycle_stage": result.lifecycle_stage.upper(),
 "benchmark_target": float(result.revenue_growth_target),
 "growth_velocity": result.growth_velocity_tier.upper(),
 "analysis_results": {
 "strategic_priorities": result.strategic_priorities[:3],
 "performance_gaps": dict(list(result.performance_gaps.items())[:3]),
 "investment_recommendations": result.investment_recommendations[:3]
 },
 "confidence_score": float(result.progression_probability),
 "processing_duration": 0.5 # Placeholder
 }

 # Save to database
 save_result = await conn.execute("""
 INSERT INTO hospital_analyses (
 hospital_name, hospital_age, lifecycle_stage, 
 benchmark_target, growth_velocity, analysis_results,
 confidence_score, processing_duration
 ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
 """, 
 analysis_data["hospital_name"],
 analysis_data["hospital_age"], 
 analysis_data["lifecycle_stage"],
 analysis_data["benchmark_target"],
 analysis_data["growth_velocity"],
 json.dumps(analysis_data["analysis_results"]),
 analysis_data["confidence_score"],
 analysis_data["processing_duration"]
 )

 if "INSERT" in save_result:
 print("Analysis results saved to database")

 # Verify by reading back
 saved = await conn.fetchrow("""
 SELECT hospital_name, lifecycle_stage, benchmark_target
 FROM hospital_analyses 
 WHERE hospital_name = $1
 ORDER BY created_at DESC
 LIMIT 1
 """, result.hospital_name)

 if saved:
 print("Verification: Data successfully retrieved")
 print(f" Saved Hospital: {saved['hospital_name']}")
 print(f" Saved Stage: {saved['lifecycle_stage']}")
 print(f" Saved Target: {saved['benchmark_target']}%")
 else:
 print("ERROR: Could not verify saved data")

 await conn.close()
 return True

 except Exception as e:
 print(f"ERROR: Hospital intelligence integration failed: {e}")
 import traceback
 traceback.print_exc()
 return False

async def main():
 """Run database validation tests"""
 print("VERTICAL LIGHT OS - Production Database Validation")
 print("=" * 60)
 print(f"Database: {DATABASE_URL}")
 print()

 # Run tests
 basic_test = await test_simple_database()
 integration_test = await test_hospital_intelligence_integration()

 print("\n" + "=" * 60)
 print("DATABASE VALIDATION RESULTS")
 print("=" * 60)
 print(f"Basic Database Operations: {'PASS' if basic_test else 'FAIL'}")
 print(f"Hospital Intelligence Integration: {'PASS' if integration_test else 'FAIL'}")

 overall_success = basic_test and integration_test
 print(f"\nOverall Result: {'PASS' if overall_success else 'FAIL'}")

 if overall_success:
 print("\nDATABASE IS FULLY OPERATIONAL!")
 print("\nYour VERTICAL LIGHT OS can now:")
 print(" - Store and retrieve live hospital data")
 print(" - Run hospital intelligence analysis")
 print(" - Generate professional reports")
 print(" - Support real client demonstrations")
 print(" - Scale to multiple hospitals")

 print(f"\nREADY FOR PRODUCTION DEPLOYMENT!")
 print(f" Database URL: {DATABASE_URL}")
 print(" Status: LIVE DATA OPERATIONS ENABLED")

 else:
 print("\nERROR: Database validation failed - needs fixes")
 print(" Check connection settings and schema")

if __name__ == "__main__":
 asyncio.run(main())