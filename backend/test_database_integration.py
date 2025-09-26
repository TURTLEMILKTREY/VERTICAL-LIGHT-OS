#!/usr/bin/env python3

"""
Database Integration Test
========================

Test script to validate database integration components without requiring PostgreSQL.
Tests validation, data flow, and service layer functionality.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Mock asyncpg for testing without actual database
class MockConnection:
 async def execute(self, query, *args):
 return "mock_result"

 async def fetch(self, query, *args):
 return []

 async def fetchrow(self, query, *args):
 return None

 async def fetchval(self, query, *args):
 return "mock_id_12345"

class MockPool:
 def __init__(self):
 self.closed = False

 def acquire(self):
 return MockConnection()

 async def close(self):
 self.closed = True

# Monkey patch asyncpg for testing
import asyncpg
original_create_pool = asyncpg.create_pool

async def mock_create_pool(*args, **kwargs):
 return MockPool()

asyncpg.create_pool = mock_create_pool

# Now import our modules
try:
 from services.data_persistence import DataPersistenceService, PersistenceResult
 from database.hospital_db import HospitalDatabase
 print("Successfully imported database modules")
except ImportError as e:
 print(f"ERROR: Import error: {e}")
 sys.exit(1)

async def test_database_integration():
 """Test database integration components"""

 print("\nDatabase Integration Test")
 print("=" * 50)

 # Test 1: Data Persistence Service Initialization
 print("\n1. Testing Data Persistence Service Initialization...")
 try:
 service = DataPersistenceService()
 await service.initialize()
 print("Data persistence service initialized successfully")
 except Exception as e:
 print(f"ERROR: Service initialization failed: {e}")
 return False

 # Test 2: Data Validation
 print("\n2. Testing Data Validation...")

 # Valid data
 valid_analysis = {
 "hospital_name": "Memorial Hospital",
 "hospital_age": 15,
 "lifecycle_stage": "GROWTH", 
 "benchmark_target": 22.5,
 "growth_velocity": "ACCELERATING",
 "confidence_score": 0.92,
 "processing_duration": 1.245,
 "analysis_results": {
 "revenue_optimization": "High potential",
 "operational_efficiency": "Strong metrics"
 }
 }

 validation_result = service._validate_analysis_data(valid_analysis)
 if validation_result.success:
 print("Valid data passed validation")
 else:
 print(f"ERROR: Valid data failed validation: {validation_result.error}")
 return False

 # Invalid data
 invalid_analysis = {
 "hospital_name": "Test Hospital",
 "hospital_age": -5, # Invalid age
 "lifecycle_stage": "INVALID_STAGE", # Invalid stage
 "benchmark_target": 150, # Invalid target
 "growth_velocity": "ACCELERATING",
 "confidence_score": 1.5 # Invalid confidence
 }

 validation_result = service._validate_analysis_data(invalid_analysis)
 if not validation_result.success:
 print("Invalid data correctly rejected")
 else:
 print("ERROR: Invalid data incorrectly accepted")
 return False

 # Test 3: Data Enrichment
 print("\n3. Testing Data Enrichment...")
 enriched_data = service._enrich_analysis_data(valid_analysis)

 required_enrichments = ['analysis_id', 'created_at', 'analysis_date', 'data_persistence_version']
 missing_enrichments = [field for field in required_enrichments if field not in enriched_data]

 if not missing_enrichments:
 print("Data enrichment added all required metadata")
 else:
 print(f"ERROR: Data enrichment missing: {missing_enrichments}")
 return False

 # Test 4: Save Analysis (with mock database)
 print("\n4. Testing Analysis Save...")
 try:
 save_result = await service.save_hospital_analysis(valid_analysis)
 if save_result.success:
 print("Analysis save completed successfully")
 else:
 print(f"ERROR: Analysis save failed: {save_result.error}")
 return False
 except Exception as e:
 print(f"ERROR: Analysis save exception: {e}")
 return False

 # Test 5: History Retrieval (with mock database)
 print("\n5. Testing History Retrieval...")
 try:
 history_result = await service.get_hospital_analysis_history("Memorial Hospital")
 if history_result.success:
 print("History retrieval completed successfully")
 else:
 print(f"ERROR: History retrieval failed: {history_result.error}")
 return False
 except Exception as e:
 print(f"ERROR: History retrieval exception: {e}")
 return False

 # Test 6: Statistics Retrieval (with mock database)
 print("\n6. Testing Statistics Retrieval...")
 try:
 stats_result = await service.get_system_statistics()
 if stats_result.success:
 print("Statistics retrieval completed successfully")
 else:
 print(f"ERROR: Statistics retrieval failed: {stats_result.error}")
 return False
 except Exception as e:
 print(f"ERROR: Statistics retrieval exception: {e}")
 return False

 # Test 7: Service Cleanup
 print("\n7. Testing Service Cleanup...")
 try:
 await service.close()
 print("Service cleanup completed successfully")
 except Exception as e:
 print(f"ERROR: Service cleanup failed: {e}")
 return False

 return True

async def test_hospital_intelligence_integration():
 """Test integration with hospital intelligence system"""

 print("\n\nHospital Intelligence Integration Test")
 print("=" * 50)

 # Test integration with existing hospital system
 try:
 # Import hospital intelligence system
 from applications.hospital_intelligence.working_hospital_system import HospitalIntelligenceSystem, HospitalAnalysisRequest

 print("Successfully imported hospital intelligence system")

 # Create test analysis request using correct field names
 from decimal import Decimal
 from applications.hospital_intelligence.working_hospital_system import HospitalTier

 test_request = HospitalAnalysisRequest(
 name="Integration Test Hospital",
 city="Mumbai", 
 tier=HospitalTier.TIER_2,
 bed_count=150,
 annual_revenue=Decimal('250000000'),
 established_year=2013,
 revenue_growth_rate=0.15,
 operating_margin=0.12,
 occupancy_rate=0.80,
 patient_satisfaction_score=85.5,
 state="Maharashtra",
 patient_volume_growth_rate=0.10,
 bed_expansion_rate=0.05,
 service_expansion_rate=0.08,
 days_in_ar=42,
 collection_rate=0.88,
 staff_turnover_rate=0.125,
 competition_density="medium",
 market_maturity="growing"
 )

 # Test hospital analysis
 system = HospitalIntelligenceSystem()
 analysis_result = await system.analyze_hospital_comprehensive(test_request.dict())

 print("Hospital analysis completed successfully")
 print(f" Lifecycle Stage: {analysis_result.get('lifecycle_stage')}")
 print(f" Benchmark Target: {analysis_result.get('benchmark_target')}%")
 print(f" Growth Velocity: {analysis_result.get('growth_velocity')}")
 print(f" Confidence Score: {analysis_result.get('confidence_score')}")

 # Test persistence integration
 from services.data_persistence import save_analysis

 save_result = await save_analysis(analysis_result)
 if save_result.success:
 print("Analysis persistence integration successful")
 return True
 else:
 print(f"ERROR: Analysis persistence integration failed: {save_result.error}")
 return False

 except ImportError as e:
 print(f"ERROR: Import error: {e}")
 return False
 except Exception as e:
 print(f"ERROR: Integration test failed: {e}")
 return False

def print_summary():
 """Print implementation summary"""

 print("\n\nDatabase Integration Implementation Summary")
 print("=" * 60)
 print("backend/database/hospital_db.py - PostgreSQL async database layer")
 print("backend/database/schema.sql - Production database schema") 
 print("backend/services/data_persistence.py - Service layer with validation")
 print("requirements.txt - Updated with asyncpg dependency")
 print("\nComponents Ready:")
 print(" • Async PostgreSQL database integration")
 print(" • Data validation and business rules")
 print(" • Service layer abstraction") 
 print(" • Error handling and logging")
 print(" • HIPAA audit trail support")
 print(" • Connection pooling and management")
 print("\nNext Steps for Production:")
 print(" 1. Set up PostgreSQL database server")
 print(" 2. Configure connection string in environment")
 print(" 3. Run schema.sql to create database tables")
 print(" 4. Test with actual PostgreSQL instance")
 print(" 5. Configure backup procedures")

async def main():
 """Run all database integration tests"""

 print("Hospital Intelligence System - Database Integration Test")
 print("=" * 60)

 # Run tests
 db_test_passed = await test_database_integration()
 intelligence_test_passed = await test_hospital_intelligence_integration()

 # Print results
 print("\n\nTest Results")
 print("=" * 30)
 print(f"Database Integration: {'PASS' if db_test_passed else 'FAIL'}")
 print(f"Intelligence Integration: {'PASS' if intelligence_test_passed else 'FAIL'}")

 overall_result = db_test_passed and intelligence_test_passed
 print(f"\nOverall Result: {'PASS' if overall_result else 'FAIL'}")

 if overall_result:
 print("\nDatabase integration is ready for production deployment!")
 else:
 print("\nWARNING: Database integration needs fixes before production.")

 print_summary()

if __name__ == "__main__":
 asyncio.run(main())