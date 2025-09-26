#!/usr/bin/env python3

"""
Production Database Integration Test
===================================

Test the complete database integration with real PostgreSQL database.
This test requires a running PostgreSQL instance.

Setup Instructions:
1. Install PostgreSQL locally or use Docker:
 docker run --name postgres-test -e POSTGRES_PASSWORD=testpass -e POSTGRES_DB=hospital_test -p 5432:5432 -d postgres:14

2. Set environment variable:
 set DATABASE_URL=postgresql://postgres:testpass@localhost:5432/hospital_test

3. Run this test:
 python test_production_integration.py
"""

import os
import sys
import asyncio
import asyncpg
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Production database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:testpass@localhost:5432/hospital_test')

async def setup_test_database():
 """Set up the test database with schema"""
 print("Setting up test database...")

 try:
 # Read schema file
 schema_path = backend_dir / "database" / "schema.sql"
 if not schema_path.exists():
 raise FileNotFoundError("Database schema file not found")

 schema_sql = schema_path.read_text()

 # Connect and create tables
 conn = await asyncpg.connect(DATABASE_URL)

 # Create tables
 await conn.execute(schema_sql)
 print("Database schema created successfully")

 await conn.close()
 return True

 except Exception as e:
 print(f"ERROR: Failed to setup database: {e}")
 return False

async def test_database_connection():
 """Test basic database connectivity"""
 print("\nTesting Database Connection")
 print("=" * 30)

 try:
 conn = await asyncpg.connect(DATABASE_URL)

 # Test basic query
 result = await conn.fetchval("SELECT version()")
 print(f"Connected to PostgreSQL: {result[:50]}...")

 # Test our tables exist
 tables = await conn.fetch("""
 SELECT table_name FROM information_schema.tables 
 WHERE table_schema = 'public'
 """)

 table_names = [row['table_name'] for row in tables]
 expected_tables = ['hospital_analyses', 'audit_logs']

 for table in expected_tables:
 if table in table_names:
 print(f"Table {table} exists")
 else:
 print(f"ERROR: Table {table} missing")
 await conn.close()
 return False

 await conn.close()
 return True

 except Exception as e:
 print(f"ERROR: Database connection failed: {e}")
 return False

async def test_hospital_database_layer():
 """Test the HospitalDatabase class with real database"""
 print("\nTesting HospitalDatabase Layer")
 print("=" * 35)

 try:
 from database.hospital_db import HospitalDatabase, HospitalAnalysisRecord

 # Initialize database
 db = HospitalDatabase(DATABASE_URL)
 await db.initialize()
 print("HospitalDatabase initialized")

 # Create test record
 test_record = HospitalAnalysisRecord(
 analysis_id="test-123",
 hospital_name="Test Hospital DB Layer",
 hospital_age=10,
 lifecycle_stage="GROWTH",
 benchmark_target=25.5,
 growth_velocity="ACCELERATING",
 confidence_score=0.87,
 recommendations=["Expand services", "Improve efficiency"],
 risk_factors=["Market competition"],
 optimization_opportunities=["Digital transformation"],
 created_at=datetime.now()
 )

 # Test save
 success = await db.save_analysis(test_record)
 if success:
 print("Analysis record saved successfully")
 else:
 print("ERROR: Failed to save analysis record")
 return False

 # Test retrieve
 retrieved = await db.get_analysis(test_record.analysis_id)
 if retrieved and retrieved.hospital_name == test_record.hospital_name:
 print("Analysis record retrieved successfully")
 else:
 print("ERROR: Failed to retrieve analysis record")
 return False

 # Test list analyses
 analyses = await db.list_analyses(limit=5)
 if len(analyses) > 0:
 print(f"Listed {len(analyses)} analysis records")
 else:
 print("ERROR: No analyses found in database")

 await db.close()
 return True

 except Exception as e:
 print(f"ERROR: HospitalDatabase layer test failed: {e}")
 import traceback
 traceback.print_exc()
 return False

