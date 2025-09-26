#!/usr/bin/env python3

"""
Hospital Intelligence REST API
==============================

Production-ready FastAPI implementation for hospital intelligence system.
Designed for single hospital deployment with enterprise-grade features.
"""

import sys
import os
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import logging
from fastapi import FastAPI, HTTPException, Header, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

# Import our hospital intelligence system
from applications.hospital_intelligence.working_hospital_system import HospitalIntelligenceSystem, HospitalAnalysisRequest
from database.hospital_db import get_database, HospitalDatabase

# Setup logging
logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
 handlers=[
 logging.FileHandler('hospital_api.log'),
 logging.StreamHandler()
 ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
 title="Hospital Intelligence API",
 description="Production-ready API for hospital lifecycle-aware benchmarking and intelligence analysis",
 version="1.0.0",
 docs_url="/docs",
 redoc_url="/redoc"
)

# Security configuration
HOSPITAL_API_KEY = os.getenv('HOSPITAL_API_KEY', 'hospital_secure_key_2025_production')
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "hospital.internal", "*.hospital.local"]

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
app.add_middleware(
 CORSMiddleware,
 allow_origins=["https://hospital.internal", "https://localhost:3000"], # Adjust for hospital environment
 allow_credentials=True,
 allow_methods=["GET", "POST"],
 allow_headers=["*"],
)

# Initialize hospital intelligence system
hospital_system = HospitalIntelligenceSystem()

# API Models
class HospitalAnalysisAPIRequest(BaseModel):
 """API request model for hospital analysis"""

 # Basic hospital information
 hospital_name: str = Field(..., min_length=1, max_length=255, description="Hospital name")
 hospital_age: int = Field(..., ge=0, le=200, description="Hospital age in years")

 # Financial metrics
 annual_revenue: float = Field(..., gt=0, description="Annual revenue in USD")
 annual_operating_expenses: float = Field(..., gt=0, description="Annual operating expenses")
 net_income: float = Field(..., description="Net income (can be negative)")
 total_assets: float = Field(..., gt=0, description="Total assets")
 total_liabilities: float = Field(..., ge=0, description="Total liabilities")

 # Operational metrics
 total_beds: int = Field(..., gt=0, le=10000, description="Total number of beds")
 occupied_beds: int = Field(..., ge=0, description="Currently occupied beds")
 annual_admissions: int = Field(..., ge=0, description="Annual patient admissions")
 average_length_of_stay: float = Field(..., gt=0, le=365, description="Average length of stay in days")
 emergency_visits: int = Field(..., ge=0, description="Annual emergency department visits")
 surgical_cases: int = Field(..., ge=0, description="Annual surgical cases")

 # Quality and compliance
 patient_satisfaction_score: float = Field(..., ge=0, le=100, description="Patient satisfaction score (0-100)")
 readmission_rate: float = Field(..., ge=0, le=100, description="30-day readmission rate (%)")
 infection_rate: float = Field(..., ge=0, le=100, description="Hospital-acquired infection rate (%)")
 mortality_rate: float = Field(..., ge=0, le=100, description="In-hospital mortality rate (%)")

 # Staffing
 total_staff: int = Field(..., gt=0, description="Total number of staff")
 physicians: int = Field(..., gt=0, description="Number of physicians")
 nurses: int = Field(..., gt=0, description="Number of nurses")
 staff_turnover_rate: float = Field(..., ge=0, le=100, description="Annual staff turnover rate (%)")

 # Technology and infrastructure
 technology_investment: float = Field(..., ge=0, description="Annual technology investment")
 emr_implementation_level: float = Field(..., ge=0, le=100, description="EMR implementation level (%)")

 # Market and competition
 market_share: float = Field(..., ge=0, le=100, description="Local market share (%)")
 number_of_competitors: int = Field(..., ge=0, description="Number of competing hospitals")

 # Additional optional fields
 specialty_services: Optional[List[str]] = Field(None, description="List of specialty services offered")
 accreditations: Optional[List[str]] = Field(None, description="List of accreditations")

 @validator('occupied_beds')
 def occupied_beds_must_not_exceed_total(cls, v, values):
 if 'total_beds' in values and v > values['total_beds']:
 raise ValueError('Occupied beds cannot exceed total beds')
 return v

