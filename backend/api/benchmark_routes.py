"""
Hospital Benchmark API Routes
RESTful API endpoints for hospital benchmark data collection and analysis
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import pandas as pd
import io
import json

from ..models.hospital_benchmarks import (
    Hospital, PerformanceMetrics, FinancialMetrics, BenchmarkStandards,
    HospitalCreate, PerformanceMetricsCreate, FinancialMetricsCreate,
    BenchmarkQuery, BenchmarkResult, CityTier, HospitalType, SpecialtyType
)
from ..services.benchmark_data_collection import HospitalDataCollector, BenchmarkAnalyzer
from ..config.advanced_config_manager import ConfigManager
from ..services.shared.error_handling import ApplicationError


router = APIRouter(prefix="/api/v1/benchmarks", tags=["Hospital Benchmarks"])


# Dependency injection
async def get_db_session():
    # This would be implemented with actual database session
    pass

async def get_config():
    return ConfigManager()


# Response Models

class DataCollectionStatus(BaseModel):
    """Data collection campaign status"""
    campaign_id: str
    status: str  # "running", "completed", "failed"
    progress_percentage: float
    hospitals_processed: int
    hospitals_total: int
    estimated_completion: Optional[datetime]
    errors: List[str]


class BenchmarkSummary(BaseModel):
    """Benchmark analysis summary"""
    total_hospitals: int
    data_coverage_percentage: float
    last_updated: datetime
    tier_distribution: Dict[str, int]
    specialty_coverage: Dict[str, int]
    data_quality_score: float


class HospitalBenchmarkComparison(BaseModel):
    """Hospital performance vs benchmark comparison"""
    hospital_id: str
    hospital_name: str
    city_tier: str
    hospital_type: str
    
    performance_scores: Dict[str, float]
    benchmark_percentiles: Dict[str, int]
    improvement_opportunities: List[Dict[str, Any]]
    peer_ranking: Optional[int]
    total_peers: Optional[int]


# Data Collection Endpoints

@router.post("/hospitals/bulk-create")
async def create_target_hospitals(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    config: ConfigManager = Depends(get_config)
):
    """Create target hospital list for benchmark data collection"""
    
    try:
        collector = HospitalDataCollector(db, config)
        
        # Get target hospitals asynchronously
        background_tasks.add_task(_execute_hospital_creation, collector)
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Hospital creation process started",
                "status": "processing",
                "estimated_hospitals": 55,
                "check_status_url": "/api/v1/benchmarks/collection-status"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start hospital creation: {str(e)}")


async def _execute_hospital_creation(collector: HospitalDataCollector):
    """Background task for creating hospital records"""
    target_hospitals = await collector.identify_target_hospitals()
    
    for hospital_data in target_hospitals:
        try:
            await collector._create_hospital_record(hospital_data)
        except Exception as e:
            print(f"Failed to create hospital {hospital_data['name']}: {str(e)}")


@router.post("/data-collection/start")
async def start_data_collection_campaign(
    collection_types: List[str] = Query(["hms_api", "manual_survey", "government_api"], 
                                       description="Data collection methods to use"),
    priority_tiers: List[CityTier] = Query([CityTier.TIER_1, CityTier.TIER_2],
                                          description="Priority city tiers"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db_session),
    config: ConfigManager = Depends(get_config)
):
    """Start comprehensive data collection campaign"""
    
    try:
        collector = HospitalDataCollector(db, config)
        
        # Start data collection in background
        campaign_id = f"campaign_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        background_tasks.add_task(
            _execute_data_collection_campaign,
            collector, campaign_id, collection_types, priority_tiers
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "campaign_id": campaign_id,
                "message": "Data collection campaign started",
                "status": "running",
                "collection_methods": collection_types,
                "priority_tiers": [tier.value for tier in priority_tiers],
                "status_check_url": f"/api/v1/benchmarks/collection-status/{campaign_id}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start data collection: {str(e)}")


async def _execute_data_collection_campaign(
    collector: HospitalDataCollector,
    campaign_id: str,
    collection_types: List[str],
    priority_tiers: List[CityTier]
):
    """Background task for executing data collection campaign"""
    
    try:
        results = await collector.execute_full_data_collection()
        
        # Store campaign results (would implement actual storage)
        print(f"Campaign {campaign_id} completed: {results['completion_rate']:.1f}% success rate")
        
    except Exception as e:
        print(f"Campaign {campaign_id} failed: {str(e)}")


@router.get("/collection-status/{campaign_id}")
async def get_collection_status(
    campaign_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> DataCollectionStatus:
    """Get status of ongoing data collection campaign"""
    
    # Mock implementation - would query actual campaign status
    return DataCollectionStatus(
        campaign_id=campaign_id,
        status="running",
        progress_percentage=65.5,
        hospitals_processed=36,
        hospitals_total=55,
        estimated_completion=datetime.utcnow() + timedelta(hours=2),
        errors=["API timeout for Hospital ABC", "Survey incomplete for Hospital XYZ"]
    )


@router.get("/collection-summary")
async def get_collection_summary(
    db: AsyncSession = Depends(get_db_session)
) -> BenchmarkSummary:
    """Get overall benchmark data collection summary"""
    
    # Mock implementation
    return BenchmarkSummary(
        total_hospitals=52,
        data_coverage_percentage=78.5,
        last_updated=datetime.utcnow(),
        tier_distribution={
            "tier_1": 15,
            "tier_2": 20, 
            "tier_3": 12,
            "tier_4": 5
        },
        specialty_coverage={
            "multispecialty": 45,
            "cardiology": 18,
            "oncology": 12,
            "orthopedics": 15
        },
        data_quality_score=8.2
    )


# Benchmark Analysis Endpoints

@router.get("/tier-wise-benchmarks")
async def get_tier_wise_benchmarks(
    city_tier: Optional[CityTier] = Query(None, description="Filter by specific city tier"),
    hospital_type: Optional[HospitalType] = Query(None, description="Filter by hospital type"),
    metric_category: Optional[str] = Query(None, regex="^(operational|financial|quality|efficiency)$"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get tier-wise performance benchmarks"""
    
    try:
        analyzer = BenchmarkAnalyzer(db)
        
        if city_tier:
            # Get specific tier benchmarks
            tier_benchmarks = await analyzer._analyze_tier_performance(city_tier)
            return {city_tier.value: tier_benchmarks}
        else:
            # Get all tier benchmarks
            all_benchmarks = await analyzer.create_tier_wise_benchmarks()
            return all_benchmarks
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve benchmarks: {str(e)}")