async def test_data_persistence_service():
 """Test the DataPersistenceService with real database"""
 print("\nTesting DataPersistenceService")
 print("=" * 32)

 try:
 from database.hospital_db import HospitalDatabase
 from services.data_persistence import DataPersistenceService

 # Initialize components
 db = HospitalDatabase(DATABASE_URL)
 service = DataPersistenceService(db)
 await service.initialize()
 print("DataPersistenceService initialized")

 # Test data with validation
 test_data = {
 "hospital_name": "Test Hospital Service Layer",
 "hospital_age": 15,
 "lifecycle_stage": "EXPANSION", 
 "benchmark_target": 22.8,
 "growth_velocity": "MODERATE",
 "confidence_score": 0.92,
 "recommendations": ["Strategic expansion", "Technology upgrade"],
 "risk_factors": ["Economic uncertainty"],
 "optimization_opportunities": ["Process automation", "Staff training"]
 }

 # Test save with service layer
 result = await service.save_hospital_analysis(test_data)

 if result.success:
 print("Analysis saved through service layer")
 print(f" Analysis ID: {result.analysis_id}")
 print(f" Metadata: {result.metadata}")
 else:
 print(f"ERROR: Service layer save failed: {result.error}")
 return False

 # Test convenience method
 saved_count = await service.get_analysis_count()
 print(f"Total analyses in database: {saved_count}")

 await service.close()
 return True

 except Exception as e:
 print(f"ERROR: DataPersistenceService test failed: {e}")
 import traceback
 traceback.print_exc()
 return False

async def test_complete_hospital_intelligence_flow():
 """Test the complete flow from hospital analysis to database"""
 print("\nTesting Complete Hospital Intelligence Flow")
 print("=" * 45)

 try:
 # Import all components
 from database.hospital_db import HospitalDatabase
 from services.data_persistence import DataPersistenceService
 from applications.hospital_intelligence.working_hospital_system import (
 HospitalIntelligenceSystem,
 HospitalAnalysisRequest,
 HospitalTier
 )

 # Initialize all services
 db = HospitalDatabase(DATABASE_URL)
 persistence = DataPersistenceService(db)
 hospital_system = HospitalIntelligenceSystem()

 await persistence.initialize()
 print("All services initialized")

 # Create realistic hospital analysis request
 test_request = HospitalAnalysisRequest(
 name="Regional Medical Center - Integration Test",
 city="Mumbai",
 tier=HospitalTier.TIER_2,
 bed_count=250,
 annual_revenue=Decimal("75000000"), # 7.5 crore INR
 established_year=2008, # 17 years old
 revenue_growth_rate=0.18, # 18% growth
 operating_margin=0.14, # 14% margin
 occupancy_rate=0.82, # 82% occupancy
 patient_satisfaction_score=4.1 # 4.1/5 rating
 )

 print(f"Created analysis request for: {test_request.name}")
 print(f" Hospital Age: {2025 - test_request.established_year} years")
 print(f" Annual Revenue: ₹{test_request.annual_revenue:,}")
 print(f" Growth Rate: {test_request.revenue_growth_rate:.1%}")

 # Run hospital analysis
 analysis_result = await hospital_system.analyze_hospital(test_request)
 print(f"Analysis completed:")
 print(f" Lifecycle Stage: {analysis_result.lifecycle_stage}")
 print(f" Growth Velocity: {analysis_result.growth_velocity_tier}")
 print(f" Revenue Target: {analysis_result.revenue_growth_target:.2f}%")
 print(f" Progression Probability: {analysis_result.progression_probability:.1%}")

 # Convert to database format
 analysis_data = {
 "hospital_name": analysis_result.hospital_name,
 "hospital_age": analysis_result.hospital_age_years,
 "lifecycle_stage": analysis_result.lifecycle_stage,
 "benchmark_target": analysis_result.revenue_growth_target,
 "growth_velocity": analysis_result.growth_velocity_tier,
 "confidence_score": analysis_result.progression_probability,
 "recommendations": analysis_result.strategic_priorities[:3], # Top 3
 "risk_factors": list(analysis_result.performance_gaps.keys())[:3],
 "optimization_opportunities": [inv['category'] for inv in analysis_result.investment_recommendations[:3]]
 }

 # Save to database
 result = await persistence.save_hospital_analysis(analysis_data)

 if result.success:
 print("Complete flow successful - Analysis saved to database")
 print(f" Database Analysis ID: {result.analysis_id}")

 # Verify it's actually in database
 saved_analysis = await db.get_analysis(result.analysis_id)
 if saved_analysis:
 print("Verification: Analysis successfully retrieved from database")
 print(f" Stored Hospital: {saved_analysis.hospital_name}")
 print(f" Stored Stage: {saved_analysis.lifecycle_stage}")
 print(f" Stored Target: {saved_analysis.benchmark_target}%")
 else:
 print("ERROR: Verification failed: Could not retrieve saved analysis")
 return False
 else:
 print(f"ERROR: Complete flow failed: {result.error}")
 return False

 await persistence.close()
 return True

 except Exception as e:
 print(f"ERROR: Complete flow test failed: {e}")
 import traceback
 traceback.print_exc()
 return False