class HospitalAnalysisAPIResponse(BaseModel):
 """API response model for hospital analysis"""

 # Analysis metadata
 analysis_id: str = Field(..., description="Unique analysis identifier")
 analysis_timestamp: datetime = Field(..., description="Analysis completion timestamp")

 # Core results
 lifecycle_stage: str = Field(..., description="Hospital lifecycle stage")
 benchmark_target: float = Field(..., description="Intelligent benchmark target (%)")
 growth_velocity: str = Field(..., description="Growth velocity classification")

 # Analysis details
 confidence_score: float = Field(..., description="Analysis confidence score (0.0-1.0)")
 processing_duration: float = Field(..., description="Processing time in seconds")
 data_quality_score: float = Field(..., description="Input data quality score (0.0-1.0)")

 # Strategic insights
 strategic_recommendations: List[str] = Field(..., description="Strategic recommendations")
 growth_opportunities: List[str] = Field(..., description="Identified growth opportunities")
 risk_factors: List[str] = Field(..., description="Identified risk factors")

 # Benchmarking results
 performance_metrics: Dict[str, Any] = Field(..., description="Detailed performance metrics")
 comparative_analysis: Dict[str, Any] = Field(..., description="Comparative analysis results")

 # System metadata
 api_version: str = Field(default="1.0.0", description="API version")
 hospital_name: str = Field(..., description="Hospital name from request")

class AnalysisHistoryResponse(BaseModel):
 """Response model for analysis history"""

 analyses: List[Dict[str, Any]] = Field(..., description="Historical analyses")
 total_count: int = Field(..., description="Total number of analyses")
 hospital_name: str = Field(..., description="Hospital name")

class HealthCheckResponse(BaseModel):
 """Health check response model"""

 status: str = Field(..., description="API health status")
 timestamp: datetime = Field(..., description="Health check timestamp")
 version: str = Field(..., description="API version")
 database_status: str = Field(..., description="Database connection status")
 components: Dict[str, str] = Field(..., description="Component health status")

# Authentication dependency
async def verify_api_key(x_api_key: str = Header(alias="X-API-Key")):
 """Verify API key authentication"""
 if x_api_key != HOSPITAL_API_KEY:
 logger.warning(f"Invalid API key attempted: {x_api_key[:10]}...")
 raise HTTPException(
 status_code=status.HTTP_401_UNAUTHORIZED,
 detail="Invalid API key",
 headers={"WWW-Authenticate": "ApiKey"},
 )
 return True

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
 """Log all API requests for audit trail"""
 start_time = datetime.now(timezone.utc)

 # Generate request ID for tracking
 request_id = str(uuid.uuid4())

 # Log request
 logger.info(f"Request {request_id}: {request.method} {request.url}")

 # Process request
 response = await call_next(request)

 # Calculate processing time
 processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()

 # Log response
 logger.info(f"Request {request_id}: Completed in {processing_time:.3f}s with status {response.status_code}")

 # Add headers for tracking
 response.headers["X-Request-ID"] = request_id
 response.headers["X-Processing-Time"] = str(processing_time)

 return response

# API Endpoints

@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
 """
 System health check endpoint
 Returns the health status of the API and its components
 """
 try:
 # Check database connectivity
 db = await get_database()
 database_status = "healthy" if db.pool else "error"

 # Check system components
 components = {
 "hospital_intelligence_engine": "healthy",
 "database": database_status,
 "api": "healthy"
 }

 overall_status = "healthy" if all(status == "healthy" for status in components.values()) else "degraded"

 return HealthCheckResponse(
 status=overall_status,
 timestamp=datetime.now(timezone.utc),
 version="1.0.0",
 database_status=database_status,
 components=components
 )

 except Exception as e:
 logger.error(f"Health check failed: {e}")
 raise HTTPException(
 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
 detail="Service health check failed"
 )

