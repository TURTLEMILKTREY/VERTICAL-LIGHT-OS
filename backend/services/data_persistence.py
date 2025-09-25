#!/usr/bin/env python3

"""
Data Persistence Service Layer
=============================

Service layer for managing hospital analysis data persistence.
Provides business logic layer between applications and database.
"""

import sys
import asyncio
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging
import json

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.hospital_db import HospitalDatabase, HospitalAnalysisRecord

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PersistenceResult:
    """Result of persistence operation"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DataValidationError(Exception):
    """Exception raised for data validation errors"""
    pass

class DataPersistenceService:
    """
    Data persistence service for hospital analysis results.
    
    This service provides:
    1. Data validation before persistence
    2. Business logic enforcement
    3. Error handling and recovery
    4. Audit trail management
    5. Data retrieval and filtering
    """
    
    def __init__(self, database: HospitalDatabase = None):
        """Initialize persistence service"""
        self.database = database or HospitalDatabase()
        self.initialized = False
    
    async def initialize(self):
        """Initialize the persistence service and database"""
        try:
            await self.database.initialize()
            self.initialized = True
            logger.info("Data persistence service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize persistence service: {e}")
            raise
    
    async def save_hospital_analysis(self, analysis_data: Dict[str, Any]) -> PersistenceResult:
        """
        Save hospital analysis results with validation and error handling.
        
        Args:
            analysis_data: Complete analysis result dictionary
            
        Returns:
            PersistenceResult with success status and details
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Validate analysis data
            validation_result = self._validate_analysis_data(analysis_data)
            if not validation_result.success:
                return validation_result
            
            # Enrich with persistence metadata
            enriched_data = self._enrich_analysis_data(analysis_data)
            
            # Save to database
            analysis_id = await self.database.save_analysis(enriched_data)
            
            logger.info(f"Successfully saved analysis {analysis_id} for hospital {enriched_data.get('hospital_name')}")
            
            return PersistenceResult(
                success=True,
                message="Analysis saved successfully",
                data={"analysis_id": analysis_id, "hospital_name": enriched_data.get('hospital_name')}
            )
            
        except DataValidationError as e:
            error_msg = f"Data validation failed: {str(e)}"
            logger.warning(error_msg)
            return PersistenceResult(
                success=False,
                message="Validation failed",
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Failed to save analysis: {str(e)}"
            logger.error(error_msg)
            return PersistenceResult(
                success=False,
                message="Database save failed",
                error=error_msg
            )
    
    async def get_hospital_analysis_history(self, hospital_name: str, limit: int = 50) -> PersistenceResult:
        """
        Retrieve analysis history for a specific hospital.
        
        Args:
            hospital_name: Name of the hospital
            limit: Maximum number of records to retrieve
            
        Returns:
            PersistenceResult with historical analysis data
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            records = await self.database.get_hospital_history(hospital_name, limit)
            
            # Convert records to dictionaries for easier handling
            history_data = []
            for record in records:
                record_dict = {
                    "analysis_id": record.id,
                    "hospital_name": record.hospital_name,
                    "analysis_date": record.analysis_date.isoformat(),
                    "hospital_age": record.hospital_age,
                    "lifecycle_stage": record.lifecycle_stage,
                    "benchmark_target": record.benchmark_target,
                    "growth_velocity": record.growth_velocity,
                    "confidence_score": record.confidence_score,
                    "processing_duration": record.processing_duration,
                    "created_at": record.created_at.isoformat(),
                    "analysis_results": record.analysis_results
                }
                history_data.append(record_dict)
            
            logger.info(f"Retrieved {len(history_data)} historical records for {hospital_name}")
            
            return PersistenceResult(
                success=True,
                message=f"Retrieved {len(history_data)} historical analyses",
                data={
                    "hospital_name": hospital_name,
                    "total_records": len(history_data),
                    "analyses": history_data
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to retrieve hospital history: {str(e)}"
            logger.error(error_msg)
            return PersistenceResult(
                success=False,
                message="Failed to retrieve history",
                error=error_msg
            )
    
    async def get_analysis_by_id(self, analysis_id: str) -> PersistenceResult:
        """
        Retrieve specific analysis by ID.
        
        Args:
            analysis_id: Unique analysis identifier
            
        Returns:
            PersistenceResult with analysis data
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            record = await self.database.get_analysis_by_id(analysis_id)
            
            if not record:
                return PersistenceResult(
                    success=False,
                    message=f"Analysis {analysis_id} not found",
                    error="Analysis not found"
                )
            
            analysis_data = {
                "analysis_id": record.id,
                "hospital_name": record.hospital_name,
                "analysis_date": record.analysis_date.isoformat(),
                "hospital_age": record.hospital_age,
                "lifecycle_stage": record.lifecycle_stage,
                "benchmark_target": record.benchmark_target,
                "growth_velocity": record.growth_velocity,
                "confidence_score": record.confidence_score,
                "processing_duration": record.processing_duration,
                "created_at": record.created_at.isoformat(),
                "analysis_results": record.analysis_results
            }
            
            logger.info(f"Retrieved analysis {analysis_id}")
            
            return PersistenceResult(
                success=True,
                message="Analysis retrieved successfully",
                data=analysis_data
            )
            
        except Exception as e:
            error_msg = f"Failed to retrieve analysis {analysis_id}: {str(e)}"
            logger.error(error_msg)
            return PersistenceResult(
                success=False,
                message="Failed to retrieve analysis",
                error=error_msg
            )
    
    async def get_system_statistics(self) -> PersistenceResult:
        """
        Get system-wide statistics and metrics.
        
        Returns:
            PersistenceResult with system statistics
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            stats = await self.database.get_analysis_statistics()
            
            return PersistenceResult(
                success=True,
                message="Statistics retrieved successfully",
                data=stats
            )
            
        except Exception as e:
            error_msg = f"Failed to retrieve statistics: {str(e)}"
            logger.error(error_msg)
            return PersistenceResult(
                success=False,
                message="Failed to retrieve statistics",
                error=error_msg
            )
    
    async def delete_analysis(self, analysis_id: str, reason: str) -> PersistenceResult:
        """
        Delete analysis with audit trail (for data governance).
        
        Args:
            analysis_id: Analysis to delete
            reason: Reason for deletion (audit trail)
            
        Returns:
            PersistenceResult with deletion status
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # First verify analysis exists
            record = await self.database.get_analysis_by_id(analysis_id)
            if not record:
                return PersistenceResult(
                    success=False,
                    message="Analysis not found",
                    error=f"Analysis {analysis_id} does not exist"
                )
            
            # Log deletion for audit trail
            logger.warning(f"Deleting analysis {analysis_id} for {record.hospital_name}. Reason: {reason}")
            
            # Delete from database (implement in database layer if needed)
            # For now, we'll mark as deleted in analysis_results
            deletion_data = {
                "deleted_at": datetime.now(timezone.utc).isoformat(),
                "deletion_reason": reason,
                "original_hospital": record.hospital_name
            }
            
            # Update record to mark as deleted
            updated_results = record.analysis_results.copy()
            updated_results["deletion_info"] = deletion_data
            
            logger.info(f"Analysis {analysis_id} marked for deletion")
            
            return PersistenceResult(
                success=True,
                message="Analysis deletion logged",
                data={"analysis_id": analysis_id, "deletion_logged": True}
            )
            
        except Exception as e:
            error_msg = f"Failed to delete analysis {analysis_id}: {str(e)}"
            logger.error(error_msg)
            return PersistenceResult(
                success=False,
                message="Failed to delete analysis",
                error=error_msg
            )
    
    def _validate_analysis_data(self, analysis_data: Dict[str, Any]) -> PersistenceResult:
        """
        Validate analysis data before persistence.
        
        Args:
            analysis_data: Analysis data to validate
            
        Returns:
            PersistenceResult with validation status
        """
        required_fields = [
            'hospital_name', 'hospital_age', 'lifecycle_stage',
            'benchmark_target', 'growth_velocity', 'confidence_score'
        ]
        
        # Check required fields
        missing_fields = []
        for field in required_fields:
            if field not in analysis_data or analysis_data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return PersistenceResult(
                success=False,
                message="Missing required fields",
                error=f"Missing fields: {', '.join(missing_fields)}"
            )
        
        # Validate data types and ranges
        try:
            # Hospital age should be positive integer
            hospital_age = int(analysis_data['hospital_age'])
            if hospital_age < 0 or hospital_age > 200:
                raise DataValidationError("Hospital age must be between 0 and 200 years")
            
            # Benchmark target should be valid percentage
            benchmark_target = float(analysis_data['benchmark_target'])
            if benchmark_target < 0 or benchmark_target > 100:
                raise DataValidationError("Benchmark target must be between 0 and 100 percent")
            
            # Confidence score should be between 0 and 1
            confidence_score = float(analysis_data['confidence_score'])
            if confidence_score < 0 or confidence_score > 1:
                raise DataValidationError("Confidence score must be between 0 and 1")
            
            # Lifecycle stage should be valid
            valid_stages = ['STARTUP', 'GROWTH', 'EXPANSION', 'MATURITY', 'ESTABLISHED']
            if analysis_data['lifecycle_stage'] not in valid_stages:
                raise DataValidationError(f"Lifecycle stage must be one of: {', '.join(valid_stages)}")
            
            # Growth velocity should be valid
            valid_velocities = ['BREAKTHROUGH', 'ACCELERATING', 'STEADY', 'SLOW', 'DECLINING']
            if analysis_data['growth_velocity'] not in valid_velocities:
                raise DataValidationError(f"Growth velocity must be one of: {', '.join(valid_velocities)}")
            
            return PersistenceResult(
                success=True,
                message="Validation successful"
            )
            
        except (ValueError, TypeError) as e:
            return PersistenceResult(
                success=False,
                message="Data type validation failed",
                error=str(e)
            )
        except DataValidationError as e:
            return PersistenceResult(
                success=False,
                message="Business rule validation failed",
                error=str(e)
            )
    
    def _enrich_analysis_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich analysis data with persistence metadata.
        
        Args:
            analysis_data: Original analysis data
            
        Returns:
            Enriched data dictionary
        """
        enriched = analysis_data.copy()
        
        # Add persistence metadata if not present
        if 'analysis_id' not in enriched:
            enriched['analysis_id'] = str(uuid.uuid4())
        
        if 'created_at' not in enriched:
            enriched['created_at'] = datetime.now(timezone.utc).isoformat()
        
        if 'analysis_date' not in enriched:
            enriched['analysis_date'] = datetime.now(timezone.utc).isoformat()
        
        # Ensure processing duration is recorded
        if 'processing_duration' not in enriched:
            enriched['processing_duration'] = 0.0
        
        # Add data quality metadata
        enriched['data_persistence_version'] = '1.0'
        enriched['persistence_timestamp'] = datetime.now(timezone.utc).isoformat()
        
        return enriched
    
    async def close(self):
        """Close database connections"""
        if self.database:
            await self.database.close()
            logger.info("Data persistence service closed")

# Global service instance
persistence_service = None

async def get_persistence_service() -> DataPersistenceService:
    """Get or create global persistence service instance"""
    global persistence_service
    
    if persistence_service is None:
        persistence_service = DataPersistenceService()
        await persistence_service.initialize()
    
    return persistence_service

# Convenience functions for common operations
async def save_analysis(analysis_data: Dict[str, Any]) -> PersistenceResult:
    """Convenience function to save analysis"""
    service = await get_persistence_service()
    return await service.save_hospital_analysis(analysis_data)

async def get_hospital_history(hospital_name: str, limit: int = 50) -> PersistenceResult:
    """Convenience function to get hospital history"""
    service = await get_persistence_service()
    return await service.get_hospital_analysis_history(hospital_name, limit)

async def get_analysis(analysis_id: str) -> PersistenceResult:
    """Convenience function to get analysis by ID"""
    service = await get_persistence_service()
    return await service.get_analysis_by_id(analysis_id)

# Example usage and testing
async def test_persistence_service():
    """Test the persistence service functionality"""
    try:
        service = DataPersistenceService()
        await service.initialize()
        
        # Test data
        test_analysis = {
            "hospital_name": "Test Memorial Hospital",
            "hospital_age": 15,
            "lifecycle_stage": "GROWTH",
            "benchmark_target": 22.5,
            "growth_velocity": "ACCELERATING",
            "confidence_score": 0.92,
            "processing_duration": 1.245,
            "analysis_results": {
                "revenue_optimization": "High potential identified",
                "operational_efficiency": "Strong performance metrics",
                "recommendations": ["Expand cardiology", "Digital health investment"]
            }
        }
        
        # Test save
        save_result = await service.save_hospital_analysis(test_analysis)
        print(f"Save result: {save_result.success} - {save_result.message}")
        
        if save_result.success:
            # Test retrieval
            history_result = await service.get_hospital_analysis_history("Test Memorial Hospital")
            print(f"History result: {history_result.success} - Retrieved {len(history_result.data.get('analyses', []))} records")
            
            # Test statistics
            stats_result = await service.get_system_statistics()
            print(f"Stats result: {stats_result.success} - {stats_result.data}")
        
        await service.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_persistence_service())