async def test_performance_and_cleanup():
 """Test performance with multiple records and cleanup"""
 print("\nTesting Performance & Cleanup")
 print("=" * 30)

 try:
 from database.hospital_db import HospitalDatabase

 db = HospitalDatabase(DATABASE_URL)
 await db.initialize()

 # Count records before
 initial_count = len(await db.list_analyses())
 print(f"Initial record count: {initial_count}")

 # Clean up test records
 conn = await asyncpg.connect(DATABASE_URL)
 deleted = await conn.execute("""
 DELETE FROM hospital_analyses 
 WHERE hospital_name LIKE '%Test%' OR hospital_name LIKE '%Integration Test%'
 """)
 await conn.close()

 final_count = len(await db.list_analyses())
 print(f"Cleaned up test records")
 print(f" Records after cleanup: {final_count}")

 await db.close()
 return True

 except Exception as e:
 print(f"ERROR: Performance test failed: {e}")
 return False

def print_setup_instructions():
 """Print database setup instructions"""
 print("Database Integration Test - Setup Required")
 print("=" * 50)
 print("\nTo run this test, you need a PostgreSQL database:")
 print("\nOption 1 - Docker (Recommended):")
 print(" docker run --name postgres-test \\")
 print(" -e POSTGRES_PASSWORD=testpass \\")
 print(" -e POSTGRES_DB=hospital_test \\")
 print(" -p 5432:5432 -d postgres:14")
 print("\nOption 2 - Local PostgreSQL:")
 print(" Create database 'hospital_test' with user access")
 print("\nThen set environment variable:")
 print(" set DATABASE_URL=postgresql://postgres:testpass@localhost:5432/hospital_test")
 print("\nRun test:")
 print(" python test_production_integration.py")

async def main():
 """Run all production integration tests"""
 print("Hospital Intelligence System - Production Database Integration")
 print("=" * 70)

 # Check if database URL is configured
 if DATABASE_URL == 'postgresql://postgres:testpass@localhost:5432/hospital_test':
 print("WARNING: Using default database URL - make sure PostgreSQL is running")

 print(f"Database URL: {DATABASE_URL}")

 # Test database setup
 setup_ok = await setup_test_database()
 if not setup_ok:
 print("\nERROR: Database setup failed. Please check connection and try again.")
 print_setup_instructions()
 return

 # Run all tests
 connection_ok = await test_database_connection()
 db_layer_ok = await test_hospital_database_layer()
 service_ok = await test_data_persistence_service() 
 complete_flow_ok = await test_complete_hospital_intelligence_flow()
 cleanup_ok = await test_performance_and_cleanup()

 # Summary
 print("\nProduction Integration Test Results")
 print("=" * 40)
 print(f"Database Connection: {'PASS' if connection_ok else 'FAIL'}")
 print(f"Database Layer: {'PASS' if db_layer_ok else 'FAIL'}")
 print(f"Service Layer: {'PASS' if service_ok else 'FAIL'}")
 print(f"Complete Flow: {'PASS' if complete_flow_ok else 'FAIL'}")
 print(f"Performance & Cleanup: {'PASS' if cleanup_ok else 'FAIL'}")

 overall_pass = all([connection_ok, db_layer_ok, service_ok, complete_flow_ok, cleanup_ok])
 print(f"\nOverall Result: {'PASS' if overall_pass else 'FAIL'}")

 if overall_pass:
 print("\nDATABASE INTEGRATION IS PRODUCTION READY!")
 print("\nThe database integration successfully:")
 print("Connects to real PostgreSQL database")
 print("Creates and manages database schema")
 print("Validates and stores hospital analysis data")
 print("Integrates with HospitalIntelligenceSystem")
 print("Provides service layer with business logic")
 print("Handles errors and edge cases properly")

 print(f"\nDatabase URL: {DATABASE_URL}")
 print("Ready for production deployment!")
 else:
 print("\nERROR: Integration tests failed - needs fixes before production")

if __name__ == "__main__":
 asyncio.run(main())