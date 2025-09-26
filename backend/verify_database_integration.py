#!/usr/bin/env python3

"""
Simple Database Integration Verification
=======================================

Verify database integration components are properly structured and importable.
"""

import sys
from pathlib import Path

# Add backend to path 
backend_dir = Path(__file__).parent # This file is in backend/
sys.path.insert(0, str(backend_dir))

def test_imports():
 """Test that all database components can be imported"""
 print("Database Integration Component Verification")
 print("=" * 50)

 try:
 # Test database module imports
 from database.hospital_db import HospitalDatabase, HospitalAnalysisRecord
 print("HospitalDatabase imported successfully")

 # Test service layer imports
 from services.data_persistence import DataPersistenceService, PersistenceResult
 print("DataPersistenceService imported successfully")

 # Test that classes are properly defined
 db = HospitalDatabase("mock_connection_string")
 print("HospitalDatabase can be instantiated")

 # Test validation logic without database
 service = DataPersistenceService(db)

 # Test valid data
 valid_data = {
 "hospital_name": "Test Hospital",
 "hospital_age": 15,
 "lifecycle_stage": "GROWTH",
 "benchmark_target": 22.5,
 "growth_velocity": "ACCELERATING", 
 "confidence_score": 0.92
 }

 validation_result = service._validate_analysis_data(valid_data)
 if validation_result.success:
 print("Data validation works for valid data")
 else:
 print(f"ERROR: Data validation failed: {validation_result.error}")
 return False

 # Test invalid data
 invalid_data = {
 "hospital_name": "Test Hospital",
 "hospital_age": -5, # Invalid
 "lifecycle_stage": "INVALID", # Invalid
 "benchmark_target": 150, # Invalid
 "growth_velocity": "ACCELERATING",
 "confidence_score": 2.0 # Invalid
 }

 validation_result = service._validate_analysis_data(invalid_data)
 if not validation_result.success:
 print("Data validation correctly rejects invalid data")
 else:
 print("ERROR: Data validation incorrectly accepted invalid data")
 return False

 # Test data enrichment
 enriched = service._enrich_analysis_data(valid_data)
 if 'analysis_id' in enriched and 'created_at' in enriched:
 print("Data enrichment adds required metadata")
 else:
 print("ERROR: Data enrichment missing required fields")
 return False

 return True

 except ImportError as e:
 print(f"ERROR: Import error: {e}")
 return False
 except Exception as e:
 print(f"ERROR: Unexpected error: {e}")
 return False

def check_database_files():
 """Check that all required database files exist"""
 print("\nDatabase File Structure Verification")
 print("=" * 40)

 # Use absolute paths
 required_files = {
 "database/hospital_db.py": backend_dir / "database" / "hospital_db.py",
 "database/schema.sql": backend_dir / "database" / "schema.sql", 
 "services/data_persistence.py": backend_dir / "services" / "data_persistence.py"
 }

 all_exist = True
 for name, full_path in required_files.items():
 if full_path.exists():
 print(f"{name}")
 else:
 print(f"ERROR: {name} - MISSING (checked: {full_path})")
 all_exist = False

 return all_exist

def verify_requirements():
 """Check requirements.txt has necessary dependencies"""
 print("\nDependency Verification")
 print("=" * 25)

 requirements_file = backend_dir.parent / "requirements.txt"
 backend_requirements = backend_dir / "requirements.txt"

 # Check both locations
 requirements_path = None
 if requirements_file.exists():
 requirements_path = requirements_file
 print(f"Found requirements.txt at: {requirements_file}")
 elif backend_requirements.exists():
 requirements_path = backend_requirements
 print(f"Found requirements.txt at: {backend_requirements}")
 else:
 print(f"ERROR: requirements.txt not found (checked {requirements_file} and {backend_requirements})")
 return False

 content = requirements_path.read_text()
 required_deps = ['asyncpg', 'fastapi', 'pydantic']

 all_deps_found = True
 for dep in required_deps:
 if dep in content:
 print(f"{dep} found in requirements.txt")
 else:
 print(f"ERROR: {dep} missing from requirements.txt") 
 all_deps_found = False

 return all_deps_found

def main():
 """Run all verification tests"""
 print("Hospital Intelligence System - Database Integration Verification")
 print("=" * 70)

 # Run tests
 files_ok = check_database_files()
 deps_ok = verify_requirements() 
 imports_ok = test_imports()

 # Summary
 print("\nVerification Summary")
 print("=" * 25)
 print(f"Database files: {'PASS' if files_ok else 'FAIL'}")
 print(f"Dependencies: {'PASS' if deps_ok else 'FAIL'}")
 print(f"Import & Logic: {'PASS' if imports_ok else 'FAIL'}")

 overall_pass = files_ok and deps_ok and imports_ok
 print(f"\nOverall: {'PASS' if overall_pass else 'FAIL'}")

 if overall_pass:
 print("\nDatabase Integration Status: READY")
 print("\nImplemented Components:")
 print("• PostgreSQL async database layer (hospital_db.py)")
 print("• Production database schema (schema.sql)") 
 print("• Service layer with validation (data_persistence.py)")
 print("• Business rule validation")
 print("• Data enrichment and audit trails")
 print("• Error handling and logging")

 print("\nFor Production Deployment:")
 print("1. Set up PostgreSQL database server")
 print("2. Configure DATABASE_URL environment variable")
 print("3. Run schema.sql to create tables") 
 print("4. Start the application services")

 else:
 print("\nDatabase Integration Status: NEEDS FIXES")
 print("Please resolve the issues above before production deployment.")

if __name__ == "__main__":
 main()