@app.post("/analyze", response_model=HospitalAnalysisAPIResponse, tags=["Analysis"])
async def analyze_hospital(
 request: HospitalAnalysisAPIRequest,
 authenticated: bool = Depends(verify_api_key)
):
 """
 Perform comprehensive hospital intelligence analysis

 This endpoint analyzes hospital data using the lifecycle-aware benchmarking engine
 and returns strategic insights, benchmark targets, and recommendations.
 """
 try:
 start_time = datetime.now(timezone.utc)
 analysis_id = str(uuid.uuid4())

 logger.info(f"Starting analysis {analysis_id} for hospital: {request.hospital_name}")

 # Convert API request to internal format
 analysis_request = HospitalAnalysisRequest(
 hospital_name=request.hospital_name,
 hospital_age=request.hospital_age,
 annual_revenue=request.annual_revenue,
 annual_operating_expenses=request.annual_operating_expenses,
 net_income=request.net_income,
 total_assets=request.total_assets,
 total_liabilities=request.total_liabilities,
 total_beds=request.total_beds,
 occupied_beds=request.occupied_beds,
 annual_admissions=request.annual_admissions,
 average_length_of_stay=request.average_length_of_stay,
 emergency_visits=request.emergency_visits,
 surgical_cases=request.surgical_cases,
 patient_satisfaction_score=request.patient_satisfaction_score,
 readmission_rate=request.readmission_rate,
 infection_rate=request.infection_rate,
 mortality_rate=request.mortality_rate,
 total_staff=request.total_staff,
 physicians=request.physicians,
 nurses=request.nurses,
 staff_turnover_rate=request.staff_turnover_rate,
 technology_investment=request.technology_investment,
 emr_implementation_level=request.emr_implementation_level,
 market_share=request.market_share,
 number_of_competitors=request.number_of_competitors,
 specialty_services=request.specialty_services or [],
 accreditations=request.accreditations or []
 )

 # Perform analysis using hospital intelligence system
 analysis_result = await hospital_system.analyze_hospital_comprehensive(analysis_request.dict())

 # Calculate processing time
 processing_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

 # Add metadata to result
 analysis_result.update({
 "analysis_id": analysis_id,
 "processing_duration": processing_duration,
 "analysis_timestamp": datetime.now(timezone.utc).isoformat()
 })

 # Save to database
 try:
 db = await get_database()
 saved_id = await db.save_analysis(analysis_result)
 logger.info(f"Analysis {analysis_id} saved to database: {saved_id}")
 except Exception as db_error:
 logger.error(f"Failed to save analysis to database: {db_error}")
 # Continue without failing the request

 # Create API response
 response = HospitalAnalysisAPIResponse(
 analysis_id=analysis_id,
 analysis_timestamp=datetime.now(timezone.utc),
 lifecycle_stage=analysis_result.get("lifecycle_stage", "UNKNOWN"),
 benchmark_target=analysis_result.get("benchmark_target", 0.0),
 growth_velocity=analysis_result.get("growth_velocity", "UNKNOWN"),
 confidence_score=analysis_result.get("confidence_score", 0.0),
 processing_duration=processing_duration,
 data_quality_score=analysis_result.get("data_quality_score", 0.0),
 strategic_recommendations=analysis_result.get("strategic_recommendations", []),
 growth_opportunities=analysis_result.get("growth_opportunities", []),
 risk_factors=analysis_result.get("risk_factors", []),
 performance_metrics=analysis_result.get("performance_metrics", {}),
 comparative_analysis=analysis_result.get("comparative_analysis", {}),
 hospital_name=request.hospital_name
 )

 logger.info(f"Analysis {analysis_id} completed successfully in {processing_duration:.3f}s")
 return response

 except Exception as e:
 logger.error(f"Analysis failed for {request.hospital_name}: {e}")
 raise HTTPException(
 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
 detail=f"Analysis failed: {str(e)}"
 )

