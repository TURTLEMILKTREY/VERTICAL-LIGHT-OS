#!/usr/bin/env python3

"""
Hospital Database Integration
============================

Production-ready database layer for hospital intelligence system.
Handles persistence of analysis results for single hospital deployment.
"""

import os
import uuid
import asyncio
import asyncpg
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HospitalAnalysisRecord:
 """Database record for hospital analysis results"""
 id: str
 hospital_name: str
 analysis_date: datetime
 hospital_age: int
 lifecycle_stage: str
 benchmark_target: float
 growth_velocity: str
 analysis_results: Dict[str, Any]
 confidence_score: float
 processing_duration: float
 created_at: datetime

class HospitalDatabase:
 """
 Production database layer for hospital intelligence system
 Optimized for single hospital deployment
 """

 def __init__(self, connection_string: str = None):
 """Initialize database connection"""
 self.connection_string = connection_string or os.getenv(
 'DATABASE_URL', 
 'postgresql://hospital_user:secure_password@localhost:5432/hospital_intelligence'
 )
 self.pool = None

 async def initialize(self):
 """Initialize database connection pool"""
 try:
 self.pool = await asyncpg.create_pool(
 self.connection_string,
 min_size=1,
 max_size=10,
 command_timeout=30
 )
 logger.info("Database connection pool initialized successfully")

 # Create tables if they don't exist
 await self.create_tables()

 except Exception as e:
 logger.error(f"Failed to initialize database: {e}")
 raise

 async def create_tables(self):
 """Create necessary database tables"""
 create_table_sql = """
 CREATE TABLE IF NOT EXISTS hospital_analyses (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 hospital_name VARCHAR(255) NOT NULL,
 analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
 hospital_age INTEGER NOT NULL,
 lifecycle_stage VARCHAR(50) NOT NULL,
 benchmark_target DECIMAL(5,2) NOT NULL,
 growth_velocity VARCHAR(50) NOT NULL,
 analysis_results JSONB NOT NULL,
 confidence_score DECIMAL(3,2) NOT NULL,
 processing_duration DECIMAL(10,3) NOT NULL,
 created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
 );

 CREATE INDEX IF NOT EXISTS idx_hospital_analyses_name_date 
 ON hospital_analyses(hospital_name, analysis_date DESC);

 CREATE INDEX IF NOT EXISTS idx_hospital_analyses_lifecycle 
 ON hospital_analyses(lifecycle_stage);

 CREATE INDEX IF NOT EXISTS idx_hospital_analyses_created 
 ON hospital_analyses(created_at DESC);
 """

 async with self.pool.acquire() as connection:
 await connection.execute(create_table_sql)
 logger.info("Database tables created successfully")

 async def save_analysis(self, analysis_result: Dict[str, Any]) -> str:
 """
 Save hospital analysis results to database

 Args:
 analysis_result: Complete analysis result from hospital intelligence system

 Returns:
 str: Analysis ID for tracking
 """
 try:
 analysis_id = str(uuid.uuid4())

 insert_sql = """
 INSERT INTO hospital_analyses (
 id, hospital_name, hospital_age, lifecycle_stage,
 benchmark_target, growth_velocity, analysis_results,
 confidence_score, processing_duration
 ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
 RETURNING id
 """

 # Extract data from analysis result
 hospital_name = analysis_result.get('hospital_name', 'Unknown Hospital')
 hospital_age = analysis_result.get('hospital_age', 0)
 lifecycle_stage = analysis_result.get('lifecycle_stage', 'UNKNOWN')
 benchmark_target = float(analysis_result.get('benchmark_target', 0.0))
 growth_velocity = analysis_result.get('growth_velocity', 'UNKNOWN')
 confidence_score = float(analysis_result.get('confidence_score', 0.0))
 processing_duration = float(analysis_result.get('processing_duration', 0.0))

 async with self.pool.acquire() as connection:
 result = await connection.fetchval(
 insert_sql,
 analysis_id,
 hospital_name,
 hospital_age,
 lifecycle_stage,
 benchmark_target,
 growth_velocity,
 json.dumps(analysis_result),
 confidence_score,
 processing_duration
 )

 logger.info(f"Analysis saved successfully: {analysis_id}")
 return result

 except Exception as e:
 logger.error(f"Failed to save analysis: {e}")
 raise

 async def get_hospital_history(self, hospital_name: str, limit: int = 50) -> List[HospitalAnalysisRecord]:
 """
 Get historical analyses for a hospital

 Args:
 hospital_name: Name of the hospital
 limit: Maximum number of records to return

 Returns:
 List of historical analysis records
 """
 try:
 select_sql = """
 SELECT 
 id, hospital_name, analysis_date, hospital_age,
 lifecycle_stage, benchmark_target, growth_velocity,
 analysis_results, confidence_score, processing_duration,
 created_at
 FROM hospital_analyses
 WHERE hospital_name = $1
 ORDER BY analysis_date DESC
 LIMIT $2
 """

 async with self.pool.acquire() as connection:
 rows = await connection.fetch(select_sql, hospital_name, limit)

 records = []
 for row in rows:
 record = HospitalAnalysisRecord(
 id=str(row['id']),
 hospital_name=row['hospital_name'],
 analysis_date=row['analysis_date'],
 hospital_age=row['hospital_age'],
 lifecycle_stage=row['lifecycle_stage'],
 benchmark_target=float(row['benchmark_target']),
 growth_velocity=row['growth_velocity'],
 analysis_results=row['analysis_results'],
 confidence_score=float(row['confidence_score']),
 processing_duration=float(row['processing_duration']),
 created_at=row['created_at']
 )
 records.append(record)

 logger.info(f"Retrieved {len(records)} historical records for {hospital_name}")
 return records

 except Exception as e:
 logger.error(f"Failed to retrieve hospital history: {e}")
 raise

 async def get_analysis_by_id(self, analysis_id: str) -> Optional[HospitalAnalysisRecord]:
 """Get specific analysis by ID"""
 try:
 select_sql = """
 SELECT 
 id, hospital_name, analysis_date, hospital_age,
 lifecycle_stage, benchmark_target, growth_velocity,
 analysis_results, confidence_score, processing_duration,
 created_at
 FROM hospital_analyses
 WHERE id = $1
 """

 async with self.pool.acquire() as connection:
 row = await connection.fetchrow(select_sql, analysis_id)

 if row:
 return HospitalAnalysisRecord(
 id=str(row['id']),
 hospital_name=row['hospital_name'],
 analysis_date=row['analysis_date'],
 hospital_age=row['hospital_age'],
 lifecycle_stage=row['lifecycle_stage'],
 benchmark_target=float(row['benchmark_target']),
 growth_velocity=row['growth_velocity'],
 analysis_results=row['analysis_results'],
 confidence_score=float(row['confidence_score']),
 processing_duration=float(row['processing_duration']),
 created_at=row['created_at']
 )

 return None

 except Exception as e:
 logger.error(f"Failed to retrieve analysis {analysis_id}: {e}")
 raise

 async def get_analysis_statistics(self) -> Dict[str, Any]:
 """Get database statistics for monitoring"""
 try:
 stats_sql = """
 SELECT 
 COUNT(*) as total_analyses,
 COUNT(DISTINCT hospital_name) as unique_hospitals,
 AVG(confidence_score) as avg_confidence,
 AVG(processing_duration) as avg_processing_time,
 MAX(created_at) as last_analysis
 FROM hospital_analyses
 """

 stage_stats_sql = """
 SELECT 
 lifecycle_stage,
 COUNT(*) as count,
 AVG(benchmark_target) as avg_target
 FROM hospital_analyses
 GROUP BY lifecycle_stage
 ORDER BY count DESC
 """

 async with self.pool.acquire() as connection:
 # Get overall stats
 overall_stats = await connection.fetchrow(stats_sql)

 # Get stage distribution
 stage_stats = await connection.fetch(stage_stats_sql)

 statistics = {
 "overall": {
 "total_analyses": overall_stats['total_analyses'],
 "unique_hospitals": overall_stats['unique_hospitals'],
 "average_confidence": float(overall_stats['avg_confidence'] or 0),
 "average_processing_time": float(overall_stats['avg_processing_time'] or 0),
 "last_analysis": overall_stats['last_analysis']
 },
 "stage_distribution": [
 {
 "stage": row['lifecycle_stage'],
 "count": row['count'],
 "average_target": float(row['avg_target'] or 0)
 }
 for row in stage_stats
 ]
 }

 return statistics

 except Exception as e:
 logger.error(f"Failed to get statistics: {e}")
 raise

 async def close(self):
 """Close database connection pool"""
 if self.pool:
 await self.pool.close()
 logger.info("Database connection pool closed")

