"""
Hospital Benchmark Database Migration Script
Create and initialize the benchmark database with Indian hospital performance data
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json

from ..models.hospital_benchmarks import (
 Base, Hospital, PerformanceMetrics, FinancialMetrics, 
 GovernmentSchemeData, BenchmarkStandards, HospitalSpecialty,
 CityTier, HospitalType, SpecialtyType, GovernmentScheme
)
from ..config.advanced_config_manager import ConfigManager


class BenchmarkDatabaseManager:
 """Manages benchmark database creation and initialization"""

 def __init__(self, config: ConfigManager):
 self.config = config
 self.logger = logging.getLogger(__name__)

 # Database configuration
 db_config = config.get("database", {})
 self.database_url = db_config.get("url", "postgresql+asyncpg://user:password@localhost/hospital_benchmarks")

 # Create async engine
 self.engine = create_async_engine(
 self.database_url,
 echo=config.get("database.echo", False),
 pool_size=config.get("database.pool_size", 10),
 max_overflow=config.get("database.max_overflow", 20)
 )

 # Create session factory
 self.async_session = sessionmaker(
 self.engine, class_=AsyncSession, expire_on_commit=False
 )

 async def create_database_schema(self):
 """Create all database tables"""

 try:
 self.logger.info("Creating benchmark database schema...")

 async with self.engine.begin() as conn:
 # Drop existing tables if requested
 if self.config.get("database.drop_existing", False):
 await conn.run_sync(Base.metadata.drop_all)
 self.logger.info("Dropped existing tables")

 # Create all tables
 await conn.run_sync(Base.metadata.create_all)

 # Create indexes for better performance
 await self._create_custom_indexes(conn)

 self.logger.info("Database schema created successfully")

 except Exception as e:
 self.logger.error(f"Failed to create database schema: {str(e)}")
 raise

 async def _create_custom_indexes(self, conn):
 """Create custom database indexes for performance optimization"""

 indexes = [
 # Hospital search indexes
 "CREATE INDEX IF NOT EXISTS idx_hospital_city_state ON hospitals (city, state);",
 "CREATE INDEX IF NOT EXISTS idx_hospital_tier_type ON hospitals (city_tier, hospital_type);",
 "CREATE INDEX IF NOT EXISTS idx_hospital_bed_count ON hospitals (bed_count);",

 # Performance metrics indexes
 "CREATE INDEX IF NOT EXISTS idx_performance_period_type ON performance_metrics (data_period, data_type);",
 "CREATE INDEX IF NOT EXISTS idx_performance_occupancy ON performance_metrics (bed_occupancy_rate);",
 "CREATE INDEX IF NOT EXISTS idx_performance_satisfaction ON performance_metrics (patient_satisfaction_score);",

 # Financial metrics indexes
 "CREATE INDEX IF NOT EXISTS idx_financial_revenue ON financial_metrics (total_revenue);",
 "CREATE INDEX IF NOT EXISTS idx_financial_margin ON financial_metrics (ebitda_margin);",
 "CREATE INDEX IF NOT EXISTS idx_financial_ar_days ON financial_metrics (accounts_receivable_days);",

 # Government scheme indexes
 "CREATE INDEX IF NOT EXISTS idx_scheme_approval_rate ON government_scheme_data (approval_rate);",
 "CREATE INDEX IF NOT EXISTS idx_scheme_reimbursement_days ON government_scheme_data (average_reimbursement_days);",

 # Benchmark standards indexes
 "CREATE INDEX IF NOT EXISTS idx_benchmark_lookup ON benchmark_standards (city_tier, hospital_type, specialty_type, bed_size_category);"
 ]

 for index_sql in indexes:
 try:
 await conn.execute(text(index_sql))
 except Exception as e:
 self.logger.warning(f"Failed to create index: {index_sql[:50]}... - {str(e)}")

 async def populate_initial_data(self):
 """Populate database with initial Indian hospital data"""

 try:
 self.logger.info("Populating initial benchmark data...")

 async with self.async_session() as session:
 # Create sample hospitals
 await self._create_sample_hospitals(session)

 # Create sample performance data
 await self._create_sample_performance_data(session)

 # Create sample financial data
 await self._create_sample_financial_data(session)

 # Create government scheme data
 await self._create_sample_government_scheme_data(session)

 # Create initial benchmark standards
 await self._create_initial_benchmark_standards(session)

 await session.commit()

 self.logger.info("Initial data populated successfully")

 except Exception as e:
 self.logger.error(f"Failed to populate initial data: {str(e)}")
 raise

 async def _create_sample_hospitals(self, session: AsyncSession):
 """Create sample hospitals representing Indian healthcare landscape"""

 sample_hospitals = [
 # Tier 1 Private Corporate Hospitals
 {
 "id": "hosp_apollo_mumbai_001",
 "name": "Apollo Hospital Mumbai",
 "city": "Mumbai", "state": "Maharashtra",
 "city_tier": CityTier.TIER_1,
 "hospital_type": HospitalType.PRIVATE_CORPORATE,
 "bed_count": 500, "established_year": 1995,
 "accreditation_nabh": True, "accreditation_jci": True,
 "phone": "+91-22-2692-7777",
 "email": "mumbai@apollohospitals.com"
 },
 {
 "id": "hosp_fortis_delhi_001", 
 "name": "Fortis Hospital Delhi",
 "city": "Delhi", "state": "Delhi",
 "city_tier": CityTier.TIER_1,
 "hospital_type": HospitalType.PRIVATE_CORPORATE,
 "bed_count": 400, "established_year": 2001,
 "accreditation_nabh": True, "accreditation_jci": False,
 "phone": "+91-11-4277-6222"
 },
 {
 "id": "hosp_manipal_bangalore_001",
 "name": "Manipal Hospital Bangalore", 
 "city": "Bangalore", "state": "Karnataka",
 "city_tier": CityTier.TIER_1,
 "hospital_type": HospitalType.PRIVATE_CORPORATE,
 "bed_count": 650, "established_year": 1991,
 "accreditation_nabh": True, "accreditation_jci": True
 },

 # Tier 1 Government Hospitals
 {
 "id": "hosp_aiims_delhi_001",
 "name": "All Institute of Medical Sciences Delhi",
 "city": "Delhi", "state": "Delhi", 
 "city_tier": CityTier.TIER_1,
 "hospital_type": HospitalType.GOVERNMENT,
 "bed_count": 2500, "established_year": 1956,
 "accreditation_nabh": True
 },
 {
 "id": "hosp_kem_mumbai_001",
 "name": "King Edward Memorial Hospital Mumbai",
 "city": "Mumbai", "state": "Maharashtra",
 "city_tier": CityTier.TIER_1, 
 "hospital_type": HospitalType.GOVERNMENT,
 "bed_count": 1800, "established_year": 1926
 },

 # Tier 2 Private Hospitals
 {
 "id": "hosp_ruby_pune_001",
 "name": "Ruby Hall Clinic Pune",
 "city": "Pune", "state": "Maharashtra",
 "city_tier": CityTier.TIER_2,
 "hospital_type": HospitalType.PRIVATE_STANDALONE,
 "bed_count": 750, "established_year": 1959,
 "accreditation_nabh": True
 },
 {
 "id": "hosp_yashoda_hyderabad_001",
 "name": "Yashoda Hospitals Hyderabad",
 "city": "Hyderabad", "state": "Telangana",
 "city_tier": CityTier.TIER_2,
 "hospital_type": HospitalType.PRIVATE_CORPORATE,
 "bed_count": 500, "established_year": 1989
 },
 {
 "id": "hosp_sterling_ahmedabad_001",
 "name": "Sterling Hospital Ahmedabad",
 "city": "Ahmedabad", "state": "Gujarat", 
 "city_tier": CityTier.TIER_2,
 "hospital_type": HospitalType.PRIVATE_STANDALONE,
 "bed_count": 300, "established_year": 2005
 },

 # Tier 3 Hospitals
 {
 "id": "hosp_indore_multi_001",
 "name": "Indore Multi Specialty Hospital",
 "city": "Indore", "state": "Madhya Pradesh",
 "city_tier": CityTier.TIER_3,
 "hospital_type": HospitalType.PRIVATE_STANDALONE,
 "bed_count": 200, "established_year": 2010
 },
 {
 "id": "hosp_coimbatore_medical_001",
 "name": "Coimbatore Medical College Hospital",
 "city": "Coimbatore", "state": "Tamil Nadu",
 "city_tier": CityTier.TIER_3,
 "hospital_type": HospitalType.MEDICAL_COLLEGE,
 "bed_count": 1200, "established_year": 1966
 }
 ]

 for hospital_data in sample_hospitals:
 hospital = Hospital(**hospital_data)
 session.add(hospital)

 # Add specialties for each hospital
 await self._add_hospital_specialties(session, hospital.id, hospital_data)

 async def _add_hospital_specialties(self, session: AsyncSession, hospital_id: str, hospital_data: dict):
 """Add specialties for hospitals"""

 # Define specialties based on hospital type and size
 if hospital_data["bed_count"] > 500:
 specialties = ["multispecialty", "cardiology", "oncology", "neurology", "orthopedics"]
 elif hospital_data["bed_count"] > 200:
 specialties = ["multispecialty", "cardiology", "orthopedics"]
 else:
 specialties = ["multispecialty"]

 for specialty in specialties:
 hospital_specialty = HospitalSpecialty(
 hospital_id=hospital_id,
 specialty_type=specialty,
 bed_count_specialty=hospital_data["bed_count"] // len(specialties),
 is_primary_specialty=(specialty == "multispecialty"),
 emergency_services=True,
 icu_services=True,
 surgery_facilities=True
 )
 session.add(hospital_specialty)

 async def _create_sample_performance_data(self, session: AsyncSession):
 """Create sample performance metrics data"""

 hospitals_query = await session.execute(text("SELECT id, city_tier, hospital_type, bed_count FROM hospitals"))
 hospitals = hospitals_query.fetchall()

 current_period = datetime.utcnow().strftime("%Y-%m")

 for hospital in hospitals:
 hospital_id, city_tier, hospital_type, bed_count = hospital

 # Generate realistic performance metrics based on hospital characteristics
 base_occupancy = self._get_base_occupancy(city_tier, hospital_type)
 base_satisfaction = self._get_base_satisfaction(city_tier, hospital_type)

 performance_data = PerformanceMetrics(
 hospital_id=hospital_id,
 data_period=current_period,
 data_type="monthly",

 # Operational Metrics
 bed_occupancy_rate=Decimal(str(base_occupancy + (hash(hospital_id) % 20) - 10)),
 average_length_of_stay=Decimal(str(3.5 + (hash(hospital_id) % 30) / 10)),
 patient_turnover_ratio=Decimal(str(8.5 + (hash(hospital_id) % 15) / 10)),

 # Emergency Department
 ed_patient_volume=(bed_count * 2) + (hash(hospital_id) % 100),
 ed_average_wait_time=25 + (hash(hospital_id) % 40),
 ed_left_without_treatment=Decimal(str(2 + (hash(hospital_id) % 8))),

 # Surgery Metrics
 or_utilization_rate=Decimal(str(75 + (hash(hospital_id) % 20))),
 surgery_volume=(bed_count // 4) + (hash(hospital_id) % 50),
 surgery_cancellation_rate=Decimal(str(3 + (hash(hospital_id) % 7))),

 # Quality Metrics
 patient_satisfaction_score=Decimal(str(base_satisfaction + (hash(hospital_id) % 20) / 10)),
 readmission_rate=Decimal(str(5 + (hash(hospital_id) % 10))),
 mortality_rate=Decimal(str(1 + (hash(hospital_id) % 4))),
 infection_rate=Decimal(str(0.5 + (hash(hospital_id) % 3))),

 # Staff Metrics
 nurse_to_patient_ratio=Decimal(str(0.4 + (hash(hospital_id) % 6) / 10)),
 doctor_to_patient_ratio=Decimal(str(0.15 + (hash(hospital_id) % 3) / 20)),
 staff_turnover_rate=Decimal(str(8 + (hash(hospital_id) % 15))),
 staff_satisfaction_score=Decimal(str(7 + (hash(hospital_id) % 25) / 10)),

 data_source="sample_data",
 data_quality_score=Decimal("8.5")
 )

 session.add(performance_data)

 def _get_base_occupancy(self, city_tier: str, hospital_type: str) -> float:
 """Get base occupancy rate based on tier and type"""
 base_rates = {
 ("tier_1", "private_corporate"): 82,
 ("tier_1", "government"): 95,
 ("tier_2", "private_corporate"): 78,
 ("tier_2", "private_standalone"): 72,
 ("tier_3", "private_standalone"): 65,
 ("tier_3", "medical_college"): 88
 }
 return base_rates.get((city_tier, hospital_type), 70)

 def _get_base_satisfaction(self, city_tier: str, hospital_type: str) -> float:
 """Get base patient satisfaction based on tier and type"""
 base_satisfaction = {
 ("tier_1", "private_corporate"): 8.2,
 ("tier_1", "government"): 6.8,
 ("tier_2", "private_corporate"): 7.8,
 ("tier_2", "private_standalone"): 7.5,
 ("tier_3", "private_standalone"): 7.0,
 ("tier_3", "medical_college"): 7.2
 }
 return base_satisfaction.get((city_tier, hospital_type), 7.0)

 async def _create_sample_financial_data(self, session: AsyncSession):
 """Create sample financial metrics data"""

 hospitals_query = await session.execute(text("SELECT id, city_tier, hospital_type, bed_count FROM hospitals"))
 hospitals = hospitals_query.fetchall()

 current_period = datetime.utcnow().strftime("%Y-%m")

 for hospital in hospitals:
 hospital_id, city_tier, hospital_type, bed_count = hospital

 # Calculate realistic financial metrics
 base_revenue_per_bed = self._get_base_revenue_per_bed(city_tier, hospital_type)
 total_revenue = Decimal(str(base_revenue_per_bed * bed_count / 12)) # Monthly revenue

 financial_data = FinancialMetrics(
 hospital_id=hospital_id,
 data_period=current_period,
 data_type="monthly",

 # Revenue Metrics (INR Lakhs)
 total_revenue=total_revenue,
 ip_revenue=total_revenue * Decimal("0.60"),
 op_revenue=total_revenue * Decimal("0.25"),
 emergency_revenue=total_revenue * Decimal("0.10"),
 diagnostic_revenue=total_revenue * Decimal("0.15"),
 pharmacy_revenue=total_revenue * Decimal("0.20"),

 # Cost Metrics
 total_costs=total_revenue * Decimal("0.82"),
 staff_costs=total_revenue * Decimal("0.45"),
 medical_supply_costs=total_revenue * Decimal("0.15"),
 equipment_costs=total_revenue * Decimal("0.08"),
 facility_costs=total_revenue * Decimal("0.10"),
 administrative_costs=total_revenue * Decimal("0.04"),

 # Profitability
 gross_margin=Decimal("18.0"),
 ebitda_margin=Decimal("12.5"),
 net_margin=Decimal("8.5"),

 # Efficiency Metrics
 revenue_per_bed=Decimal(str(base_revenue_per_bed / 12)),
 cost_per_patient=Decimal(str(12000 + (hash(hospital_id) % 8000))),
 accounts_receivable_days=35 + (hash(hospital_id) % 30),
 inventory_turnover_ratio=Decimal(str(6 + (hash(hospital_id) % 8))),

 # Payer Mix
 cash_percentage=Decimal(str(30 + (hash(hospital_id) % 25))),
 insurance_percentage=Decimal(str(25 + (hash(hospital_id) % 20))),
 government_scheme_percentage=Decimal(str(20 + (hash(hospital_id) % 25))),
 corporate_tie_up_percentage=Decimal(str(10 + (hash(hospital_id) % 15))),

 data_source="sample_data",
 audited=True
 )

 session.add(financial_data)

 def _get_base_revenue_per_bed(self, city_tier: str, hospital_type: str) -> float:
 """Get base annual revenue per bed based on tier and type"""
 base_revenue = {
 ("tier_1", "private_corporate"): 25.0, # INR Lakhs per bed per year
 ("tier_1", "government"): 8.0,
 ("tier_2", "private_corporate"): 18.0,
 ("tier_2", "private_standalone"): 15.0,
 ("tier_3", "private_standalone"): 12.0,
 ("tier_3", "medical_college"): 6.0
 }
 return base_revenue.get((city_tier, hospital_type), 10.0)

 async def _create_sample_government_scheme_data(self, session: AsyncSession):
 """Create sample government scheme reimbursement data"""

 hospitals_query = await session.execute(text("SELECT id, city_tier, hospital_type FROM hospitals"))
 hospitals = hospitals_query.fetchall()

 current_period = datetime.utcnow().strftime("%Y-%m")

 schemes = [
 GovernmentScheme.AYUSHMAN_BHARAT,
 GovernmentScheme.CGHS,
 GovernmentScheme.ESI,
 GovernmentScheme.STATE_SCHEMES
 ]

 for hospital in hospitals:
 hospital_id, city_tier, hospital_type = hospital

 for scheme in schemes:
 # Skip certain combinations that don't make sense
 if hospital_type == "private_corporate" and scheme == GovernmentScheme.CGHS:
 continue

 case_count = self._get_scheme_case_count(scheme, city_tier)

 scheme_data = GovernmentSchemeData(
 hospital_id=hospital_id,
 scheme_type=scheme.value,
 data_period=current_period,

 # Volume Metrics
 total_cases=case_count,
 total_patients=int(case_count * 0.85),

 # Financial Metrics
 total_billed_amount=Decimal(str(case_count * 25000)), # Avg ₹25,000 per case
 total_approved_amount=Decimal(str(case_count * 22000)), # 88% approval
 total_received_amount=Decimal(str(case_count * 20000)), # 91% collection

 # Efficiency Metrics
 approval_rate=Decimal(str(85 + (hash(hospital_id + scheme.value) % 10))),
 rejection_rate=Decimal(str(8 + (hash(hospital_id + scheme.value) % 7))),
 average_reimbursement_days=25 + (hash(hospital_id + scheme.value) % 20),

 # Case Mix
 emergency_cases=int(case_count * 0.30),
 planned_cases=int(case_count * 0.70),
 surgery_cases=int(case_count * 0.40),
 medical_cases=int(case_count * 0.60),

 # Pricing
 average_case_value=Decimal(str(22000 + (hash(hospital_id + scheme.value) % 8000))),
 price_variance_percentage=Decimal(str(5 + (hash(hospital_id + scheme.value) % 15)))
 )

 session.add(scheme_data)

 def _get_scheme_case_count(self, scheme: GovernmentScheme, city_tier: str) -> int:
 """Get realistic case counts for government schemes"""
 base_cases = {
 (GovernmentScheme.AYUSHMAN_BHARAT, "tier_1"): 200,
 (GovernmentScheme.AYUSHMAN_BHARAT, "tier_2"): 150, 
 (GovernmentScheme.AYUSHMAN_BHARAT, "tier_3"): 100,
 (GovernmentScheme.CGHS, "tier_1"): 80,
 (GovernmentScheme.CGHS, "tier_2"): 50,
 (GovernmentScheme.ESI, "tier_1"): 120,
 (GovernmentScheme.ESI, "tier_2"): 90,
 (GovernmentScheme.STATE_SCHEMES, "tier_1"): 100,
 (GovernmentScheme.STATE_SCHEMES, "tier_2"): 80,
 (GovernmentScheme.STATE_SCHEMES, "tier_3"): 60
 }
 return base_cases.get((scheme, city_tier), 50)

 async def _create_initial_benchmark_standards(self, session: AsyncSession):
 """Create initial benchmark standards for Indian hospitals"""

 # Define benchmark categories
 benchmark_categories = [
 ("tier_1", "private_corporate", None, "large"),
 ("tier_1", "government", None, "large"),
 ("tier_2", "private_corporate", None, "medium"),
 ("tier_2", "private_standalone", None, "medium"),
 ("tier_3", "private_standalone", None, "small")
 ]

 current_period = datetime.utcnow().strftime("%Y-Q%d" % ((datetime.utcnow().month - 1) // 3 + 1))

 for city_tier, hospital_type, specialty_type, bed_size in benchmark_categories:
 benchmark_data = self._generate_benchmark_data(city_tier, hospital_type)

 benchmark_standard = BenchmarkStandards(
 city_tier=city_tier,
 hospital_type=hospital_type,
 specialty_type=specialty_type,
 bed_size_category=bed_size,
 benchmark_data=benchmark_data,
 sample_size=self._get_sample_size(city_tier, hospital_type),
 data_period=current_period,
 percentile_25=self._calculate_percentiles(benchmark_data, 25),
 percentile_50=self._calculate_percentiles(benchmark_data, 50),
 percentile_75=self._calculate_percentiles(benchmark_data, 75),
 percentile_90=self._calculate_percentiles(benchmark_data, 90)
 )

 session.add(benchmark_standard)

 def _generate_benchmark_data(self, city_tier: str, hospital_type: str) -> dict:
 """Generate realistic benchmark data for tier and type combination"""

 benchmarks = {
 ("tier_1", "private_corporate"): {
 "bed_occupancy_rate": {"mean": 82.5, "std": 8.2, "p50": 83.0, "p75": 88.5, "p90": 92.0},
 "patient_satisfaction_score": {"mean": 8.2, "std": 0.8, "p50": 8.3, "p75": 8.8, "p90": 9.1},
 "revenue_per_bed": {"mean": 24.5, "std": 4.2, "p50": 24.0, "p75": 27.5, "p90": 30.8},
 "accounts_receivable_days": {"mean": 38, "std": 12, "p50": 36, "p75": 45, "p90": 55},
 "ebitda_margin": {"mean": 18.5, "std": 4.8, "p50": 18.0, "p75": 21.5, "p90": 25.2}
 },
 ("tier_1", "government"): {
 "bed_occupancy_rate": {"mean": 95.2, "std": 5.5, "p50": 96.0, "p75": 98.5, "p90": 99.5},
 "patient_satisfaction_score": {"mean": 6.8, "std": 1.2, "p50": 6.9, "p75": 7.5, "p90": 8.2},
 "revenue_per_bed": {"mean": 8.5, "std": 2.1, "p50": 8.2, "p75": 9.8, "p90": 11.2},
 "accounts_receivable_days": {"mean": 65, "std": 18, "p50": 62, "p75": 75, "p90": 88},
 "ebitda_margin": {"mean": 5.5, "std": 3.2, "p50": 5.0, "p75": 7.8, "p90": 10.5}
 },
 ("tier_2", "private_corporate"): {
 "bed_occupancy_rate": {"mean": 78.2, "std": 9.5, "p50": 79.0, "p75": 84.5, "p90": 89.0},
 "patient_satisfaction_score": {"mean": 7.8, "std": 0.9, "p50": 7.9, "p75": 8.4, "p90": 8.8},
 "revenue_per_bed": {"mean": 18.2, "std": 3.8, "p50": 18.0, "p75": 20.8, "p90": 23.5},
 "accounts_receivable_days": {"mean": 42, "std": 14, "p50": 40, "p75": 50, "p90": 62},
 "ebitda_margin": {"mean": 15.8, "std": 4.2, "p50": 15.5, "p75": 18.5, "p90": 22.0}
 }
 }

 return benchmarks.get((city_tier, hospital_type), benchmarks[("tier_1", "private_corporate")])

 def _get_sample_size(self, city_tier: str, hospital_type: str) -> int:
 """Get realistic sample sizes for benchmark categories"""
 sample_sizes = {
 ("tier_1", "private_corporate"): 15,
 ("tier_1", "government"): 8,
 ("tier_2", "private_corporate"): 12,
 ("tier_2", "private_standalone"): 18,
 ("tier_3", "private_standalone"): 25
 }
 return sample_sizes.get((city_tier, hospital_type), 10)

 def _calculate_percentiles(self, benchmark_data: dict, percentile: int) -> dict:
 """Calculate percentile values from benchmark data"""
 percentile_data = {}

 for metric, stats in benchmark_data.items():
 if isinstance(stats, dict) and f"p{percentile}" in stats:
 percentile_data[metric] = stats[f"p{percentile}"]

 return percentile_data

 async def create_data_collection_tracking(self):
 """Create tables for tracking data collection campaigns"""

 collection_tracking_sql = """
 CREATE TABLE IF NOT EXISTS data_collection_campaigns (
 id VARCHAR PRIMARY KEY,
 campaign_name VARCHAR(255) NOT NULL,
 start_date TIMESTAMP,
 end_date TIMESTAMP,
 status VARCHAR(50),
 target_hospitals INTEGER,
 completed_hospitals INTEGER,
 success_rate DECIMAL(5,2),
 data_quality_average DECIMAL(4,2),
 collection_methods JSON,
 errors JSON,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 );

 CREATE TABLE IF NOT EXISTS hospital_data_collection_log (
 id VARCHAR PRIMARY KEY,
 hospital_id VARCHAR REFERENCES hospitals(id),
 campaign_id VARCHAR REFERENCES data_collection_campaigns(id),
 collection_method VARCHAR(50),
 collection_timestamp TIMESTAMP,
 success BOOLEAN,
 data_quality_score DECIMAL(4,2),
 errors JSON,
 data_summary JSON,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 );

 CREATE INDEX IF NOT EXISTS idx_collection_log_hospital ON hospital_data_collection_log (hospital_id);
 CREATE INDEX IF NOT EXISTS idx_collection_log_campaign ON hospital_data_collection_log (campaign_id);
 CREATE INDEX IF NOT EXISTS idx_collection_log_timestamp ON hospital_data_collection_log (collection_timestamp);
 """

 async with self.engine.begin() as conn:
 for sql in collection_tracking_sql.split(';'):
 if sql.strip():
 await conn.execute(text(sql))

 async def generate_sample_report(self) -> dict:
 """Generate sample benchmark report to validate data"""

 async with self.async_session() as session:
 # Get hospital count by tier
 tier_query = await session.execute(
 text("SELECT city_tier, COUNT(*) as count FROM hospitals GROUP BY city_tier")
 )
 tier_distribution = {row[0]: row[1] for row in tier_query.fetchall()}

 # Get average performance metrics
 perf_query = await session.execute(
 text("""
 SELECT 
 AVG(bed_occupancy_rate) as avg_occupancy,
 AVG(patient_satisfaction_score) as avg_satisfaction,
 AVG(accounts_receivable_days) as avg_ar_days
 FROM performance_metrics pm
 JOIN financial_metrics fm ON pm.hospital_id = fm.hospital_id
 """)
 )

 perf_result = perf_query.fetchone()

 report = {
 "database_status": "initialized",
 "total_hospitals": sum(tier_distribution.values()),
 "tier_distribution": tier_distribution,
 "sample_averages": {
 "bed_occupancy_rate": float(perf_result[0]) if perf_result[0] else 0,
 "patient_satisfaction_score": float(perf_result[1]) if perf_result[1] else 0,
 "accounts_receivable_days": float(perf_result[2]) if perf_result[2] else 0
 },
 "data_timestamp": datetime.utcnow().isoformat()
 }

 return report


async def main():
 """Main function to initialize the benchmark database"""

 # Configure logging
 logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
 )

 # Load configuration
 config = ConfigManager()

 # Initialize database manager
 db_manager = BenchmarkDatabaseManager(config)

 try:
 # Create schema
 await db_manager.create_database_schema()

 # Populate initial data
 await db_manager.populate_initial_data()

 # Create data collection tracking tables
 await db_manager.create_data_collection_tracking()

 # Generate sample report
 report = await db_manager.generate_sample_report()

 print("\n" + "="*60)
 print("HOSPITAL BENCHMARK DATABASE INITIALIZATION COMPLETE")
 print("="*60)
 print(f"Total Hospitals Created: {report['total_hospitals']}")
 print(f"Tier Distribution: {report['tier_distribution']}")
 print(f"Average Bed Occupancy: {report['sample_averages']['bed_occupancy_rate']:.1f}%")
 print(f"Average Patient Satisfaction: {report['sample_averages']['patient_satisfaction_score']:.1f}/10")
 print(f"Average AR Days: {report['sample_averages']['accounts_receivable_days']:.1f}")
 print("="*60)
 print("Ready for benchmark data collection!")

 except Exception as e:
 logging.error(f"Database initialization failed: {str(e)}")
 raise

 finally:
 await db_manager.engine.dispose()


if __name__ == "__main__":
 asyncio.run(main())