@app.get("/analysis/{analysis_id}", response_model=HospitalAnalysisAPIResponse, tags=["Analysis"])
async def get_analysis_by_id(
 analysis_id: str,
 authenticated: bool = Depends(verify_api_key)
):
 """
 Retrieve a specific analysis by its ID
 """
 try:
 db = await get_database()
 analysis_record = await db.get_analysis_by_id(analysis_id)

 if not analysis_record:
 raise HTTPException(
 status_code=status.HTTP_404_NOT_FOUND,
 detail=f"Analysis {analysis_id} not found"
 )

 # Convert database record to API response
 response = HospitalAnalysisAPIResponse(
 analysis_id=analysis_record.id,
 analysis_timestamp=analysis_record.analysis_date,
 lifecycle_stage=analysis_record.lifecycle_stage,
 benchmark_target=analysis_record.benchmark_target,
 growth_velocity=analysis_record.growth_velocity,
 confidence_score=analysis_record.confidence_score,
 processing_duration=analysis_record.processing_duration,
 data_quality_score=analysis_record.analysis_results.get("data_quality_score", 0.0),
 strategic_recommendations=analysis_record.analysis_results.get("strategic_recommendations", []),
 growth_opportunities=analysis_record.analysis_results.get("growth_opportunities", []),
 risk_factors=analysis_record.analysis_results.get("risk_factors", []),
 performance_metrics=analysis_record.analysis_results.get("performance_metrics", {}),
 comparative_analysis=analysis_record.analysis_results.get("comparative_analysis", {}),
 hospital_name=analysis_record.hospital_name
 )

 return response

 except HTTPException:
 raise
 except Exception as e:
 logger.error(f"Failed to retrieve analysis {analysis_id}: {e}")
 raise HTTPException(
 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
 detail="Failed to retrieve analysis"
 )

@app.get("/hospital/{hospital_name}/history", response_model=AnalysisHistoryResponse, tags=["Analysis"])
async def get_hospital_history(
 hospital_name: str,
 limit: int = 50,
 authenticated: bool = Depends(verify_api_key)
):
 """
 Get analysis history for a specific hospital
 """
 try:
 db = await get_database()
 history_records = await db.get_hospital_history(hospital_name, limit)

 analyses = []
 for record in history_records:
 analyses.append({
 "analysis_id": record.id,
 "analysis_date": record.analysis_date.isoformat(),
 "lifecycle_stage": record.lifecycle_stage,
 "benchmark_target": record.benchmark_target,
 "growth_velocity": record.growth_velocity,
 "confidence_score": record.confidence_score,
 "processing_duration": record.processing_duration
 })

 return AnalysisHistoryResponse(
 analyses=analyses,
 total_count=len(analyses),
 hospital_name=hospital_name
 )

 except Exception as e:
 logger.error(f"Failed to retrieve history for {hospital_name}: {e}")
 raise HTTPException(
 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
 detail="Failed to retrieve hospital history"
 )

@app.get("/statistics", tags=["System"])
async def get_system_statistics(authenticated: bool = Depends(verify_api_key)):
 """
 Get system-wide statistics and metrics
 """
 try:
 db = await get_database()
 stats = await db.get_analysis_statistics()

 return {
 "statistics": stats,
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "api_version": "1.0.0"
 }

 except Exception as e:
 logger.error(f"Failed to retrieve statistics: {e}")
 raise HTTPException(
 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
 detail="Failed to retrieve statistics"
 )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
 """Custom HTTP exception handler"""
 logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
 return JSONResponse(
 status_code=exc.status_code,
 content={
 "error": exc.detail,
 "status_code": exc.status_code,
 "timestamp": datetime.now(timezone.utc).isoformat()
 }
 )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
 """General exception handler"""
 logger.error(f"Unhandled exception: {exc} - {request.url}")
 return JSONResponse(
 status_code=500,
 content={
 "error": "Internal server error",
 "status_code": 500,
 "timestamp": datetime.now(timezone.utc).isoformat()
 }
 )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
 """Initialize system on startup"""
 logger.info("Starting Hospital Intelligence API")
 try:
 # Initialize database
 db = await get_database()
 logger.info("Database connection established")
 except Exception as e:
 logger.error(f"Failed to initialize database: {e}")
 raise

@app.on_event("shutdown")
async def shutdown_event():
 """Cleanup on shutdown"""
 logger.info("Shutting down Hospital Intelligence API")
 try:
 from database.hospital_db import hospital_db
 await hospital_db.close()
 logger.info("Database connections closed")
 except Exception as e:
 logger.error(f"Error during shutdown: {e}")

# Production server configuration
def create_production_app():
 """Create production-configured app"""
 return app

if __name__ == "__main__":
 # Development server
 uvicorn.run(
 "hospital_analysis_api:app",
 host="0.0.0.0",
 port=8000,
 reload=True,
 log_level="info",
 access_log=True
 )