# Global database instance for the application
hospital_db = HospitalDatabase()

async def initialize_database():
 """Initialize the global database instance"""
 await hospital_db.initialize()

async def get_database() -> HospitalDatabase:
 """Get the database instance"""
 if not hospital_db.pool:
 await hospital_db.initialize()
 return hospital_db

# Example usage
async def main():
 """Example usage of hospital database"""
 try:
 # Initialize database
 db = HospitalDatabase()
 await db.initialize()

 # Example analysis result
 sample_analysis = {
 "hospital_name": "Memorial Hospital",
 "hospital_age": 15,
 "lifecycle_stage": "GROWTH",
 "benchmark_target": 22.5,
 "growth_velocity": "ACCELERATING",
 "confidence_score": 0.92,
 "processing_duration": 1.245,
 "analysis_results": {
 "revenue_optimization": "High potential for revenue growth",
 "operational_efficiency": "Strong performance metrics",
 "strategic_recommendations": ["Expand cardiology services", "Invest in digital health"]
 }
 }

 # Save analysis
 analysis_id = await db.save_analysis(sample_analysis)
 print(f"Saved analysis: {analysis_id}")

 # Get hospital history
 history = await db.get_hospital_history("Memorial Hospital")
 print(f"Found {len(history)} historical analyses")

 # Get statistics
 stats = await db.get_analysis_statistics()
 print(f"Database statistics: {stats}")

 await db.close()

 except Exception as e:
 print(f"Database example failed: {e}")

if __name__ == "__main__":
 asyncio.run(main())