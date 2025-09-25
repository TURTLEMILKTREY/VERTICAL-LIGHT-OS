"""
Real Data Integration Orchestrator
Coordinates all real data collection services for comprehensive hospital benchmark data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import pandas as pd
from pathlib import Path
import uuid

from .hms_api_integrator import HMSAPIIntegrator, HMSType
from .government_api_integrator import GovernmentDataIntegrator, GovernmentScheme
from .survey_data_collector import RealSurveyDataCollector, SurveyChannel
from .partner_network_integrator import PartnerNetworkDataIntegrator, PartnerType
from .third_party_analytics_integrator import ThirdPartyAnalyticsIntegrator, AnalyticsPlatform
from .data_quality_validator import DataQualityValidator, DataSource, ValidationSeverity

from ...models.hospital_benchmarks import (
    Hospital, CityTier, HospitalType, SpecialtyType
)
from ...config.advanced_config_manager import ConfigManager
from ...services.shared.error_handling import ApplicationError


class IntegrationPhase(Enum):
    """Data integration phases"""
    INITIALIZATION = "initialization"
    HMS_COLLECTION = "hms_collection"
    GOVERNMENT_COLLECTION = "government_collection" 
    SURVEY_COLLECTION = "survey_collection"
    PARTNER_COLLECTION = "partner_collection"
    VALIDATION = "validation"
    ENRICHMENT = "enrichment"
    CONSOLIDATION = "consolidation"
    COMPLETE = "complete"
    FAILED = "failed"


class IntegrationPriority(Enum):
    """Integration priority levels"""
    CRITICAL = "critical"     # Must complete for benchmarking
    HIGH = "high"            # Important for comprehensive analysis
    MEDIUM = "medium"        # Useful supplementary data
    LOW = "low"             # Nice to have


@dataclass
class IntegrationTask:
    """Individual data integration task"""
    task_id: str
    hospital_id: str
    data_source: DataSource
    integration_method: str
    priority: IntegrationPriority
    scheduled_time: datetime
    phase: IntegrationPhase = IntegrationPhase.INITIALIZATION
    status: str = "pending"  # pending, running, completed, failed
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    collected_data: Optional[Dict[str, Any]] = None
    quality_score: Optional[int] = None
    completion_time: Optional[datetime] = None


@dataclass
class IntegrationPlan:
    """Comprehensive integration plan for hospital data collection"""
    plan_id: str
    hospital_id: str
    hospital_name: str
    city_tier: str
    hospital_type: str
    target_data_types: List[str]
    integration_tasks: List[IntegrationTask] = field(default_factory=list)
    current_phase: IntegrationPhase = IntegrationPhase.INITIALIZATION
    overall_status: str = "pending"
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    quality_report: Optional[Dict[str, Any]] = None
    consolidated_data: Optional[Dict[str, Any]] = None


class RealDataIntegrationError(ApplicationError):
    """Real data integration orchestration errors"""
    pass


class RealDataIntegrationOrchestrator:
    """Production Real Data Integration Orchestration Service"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize integration services
        self.hms_integrator = HMSAPIIntegrator(config)
        self.government_integrator = GovernmentDataIntegrator(config)
        self.survey_collector = RealSurveyDataCollector(config)
        self.partner_integrator = PartnerNetworkDataIntegrator(config)
        self.analytics_integrator = ThirdPartyAnalyticsIntegrator(config)
        self.quality_validator = DataQualityValidator(config)
        
        # Active integration plans
        self.active_plans: Dict[str, IntegrationPlan] = {}
        
        # Integration analytics
        self.integration_analytics = {
            "total_hospitals_processed": 0,
            "successful_integrations": 0,
            "failed_integrations": 0,
            "average_quality_score": 0,
            "data_source_performance": {},
            "integration_timeline": []
        }
        
        # Default data collection configuration
        self.default_data_types = [
            "performance_metrics",
            "financial_data", 
            "quality_metrics",
            "government_schemes",
            "operational_data",
            "patient_demographics"
        ]
    
    async def create_hospital_integration_plan(self, hospital_info: Dict[str, Any]) -> IntegrationPlan:
        """Create comprehensive integration plan for a hospital"""
        
        try:
            hospital_id = hospital_info.get("hospital_id") or str(uuid.uuid4())
            hospital_name = hospital_info.get("hospital_name", "Unknown Hospital")
            city_tier = hospital_info.get("city_tier", "unknown")
            hospital_type = hospital_info.get("hospital_type", "unknown")
            
            # Create integration plan
            plan = IntegrationPlan(
                plan_id=f"integration_{hospital_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                hospital_id=hospital_id,
                hospital_name=hospital_name,
                city_tier=city_tier,
                hospital_type=hospital_type,
                target_data_types=hospital_info.get("data_types", self.default_data_types),
                start_time=datetime.utcnow()
            )
            
            # Determine available integration methods
            available_methods = await self._assess_integration_methods(hospital_info)
            
            # Create integration tasks based on availability and priority
            tasks = []
            
            # HMS Integration (High Priority)
            if available_methods.get("hms_api"):
                task = IntegrationTask(
                    task_id=f"hms_{hospital_id}_{uuid.uuid4().hex[:8]}",
                    hospital_id=hospital_id,
                    data_source=DataSource.HMS_API,
                    integration_method="hms_api",
                    priority=IntegrationPriority.HIGH,
                    scheduled_time=datetime.utcnow() + timedelta(minutes=1),
                    phase=IntegrationPhase.HMS_COLLECTION
                )
                tasks.append(task)
            
            # Government API Integration (Critical Priority)
            if available_methods.get("government_api"):
                task = IntegrationTask(
                    task_id=f"govt_{hospital_id}_{uuid.uuid4().hex[:8]}",
                    hospital_id=hospital_id,
                    data_source=DataSource.GOVERNMENT_API,
                    integration_method="government_api",
                    priority=IntegrationPriority.CRITICAL,
                    scheduled_time=datetime.utcnow() + timedelta(minutes=2),
                    phase=IntegrationPhase.GOVERNMENT_COLLECTION
                )
                tasks.append(task)
            
            # Partner Network Integration (Medium Priority)
            if available_methods.get("partner_network"):
                task = IntegrationTask(
                    task_id=f"partner_{hospital_id}_{uuid.uuid4().hex[:8]}",
                    hospital_id=hospital_id,
                    data_source=DataSource.PARTNER_NETWORK,
                    integration_method="partner_network",
                    priority=IntegrationPriority.MEDIUM,
                    scheduled_time=datetime.utcnow() + timedelta(minutes=3),
                    phase=IntegrationPhase.PARTNER_COLLECTION
                )
                tasks.append(task)
            
            # Third-Party Analytics Integration (Medium Priority)
            if available_methods.get("analytics_platforms"):
                task = IntegrationTask(
                    task_id=f"analytics_{hospital_id}_{uuid.uuid4().hex[:8]}",
                    hospital_id=hospital_id,
                    data_source=DataSource.EXTERNAL_IMPORT,
                    integration_method="analytics_platforms",
                    priority=IntegrationPriority.MEDIUM,
                    scheduled_time=datetime.utcnow() + timedelta(minutes=4),
                    phase=IntegrationPhase.PARTNER_COLLECTION
                )
                tasks.append(task)
            
            # Survey Collection (Always available, Low Priority)
            task = IntegrationTask(
                task_id=f"survey_{hospital_id}_{uuid.uuid4().hex[:8]}",
                hospital_id=hospital_id,
                data_source=DataSource.SURVEY_MANUAL,
                integration_method="survey_collection",
                priority=IntegrationPriority.LOW,
                scheduled_time=datetime.utcnow() + timedelta(minutes=5),
                phase=IntegrationPhase.SURVEY_COLLECTION
            )
            tasks.append(task)
            
            plan.integration_tasks = tasks
            self.active_plans[plan.plan_id] = plan
            
            self.logger.info(f"Created integration plan {plan.plan_id} for {hospital_name} with {len(tasks)} tasks")
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create integration plan: {str(e)}")
            raise RealDataIntegrationError(f"Integration plan creation failed: {str(e)}")
    
    async def execute_integration_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute comprehensive data integration plan"""
        
        plan = self.active_plans.get(plan_id)
        if not plan:
            raise RealDataIntegrationError(f"Integration plan {plan_id} not found")
        
        execution_results = {
            "plan_id": plan_id,
            "hospital_id": plan.hospital_id,
            "hospital_name": plan.hospital_name,
            "execution_start": datetime.utcnow().isoformat(),
            "phases_completed": [],
            "tasks_completed": 0,
            "tasks_failed": 0,
            "collected_data": {},
            "quality_scores": {},
            "overall_quality": 0,
            "success": False
        }
        
        try:
            plan.overall_status = "running"
            
            # Execute tasks by priority order
            priority_order = [
                IntegrationPriority.CRITICAL,
                IntegrationPriority.HIGH, 
                IntegrationPriority.MEDIUM,
                IntegrationPriority.LOW
            ]
            
            for priority in priority_order:
                priority_tasks = [t for t in plan.integration_tasks if t.priority == priority]
                
                if priority_tasks:
                    self.logger.info(f"Executing {len(priority_tasks)} {priority.value} priority tasks")
                    
                    # Execute priority tasks in parallel
                    task_results = await asyncio.gather(
                        *[self._execute_integration_task(task) for task in priority_tasks],
                        return_exceptions=True
                    )
                    
                    # Process results
                    for task, result in zip(priority_tasks, task_results):
                        if isinstance(result, Exception):
                            self.logger.error(f"Task {task.task_id} failed: {str(result)}")
                            task.status = "failed"
                            task.error_message = str(result)
                            execution_results["tasks_failed"] += 1
                        else:
                            task.status = "completed"
                            task.collected_data = result.get("data", {})
                            task.quality_score = result.get("quality_score", 0)
                            task.completion_time = datetime.utcnow()
                            
                            execution_results["tasks_completed"] += 1
                            execution_results["collected_data"][task.data_source.value] = task.collected_data
                            execution_results["quality_scores"][task.data_source.value] = task.quality_score
            
            # Data Validation Phase
            plan.current_phase = IntegrationPhase.VALIDATION
            execution_results["phases_completed"].append("validation")
            
            validation_results = await self._validate_collected_data(plan, execution_results["collected_data"])
            execution_results["validation_results"] = validation_results
            
            # Data Enrichment Phase  
            plan.current_phase = IntegrationPhase.ENRICHMENT
            execution_results["phases_completed"].append("enrichment")
            
            enriched_data = await self._enrich_collected_data(plan, execution_results["collected_data"])
            execution_results["enriched_data"] = enriched_data
            
            # Data Consolidation Phase
            plan.current_phase = IntegrationPhase.CONSOLIDATION
            execution_results["phases_completed"].append("consolidation")
            
            consolidated_data = await self._consolidate_hospital_data(plan, enriched_data)
            execution_results["consolidated_data"] = consolidated_data
            plan.consolidated_data = consolidated_data
            
            # Calculate overall quality score
            if execution_results["quality_scores"]:
                scores = list(execution_results["quality_scores"].values())
                execution_results["overall_quality"] = int(sum(scores) / len(scores))
            
            # Mark as complete
            plan.current_phase = IntegrationPhase.COMPLETE
            plan.overall_status = "completed"
            plan.completion_time = datetime.utcnow()
            
            execution_results["success"] = execution_results["tasks_completed"] > 0
            execution_results["execution_end"] = datetime.utcnow().isoformat()
            
            # Update analytics
            self._update_integration_analytics(plan, execution_results)
            
            self.logger.info(f"Integration plan {plan_id} completed successfully")
            
            return execution_results
            
        except Exception as e:
            plan.current_phase = IntegrationPhase.FAILED
            plan.overall_status = "failed"
            
            execution_results["success"] = False
            execution_results["error"] = str(e)
            execution_results["execution_end"] = datetime.utcnow().isoformat()
            
            self.logger.error(f"Integration plan {plan_id} failed: {str(e)}")
            
            return execution_results
    
    async def _assess_integration_methods(self, hospital_info: Dict[str, Any]) -> Dict[str, bool]:
        """Assess available integration methods for a hospital"""
        
        available_methods = {
            "hms_api": False,
            "government_api": True,  # Always available through public APIs
            "partner_network": False,
            "analytics_platforms": False,
            "survey_collection": True  # Always available as fallback
        }
        
        try:
            # Check HMS API availability
            hospital_name = hospital_info.get("hospital_name", "")
            city = hospital_info.get("city", "")
            
            # Test HMS connections
            hms_availability = await self.hms_integrator.test_hospital_connectivity({
                "hospital_name": hospital_name,
                "city": city,
                "contact_email": hospital_info.get("contact_email", "")
            })
            
            available_methods["hms_api"] = hms_availability.get("can_connect", False)
            
            # Check partner network coverage
            partner_coverage = self.partner_integrator.get_partner_analytics()
            covered_hospitals = partner_coverage.get("total_hospitals_covered", 0)
            
            available_methods["partner_network"] = covered_hospitals > 0
            
            # Check analytics platform availability
            analytics_status = self.analytics_integrator.get_analytics_integration_status()
            active_platforms = analytics_status.get("active_platforms", 0)
            
            available_methods["analytics_platforms"] = active_platforms > 0
            
        except Exception as e:
            self.logger.warning(f"Failed to assess integration methods: {str(e)}")
        
        return available_methods
    
    async def _execute_integration_task(self, task: IntegrationTask) -> Dict[str, Any]:
        """Execute individual integration task"""
        
        task.status = "running"
        
        try:
            if task.data_source == DataSource.HMS_API:
                result = await self._execute_hms_integration(task)
            
            elif task.data_source == DataSource.GOVERNMENT_API:
                result = await self._execute_government_integration(task)
            
            elif task.data_source == DataSource.PARTNER_NETWORK:
                result = await self._execute_partner_integration(task)
            
            elif task.data_source == DataSource.SURVEY_MANUAL:
                result = await self._execute_survey_integration(task)
            
            elif task.data_source == DataSource.EXTERNAL_IMPORT and task.integration_method == "analytics_platforms":
                result = await self._execute_analytics_integration(task)
            
            else:
                raise RealDataIntegrationError(f"Unknown data source: {task.data_source}")
            
            # Validate collected data
            if result.get("data"):
                quality_report = await self.quality_validator.validate_hospital_data(
                    result["data"], task.data_source, task.hospital_id
                )
                result["quality_score"] = quality_report.overall_score
                result["quality_report"] = quality_report
            
            return result
            
        except Exception as e:
            task.retry_count += 1
            
            if task.retry_count <= task.max_retries:
                self.logger.warning(f"Task {task.task_id} failed, retrying ({task.retry_count}/{task.max_retries}): {str(e)}")
                # Schedule retry
                await asyncio.sleep(5)
                return await self._execute_integration_task(task)
            else:
                self.logger.error(f"Task {task.task_id} failed permanently: {str(e)}")
                raise RealDataIntegrationError(f"Task execution failed: {str(e)}")
    
    async def _execute_hms_integration(self, task: IntegrationTask) -> Dict[str, Any]:
        """Execute HMS API integration task"""
        
        try:
            # Get hospital connection details from task
            hospital_data = await self.hms_integrator.collect_hospital_data(
                hospital_id=task.hospital_id,
                hms_types=[HMSType.MEDTECH, HMSType.BIRLAMEDISOFT, HMSType.HMIS_PLUS]
            )
            
            return {
                "success": hospital_data["success"],
                "data": hospital_data.get("collected_data", {}),
                "source": "hms_api",
                "collection_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise RealDataIntegrationError(f"HMS integration failed: {str(e)}")
    
    async def _execute_government_integration(self, task: IntegrationTask) -> Dict[str, Any]:
        """Execute Government API integration task"""
        
        try:
            # Collect government scheme data
            govt_data = await self.government_integrator.collect_hospital_scheme_data(
                hospital_id=task.hospital_id,
                schemes=[
                    GovernmentScheme.PMJAY_AYUSHMAN_BHARAT,
                    GovernmentScheme.CGHS,
                    GovernmentScheme.ESI
                ]
            )
            
            return {
                "success": govt_data["success"],
                "data": govt_data.get("scheme_data", {}),
                "source": "government_api", 
                "collection_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise RealDataIntegrationError(f"Government integration failed: {str(e)}")
    
    async def _execute_partner_integration(self, task: IntegrationTask) -> Dict[str, Any]:
        """Execute Partner Network integration task"""
        
        try:
            # Get partner data for hospital
            partner_data = await self.partner_integrator.collect_partner_data(
                partner_id="all",  # Collect from all available partners
                hospital_ids=[task.hospital_id]
            )
            
            return {
                "success": partner_data["success"],
                "data": partner_data.get("processed_data", {}),
                "source": "partner_network",
                "collection_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise RealDataIntegrationError(f"Partner integration failed: {str(e)}")
    
    async def _execute_survey_integration(self, task: IntegrationTask) -> Dict[str, Any]:
        """Execute Survey collection integration task"""
        
        try:
            # Create and distribute survey for hospital
            survey_result = await self.survey_collector.create_comprehensive_survey(
                hospital_id=task.hospital_id,
                survey_name=f"Data Collection Survey - {task.hospital_id}",
                distribution_channels=[
                    SurveyChannel.EMAIL,
                    SurveyChannel.WHATSAPP
                ]
            )
            
            return {
                "success": survey_result["success"],
                "data": survey_result.get("survey_data", {}),
                "source": "survey_manual",
                "collection_timestamp": datetime.utcnow().isoformat(),
                "survey_id": survey_result.get("survey_id")
            }
            
        except Exception as e:
            raise RealDataIntegrationError(f"Survey integration failed: {str(e)}")
    
    async def _execute_analytics_integration(self, task: IntegrationTask) -> Dict[str, Any]:
        """Execute Third-Party Analytics integration task"""
        
        try:
            # Collect analytics data from all available platforms for this hospital
            analytics_result = await self.analytics_integrator.batch_analytics_collection(
                hospital_ids=[task.hospital_id],
                platform_ids=None  # Use all available platforms
            )
            
            return {
                "success": analytics_result["success"],
                "data": analytics_result.get("consolidated_data", {}),
                "source": "analytics_platforms",
                "collection_timestamp": datetime.utcnow().isoformat(),
                "platforms_used": analytics_result.get("batch_analytics", {}).get("platforms_successful", 0),
                "total_data_points": analytics_result.get("batch_analytics", {}).get("total_data_points_collected", 0)
            }
            
        except Exception as e:
            raise RealDataIntegrationError(f"Analytics integration failed: {str(e)}")
    
    async def _validate_collected_data(self, plan: IntegrationPlan, 
                                     collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all collected data"""
        
        validation_results = {}
        
        for data_source, data in collected_data.items():
            try:
                # Convert source string back to enum
                source_enum = DataSource(data_source)
                
                quality_report = await self.quality_validator.validate_hospital_data(
                    data, source_enum, plan.hospital_id
                )
                
                validation_results[data_source] = {
                    "quality_score": quality_report.overall_score,
                    "total_validations": quality_report.total_validations,
                    "passed_validations": quality_report.passed_validations,
                    "failed_validations": quality_report.failed_validations,
                    "critical_issues": quality_report.critical_issues,
                    "validation_summary": {
                        result.rule_id: {
                            "passed": result.passed,
                            "message": result.message,
                            "severity": result.severity.value
                        }
                        for result in quality_report.validation_results[:10]  # Top 10 issues
                    }
                }
                
            except Exception as e:
                self.logger.error(f"Validation failed for {data_source}: {str(e)}")
                validation_results[data_source] = {
                    "quality_score": 0,
                    "error": str(e)
                }
        
        return validation_results
    
    async def _enrich_collected_data(self, plan: IntegrationPlan, 
                                   collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich collected data with additional information"""
        
        enriched_data = {}
        
        for data_source, data in collected_data.items():
            try:
                enriched = await self.quality_validator.enrich_hospital_data(
                    data, plan.hospital_id
                )
                enriched_data[data_source] = enriched
                
            except Exception as e:
                self.logger.error(f"Enrichment failed for {data_source}: {str(e)}")
                enriched_data[data_source] = data  # Use original data if enrichment fails
        
        return enriched_data
    
    async def _consolidate_hospital_data(self, plan: IntegrationPlan, 
                                       enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate data from all sources into unified hospital profile"""
        
        consolidated = {
            "hospital_id": plan.hospital_id,
            "hospital_name": plan.hospital_name,
            "city_tier": plan.city_tier,
            "hospital_type": plan.hospital_type,
            "data_collection_timestamp": datetime.utcnow().isoformat(),
            "data_sources_used": list(enriched_data.keys()),
            "performance_metrics": {},
            "financial_data": {},
            "quality_metrics": {},
            "government_schemes": {},
            "operational_data": {},
            "patient_demographics": {}
        }
        
        try:
            # Consolidate performance metrics
            performance_data = {}
            for source_data in enriched_data.values():
                if "bed_occupancy_rate" in source_data:
                    performance_data["bed_occupancy_rate"] = source_data["bed_occupancy_rate"]
                if "average_length_of_stay" in source_data:
                    performance_data["average_length_of_stay"] = source_data["average_length_of_stay"]
                if "or_utilization_rate" in source_data:
                    performance_data["or_utilization_rate"] = source_data["or_utilization_rate"]
            
            consolidated["performance_metrics"] = performance_data
            
            # Consolidate financial data
            financial_data = {}
            for source_data in enriched_data.values():
                if "total_revenue" in source_data:
                    financial_data["total_revenue"] = source_data["total_revenue"]
                if "total_costs" in source_data:
                    financial_data["total_costs"] = source_data["total_costs"]
                if "profit_margin" in source_data:
                    financial_data["profit_margin"] = source_data["profit_margin"]
            
            consolidated["financial_data"] = financial_data
            
            # Consolidate quality metrics
            quality_data = {}
            for source_data in enriched_data.values():
                if "patient_satisfaction_score" in source_data:
                    quality_data["patient_satisfaction_score"] = source_data["patient_satisfaction_score"]
                if "readmission_rate" in source_data:
                    quality_data["readmission_rate"] = source_data["readmission_rate"]
                if "infection_rate" in source_data:
                    quality_data["infection_rate"] = source_data["infection_rate"]
            
            consolidated["quality_metrics"] = quality_data
            
            # Consolidate government scheme data
            scheme_data = {}
            for source_data in enriched_data.values():
                if "government_scheme_revenue" in source_data:
                    scheme_data["government_scheme_revenue"] = source_data["government_scheme_revenue"]
                if "pmjay_cases" in source_data:
                    scheme_data["pmjay_cases"] = source_data["pmjay_cases"]
                if "cghs_revenue" in source_data:
                    scheme_data["cghs_revenue"] = source_data["cghs_revenue"]
            
            consolidated["government_schemes"] = scheme_data
            
            # Add data quality indicators
            consolidated["data_quality"] = {
                "overall_completeness": self._calculate_completeness(consolidated),
                "source_count": len(enriched_data),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
            
            # Add benchmark readiness score
            consolidated["benchmark_readiness"] = self._calculate_benchmark_readiness(consolidated)
            
        except Exception as e:
            self.logger.error(f"Data consolidation failed: {str(e)}")
            consolidated["consolidation_error"] = str(e)
        
        return consolidated
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> int:
        """Calculate data completeness percentage"""
        
        essential_fields = [
            "performance_metrics.bed_occupancy_rate",
            "performance_metrics.average_length_of_stay",
            "financial_data.total_revenue",
            "quality_metrics.patient_satisfaction_score"
        ]
        
        completed_fields = 0
        
        for field_path in essential_fields:
            try:
                parts = field_path.split('.')
                current = data
                
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        current = None
                        break
                
                if current is not None and current != "":
                    completed_fields += 1
                    
            except (KeyError, TypeError):
                pass
        
        return int((completed_fields / len(essential_fields)) * 100)
    
    def _calculate_benchmark_readiness(self, data: Dict[str, Any]) -> int:
        """Calculate how ready the data is for benchmarking analysis"""
        
        readiness_score = 0
        
        # Performance metrics readiness (40 points)
        performance = data.get("performance_metrics", {})
        if performance.get("bed_occupancy_rate"):
            readiness_score += 15
        if performance.get("average_length_of_stay"):
            readiness_score += 15
        if performance.get("or_utilization_rate"):
            readiness_score += 10
        
        # Financial data readiness (30 points)
        financial = data.get("financial_data", {})
        if financial.get("total_revenue"):
            readiness_score += 15
        if financial.get("total_costs"):
            readiness_score += 15
        
        # Quality metrics readiness (20 points)
        quality = data.get("quality_metrics", {})
        if quality.get("patient_satisfaction_score"):
            readiness_score += 10
        if quality.get("readmission_rate"):
            readiness_score += 10
        
        # Government scheme data readiness (10 points)
        schemes = data.get("government_schemes", {})
        if schemes.get("government_scheme_revenue"):
            readiness_score += 10
        
        return min(100, readiness_score)
    
    def _update_integration_analytics(self, plan: IntegrationPlan, 
                                    results: Dict[str, Any]) -> None:
        """Update integration analytics with execution results"""
        
        try:
            self.integration_analytics["total_hospitals_processed"] += 1
            
            if results["success"]:
                self.integration_analytics["successful_integrations"] += 1
            else:
                self.integration_analytics["failed_integrations"] += 1
            
            # Update average quality score
            if results.get("overall_quality"):
                current_avg = self.integration_analytics["average_quality_score"]
                total_processed = self.integration_analytics["total_hospitals_processed"]
                
                new_avg = ((current_avg * (total_processed - 1)) + results["overall_quality"]) / total_processed
                self.integration_analytics["average_quality_score"] = round(new_avg, 1)
            
            # Update data source performance
            for source, score in results.get("quality_scores", {}).items():
                if source not in self.integration_analytics["data_source_performance"]:
                    self.integration_analytics["data_source_performance"][source] = {
                        "total_collections": 0,
                        "successful_collections": 0,
                        "average_quality": 0
                    }
                
                source_stats = self.integration_analytics["data_source_performance"][source]
                source_stats["total_collections"] += 1
                
                if score > 0:
                    source_stats["successful_collections"] += 1
                    current_avg = source_stats["average_quality"]
                    success_count = source_stats["successful_collections"]
                    
                    new_avg = ((current_avg * (success_count - 1)) + score) / success_count
                    source_stats["average_quality"] = round(new_avg, 1)
            
            # Add timeline entry
            timeline_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "hospital_id": plan.hospital_id,
                "hospital_name": plan.hospital_name,
                "success": results["success"],
                "quality_score": results.get("overall_quality", 0),
                "data_sources": list(results.get("quality_scores", {}).keys())
            }
            
            self.integration_analytics["integration_timeline"].append(timeline_entry)
            
            # Keep only last 1000 entries
            if len(self.integration_analytics["integration_timeline"]) > 1000:
                self.integration_analytics["integration_timeline"] = \
                    self.integration_analytics["integration_timeline"][-1000:]
        
        except Exception as e:
            self.logger.error(f"Failed to update integration analytics: {str(e)}")
    
    async def batch_hospital_integration(self, hospital_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute integration for multiple hospitals in batch"""
        
        batch_results = {
            "batch_id": str(uuid.uuid4()),
            "batch_start": datetime.utcnow().isoformat(),
            "total_hospitals": len(hospital_list),
            "completed_hospitals": 0,
            "failed_hospitals": 0,
            "hospital_results": {},
            "batch_analytics": {}
        }
        
        try:
            # Create integration plans for all hospitals
            plans = []
            for hospital_info in hospital_list:
                plan = await self.create_hospital_integration_plan(hospital_info)
                plans.append(plan)
            
            self.logger.info(f"Created {len(plans)} integration plans for batch processing")
            
            # Execute plans with controlled concurrency
            semaphore = asyncio.Semaphore(5)  # Limit concurrent executions
            
            async def execute_with_semaphore(plan):
                async with semaphore:
                    return await self.execute_integration_plan(plan.plan_id)
            
            # Execute all plans
            plan_results = await asyncio.gather(
                *[execute_with_semaphore(plan) for plan in plans],
                return_exceptions=True
            )
            
            # Process results
            for plan, result in zip(plans, plan_results):
                if isinstance(result, Exception):
                    batch_results["failed_hospitals"] += 1
                    batch_results["hospital_results"][plan.hospital_id] = {
                        "success": False,
                        "error": str(result)
                    }
                else:
                    if result["success"]:
                        batch_results["completed_hospitals"] += 1
                    else:
                        batch_results["failed_hospitals"] += 1
                    
                    batch_results["hospital_results"][plan.hospital_id] = result
            
            # Calculate batch analytics
            successful_results = [r for r in batch_results["hospital_results"].values() if r.get("success")]
            
            if successful_results:
                avg_quality = sum(r.get("overall_quality", 0) for r in successful_results) / len(successful_results)
                
                batch_results["batch_analytics"] = {
                    "success_rate": round((batch_results["completed_hospitals"] / batch_results["total_hospitals"]) * 100, 1),
                    "average_quality_score": round(avg_quality, 1),
                    "total_data_points": sum(len(r.get("collected_data", {})) for r in successful_results),
                    "data_source_coverage": self._analyze_batch_data_sources(successful_results)
                }
            
            batch_results["batch_end"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Batch integration completed: {batch_results['completed_hospitals']}/{batch_results['total_hospitals']} successful")
            
            return batch_results
            
        except Exception as e:
            batch_results["batch_end"] = datetime.utcnow().isoformat()
            batch_results["batch_error"] = str(e)
            
            self.logger.error(f"Batch integration failed: {str(e)}")
            
            return batch_results
    
    def _analyze_batch_data_sources(self, successful_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze data source coverage across batch"""
        
        source_coverage = {}
        
        for result in successful_results:
            for source in result.get("collected_data", {}).keys():
                source_coverage[source] = source_coverage.get(source, 0) + 1
        
        # Calculate percentages
        total_hospitals = len(successful_results)
        source_percentages = {
            source: round((count / total_hospitals) * 100, 1)
            for source, count in source_coverage.items()
        }
        
        return {
            "source_counts": source_coverage,
            "source_percentages": source_percentages,
            "most_common_source": max(source_coverage.items(), key=lambda x: x[1])[0] if source_coverage else None
        }
    
    def get_integration_status(self, plan_id: Optional[str] = None) -> Dict[str, Any]:
        """Get integration status for specific plan or overall analytics"""
        
        if plan_id:
            plan = self.active_plans.get(plan_id)
            if not plan:
                return {"error": f"Integration plan {plan_id} not found"}
            
            return {
                "plan_id": plan.plan_id,
                "hospital_id": plan.hospital_id,
                "hospital_name": plan.hospital_name,
                "current_phase": plan.current_phase.value,
                "overall_status": plan.overall_status,
                "start_time": plan.start_time.isoformat() if plan.start_time else None,
                "completion_time": plan.completion_time.isoformat() if plan.completion_time else None,
                "total_tasks": len(plan.integration_tasks),
                "completed_tasks": len([t for t in plan.integration_tasks if t.status == "completed"]),
                "failed_tasks": len([t for t in plan.integration_tasks if t.status == "failed"]),
                "task_details": [
                    {
                        "task_id": task.task_id,
                        "data_source": task.data_source.value,
                        "priority": task.priority.value,
                        "status": task.status,
                        "quality_score": task.quality_score,
                        "error": task.error_message
                    }
                    for task in plan.integration_tasks
                ]
            }
        else:
            return {
                "overall_analytics": self.integration_analytics,
                "active_plans": len(self.active_plans),
                "plan_summary": [
                    {
                        "plan_id": plan.plan_id,
                        "hospital_name": plan.hospital_name,
                        "status": plan.overall_status,
                        "current_phase": plan.current_phase.value
                    }
                    for plan in self.active_plans.values()
                ]
            }
    
    async def cleanup_completed_plans(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up completed integration plans older than specified hours"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        plans_to_remove = []
        for plan_id, plan in self.active_plans.items():
            if (plan.overall_status in ["completed", "failed"] and 
                plan.completion_time and 
                plan.completion_time < cutoff_time):
                plans_to_remove.append(plan_id)
        
        # Archive plan data before removal
        archived_plans = {}
        for plan_id in plans_to_remove:
            plan = self.active_plans[plan_id]
            archived_plans[plan_id] = {
                "hospital_id": plan.hospital_id,
                "hospital_name": plan.hospital_name,
                "status": plan.overall_status,
                "completion_time": plan.completion_time.isoformat(),
                "task_count": len(plan.integration_tasks)
            }
            del self.active_plans[plan_id]
        
        self.logger.info(f"Cleaned up {len(plans_to_remove)} completed integration plans")
        
        return {
            "cleaned_plans": len(plans_to_remove),
            "archived_plans": archived_plans,
            "remaining_active_plans": len(self.active_plans)
        }