@router.get("/specialty-benchmarks")
async def get_specialty_benchmarks(
    specialty: Optional[SpecialtyType] = Query(None, description="Filter by medical specialty"),
    city_tier: Optional[CityTier] = Query(None, description="Filter by city tier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get specialty-wise performance benchmarks"""
    
    try:
        analyzer = BenchmarkAnalyzer(db)
        
        if specialty:
            specialty_data = await analyzer._analyze_specialty_performance(specialty)
            return {specialty.value: specialty_data}
        else:
            all_specialty_benchmarks = await analyzer.create_specialty_benchmarks()
            return all_specialty_benchmarks
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve specialty benchmarks: {str(e)}")


@router.get("/government-scheme-analysis")
async def get_government_scheme_analysis(
    scheme_type: Optional[str] = Query(None, description="Filter by scheme type"),
    city_tier: Optional[CityTier] = Query(None, description="Filter by city tier"),
    time_period: Optional[str] = Query("6m", regex="^(1m|3m|6m|12m)$", description="Analysis period"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get government scheme reimbursement pattern analysis"""
    
    try:
        analyzer = BenchmarkAnalyzer(db)
        scheme_patterns = await analyzer.analyze_government_scheme_patterns()
        
        # Filter by scheme type if specified
        if scheme_type and scheme_type in scheme_patterns:
            return {scheme_type: scheme_patterns[scheme_type]}
        
        return scheme_patterns
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze government schemes: {str(e)}")


@router.get("/hospitals/{hospital_id}/benchmark-comparison")
async def get_hospital_benchmark_comparison(
    hospital_id: str,
    metric_categories: List[str] = Query(["operational", "financial", "quality"], 
                                        description="Metric categories to compare"),
    db: AsyncSession = Depends(get_db_session)
) -> HospitalBenchmarkComparison:
    """Get specific hospital performance vs benchmark comparison"""
    
    try:
        # Mock implementation - would perform actual benchmark comparison
        comparison = HospitalBenchmarkComparison(
            hospital_id=hospital_id,
            hospital_name="Apollo Hospital Mumbai",
            city_tier="tier_1",
            hospital_type="private_corporate",
            performance_scores={
                "bed_occupancy_rate": 78.5,
                "patient_satisfaction": 8.1,
                "or_utilization_rate": 82.3,
                "revenue_per_bed": 24.5,
                "accounts_receivable_days": 42.0
            },
            benchmark_percentiles={
                "bed_occupancy_rate": 65,
                "patient_satisfaction": 72,
                "or_utilization_rate": 78,
                "revenue_per_bed": 85,
                "accounts_receivable_days": 25
            },
            improvement_opportunities=[
                {
                    "metric": "accounts_receivable_days",
                    "current_value": 42.0,
                    "benchmark_target": 28.0,
                    "improvement_potential": 33.3,
                    "priority": "high",
                    "estimated_financial_impact": "₹15.2 lakhs/month"
                },
                {
                    "metric": "bed_occupancy_rate", 
                    "current_value": 78.5,
                    "benchmark_target": 85.0,
                    "improvement_potential": 8.3,
                    "priority": "medium",
                    "estimated_financial_impact": "₹8.5 lakhs/month"
                }
            ],
            peer_ranking=8,
            total_peers=15
        )
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate comparison: {str(e)}")


# Data Export Endpoints

@router.get("/export/benchmarks")
async def export_benchmark_data(
    format: str = Query("excel", regex="^(excel|csv|json)$"),
    city_tier: Optional[CityTier] = Query(None),
    hospital_type: Optional[HospitalType] = Query(None),
    include_raw_data: bool = Query(False, description="Include raw hospital data"),
    db: AsyncSession = Depends(get_db_session)
):
    """Export benchmark data in various formats"""
    
    try:
        analyzer = BenchmarkAnalyzer(db)
        
        # Get benchmark data
        tier_benchmarks = await analyzer.create_tier_wise_benchmarks()
        specialty_benchmarks = await analyzer.create_specialty_benchmarks()
        
        export_data = {
            "tier_benchmarks": tier_benchmarks,
            "specialty_benchmarks": specialty_benchmarks,
            "export_timestamp": datetime.utcnow().isoformat(),
            "data_coverage": {
                "total_hospitals": 52,
                "data_points": 15000,
                "quality_score": 8.2
            }
        }
        
        if format == "json":
            return JSONResponse(content=export_data)
        
        elif format == "excel":
            # Create Excel file
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Tier benchmarks sheet
                tier_df = pd.json_normalize(tier_benchmarks)
                tier_df.to_excel(writer, sheet_name='Tier_Benchmarks', index=False)
                
                # Specialty benchmarks sheet
                specialty_df = pd.json_normalize(specialty_benchmarks)
                specialty_df.to_excel(writer, sheet_name='Specialty_Benchmarks', index=False)
            
            output.seek(0)
            
            return FileResponse(
                path="benchmark_data.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=f"hospital_benchmarks_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
            )
        
        elif format == "csv":
            # Return CSV of tier benchmarks
            tier_df = pd.json_normalize(tier_benchmarks)
            csv_output = tier_df.to_csv(index=False)
            
            return JSONResponse(
                content=csv_output,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=tier_benchmarks.csv"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


# Data Quality & Validation Endpoints

@router.get("/data-quality/report")
async def get_data_quality_report(
    db: AsyncSession = Depends(get_db_session)
):
    """Get comprehensive data quality report"""
    
    quality_report = {
        "overall_quality_score": 8.2,
        "data_completeness": {
            "performance_metrics": 85.5,
            "financial_metrics": 72.3,
            "government_scheme_data": 68.8,
            "hospital_basic_info": 95.2
        },
        "data_freshness": {
            "last_30_days": 45,
            "last_90_days": 38,
            "older_than_90_days": 17
        },
        "source_reliability": {
            "hms_api": {"count": 18, "quality_score": 9.1},
            "manual_survey": {"count": 22, "quality_score": 7.5},
            "government_api": {"count": 8, "quality_score": 8.8},
            "partner_network": {"count": 12, "quality_score": 8.0}
        },
        "data_validation_issues": [
            {"hospital_id": "hosp_001", "issue": "Bed occupancy > 100%", "severity": "high"},
            {"hospital_id": "hosp_015", "issue": "Missing financial data", "severity": "medium"},
            {"hospital_id": "hosp_028", "issue": "Outdated contact info", "severity": "low"}
        ],
        "recommendations": [
            "Implement automated data validation for bed occupancy rates",
            "Follow up with 8 hospitals missing recent financial data",
            "Set up automated HMS API connections for 12 manually-surveyed hospitals"
        ]
    }
    
    return quality_report


@router.post("/data-collection/validate")
async def validate_collected_data(
    hospital_id: str,
    data_type: str = Query(..., regex="^(performance|financial|government_scheme)$"),
    db: AsyncSession = Depends(get_db_session)
):
    """Validate specific hospital data collection"""
    
    validation_result = {
        "hospital_id": hospital_id,
        "data_type": data_type,
        "validation_timestamp": datetime.utcnow(),
        "is_valid": True,
        "quality_score": 8.5,
        "issues_found": [],
        "recommendations": []
    }
    
    # Mock validation logic
    if data_type == "performance":
        validation_result["issues_found"] = [
            "Average length of stay seems high (6.8 days vs benchmark 4.2 days)",
            "Patient satisfaction score missing for last 2 months"
        ]
        validation_result["quality_score"] = 7.8
    
    return validation_result


# Hospital Management Endpoints

@router.post("/hospitals")
async def create_hospital(
    hospital_data: HospitalCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create new hospital in benchmark database"""
    
    try:
        # Create hospital record
        hospital = Hospital(**hospital_data.dict())
        
        # Mock database insertion
        hospital.id = f"hosp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "hospital_id": hospital.id,
            "message": "Hospital created successfully",
            "status": "active"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create hospital: {str(e)}")


@router.get("/hospitals")
async def list_hospitals(
    city_tier: Optional[CityTier] = Query(None),
    hospital_type: Optional[HospitalType] = Query(None),
    has_data: Optional[bool] = Query(None, description="Filter by data availability"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
):
    """List hospitals with filtering and pagination"""
    
    # Mock hospital listing
    hospitals = [
        {
            "id": "hosp_001",
            "name": "Apollo Hospital Mumbai",
            "city": "Mumbai",
            "state": "Maharashtra",
            "city_tier": "tier_1",
            "hospital_type": "private_corporate",
            "bed_count": 500,
            "data_availability": True,
            "last_data_update": "2024-09-20T10:30:00Z",
            "data_quality_score": 9.1
        },
        {
            "id": "hosp_002", 
            "name": "Fortis Hospital Delhi",
            "city": "Delhi",
            "state": "Delhi",
            "city_tier": "tier_1",
            "hospital_type": "private_corporate",
            "bed_count": 400,
            "data_availability": True,
            "last_data_update": "2024-09-22T14:15:00Z",
            "data_quality_score": 8.7
        }
    ]
    
    return {
        "hospitals": hospitals,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": 52,
            "total_pages": 3
        },
        "filters_applied": {
            "city_tier": city_tier.value if city_tier else None,
            "hospital_type": hospital_type.value if hospital_type else None,
            "has_data": has_data
        }
    }


@router.get("/hospitals/{hospital_id}")
async def get_hospital_details(
    hospital_id: str,
    include_performance_data: bool = Query(True),
    include_financial_data: bool = Query(True),
    db: AsyncSession = Depends(get_db_session)
):
    """Get detailed hospital information and performance data"""
    
    hospital_details = {
        "id": hospital_id,
        "name": "Apollo Hospital Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "city_tier": "tier_1",
        "hospital_type": "private_corporate",
        "bed_count": 500,
        "established_year": 1995,
        "accreditation_nabh": True,
        "accreditation_jci": True,
        "specialties": ["multispecialty", "cardiology", "oncology", "neurology"],
        "contact_info": {
            "address": "21, Greams Lane, Off Greams Road, Chennai - 600006",
            "phone": "+91-44-2829-3333",
            "email": "info@apollohospitals.com",
            "website": "https://www.apollohospitals.com"
        }
    }
    
    if include_performance_data:
        hospital_details["performance_metrics"] = {
            "bed_occupancy_rate": 78.5,
            "average_length_of_stay": 4.2,
            "patient_satisfaction_score": 8.1,
            "or_utilization_rate": 82.3,
            "readmission_rate": 6.8,
            "last_updated": "2024-09-20T10:30:00Z"
        }
    
    if include_financial_data:
        hospital_details["financial_metrics"] = {
            "total_revenue": 245.8,  # INR Lakhs
            "revenue_per_bed": 24.5,
            "ebitda_margin": 18.5,
            "accounts_receivable_days": 42,
            "cash_percentage": 35.2,
            "government_scheme_percentage": 28.5,
            "last_updated": "2024-09-15T09:00:00Z"
        }
    
    return hospital_details