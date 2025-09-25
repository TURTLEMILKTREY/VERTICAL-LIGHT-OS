"""
Third-Party Analytics Integration Service
Real data collection from healthcare analytics platforms and business intelligence systems
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import aiohttp
from aiohttp import ClientSession, ClientTimeout
import pandas as pd
from pathlib import Path
import base64
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote
import hashlib
import hmac
from io import StringIO, BytesIO

from ...models.hospital_benchmarks import (
    Hospital, CityTier, HospitalType, SpecialtyType
)
from ...config.advanced_config_manager import ConfigManager
from ...services.shared.error_handling import ApplicationError


class AnalyticsPlatform(Enum):
    """Supported analytics platforms"""
    TABLEAU_SERVER = "tableau_server"
    POWER_BI = "power_bi"
    QLIK_SENSE = "qlik_sense"
    LOOKER = "looker"
    SISENSE = "sisense"
    DOMO = "domo"
    PENTAHO = "pentaho"
    SAP_ANALYTICS = "sap_analytics"
    IBM_COGNOS = "ibm_cognos"
    ORACLE_ANALYTICS = "oracle_analytics"
    GOOGLE_DATA_STUDIO = "google_data_studio"
    CUSTOM_DASHBOARD = "custom_dashboard"


class DataVisualizationType(Enum):
    """Types of healthcare data visualizations"""
    PERFORMANCE_DASHBOARD = "performance_dashboard"
    FINANCIAL_REPORT = "financial_report"
    CLINICAL_METRICS = "clinical_metrics"
    OPERATIONAL_KPI = "operational_kpi"
    PATIENT_ANALYTICS = "patient_analytics"
    QUALITY_SCORECARD = "quality_scorecard"
    GOVERNMENT_SCHEME_REPORT = "government_scheme_report"
    BENCHMARK_COMPARISON = "benchmark_comparison"
    TREND_ANALYSIS = "trend_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"


@dataclass
class AnalyticsPlatformConfig:
    """Analytics platform configuration"""
    platform_id: str
    platform_name: str
    platform_type: AnalyticsPlatform
    server_url: str
    authentication: Dict[str, str]
    site_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    available_reports: List[str] = field(default_factory=list)
    data_refresh_schedule: str = "daily"
    hospital_ids_covered: List[str] = field(default_factory=list)
    active: bool = True


@dataclass
class AnalyticsDataSource:
    """Analytics data source configuration"""
    source_id: str
    platform_config: AnalyticsPlatformConfig
    report_name: str
    visualization_type: DataVisualizationType
    data_fields: List[str]
    hospital_filter_field: str
    date_filter_field: str
    export_format: str = "csv"  # csv, json, excel, pdf
    refresh_frequency: str = "daily"
    quality_threshold: int = 70


@dataclass
class AnalyticsDataPoint:
    """Individual analytics data point"""
    hospital_id: str
    metric_name: str
    metric_value: Union[Decimal, int, float, str]
    metric_category: str
    measurement_date: datetime
    data_source: str
    platform_type: AnalyticsPlatform
    confidence_score: int = 100


class ThirdPartyAnalyticsError(ApplicationError):
    """Third-party analytics integration errors"""
    pass


class ThirdPartyAnalyticsIntegrator:
    """Production Third-Party Analytics Integration Service"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Analytics platform configurations
        self.platform_configs: Dict[str, AnalyticsPlatformConfig] = {}
        
        # Data source configurations
        self.data_sources: Dict[str, AnalyticsDataSource] = {}
        
        # Active sessions for platforms
        self.platform_sessions: Dict[str, ClientSession] = {}
        
        # Data mapping configurations
        self.field_mappings = self._initialize_field_mappings()
        
        # Load platform configurations
        self._load_platform_configurations()
        
        # Initialize platform integrations
        self._initialize_platform_integrations()
    
    def _initialize_field_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize field mappings for different analytics platforms"""
        
        return {
            # Tableau Healthcare Dashboard Mappings
            "tableau_hospital_performance": {
                "bed_occupancy_rate": "Bed Occupancy %",
                "average_length_of_stay": "Avg LOS (Days)",
                "or_utilization_rate": "OR Utilization %", 
                "emergency_wait_time": "ER Wait Time (Min)",
                "patient_satisfaction": "Patient Satisfaction Score",
                "readmission_rate": "30-Day Readmission %",
                "total_revenue": "Total Revenue (INR)",
                "total_admissions": "Total Admissions",
                "discharge_count": "Total Discharges"
            },
            
            "tableau_financial_analytics": {
                "gross_revenue": "Gross Revenue",
                "net_revenue": "Net Revenue", 
                "total_expenses": "Total Operating Expenses",
                "ebitda": "EBITDA",
                "profit_margin": "Operating Margin %",
                "revenue_per_bed": "Revenue per Bed",
                "cost_per_patient": "Cost per Patient",
                "accounts_receivable": "A/R Days Outstanding"
            },
            
            # Power BI Healthcare Mappings
            "powerbi_clinical_dashboard": {
                "mortality_rate": "Hospital Mortality Rate",
                "infection_rate": "Healthcare Associated Infections",
                "medication_errors": "Medication Error Rate",
                "fall_incidents": "Patient Fall Rate",
                "pressure_ulcer_rate": "Pressure Ulcer Incidence",
                "surgical_site_infections": "SSI Rate",
                "ventilator_days": "Ventilator Utilization Days",
                "icu_mortality": "ICU Mortality Rate"
            },
            
            "powerbi_operational_metrics": {
                "staff_turnover": "Nursing Turnover Rate",
                "overtime_hours": "Overtime Hours %",
                "patient_complaints": "Patient Complaints Count",
                "equipment_downtime": "Equipment Downtime %",
                "pharmacy_turnaround": "Pharmacy TAT (Min)",
                "lab_turnaround": "Lab TAT (Hours)",
                "radiology_turnaround": "Radiology TAT (Hours)"
            },
            
            # QlikSense Health Analytics
            "qlik_quality_scorecard": {
                "cms_star_rating": "CMS Star Rating",
                "jhaco_score": "JCAHO Score",
                "patient_experience": "HCAHPS Score", 
                "safety_score": "Patient Safety Score",
                "clinical_outcomes": "Clinical Outcomes Score",
                "process_measures": "Process Measures Score"
            },
            
            # Government Scheme Analytics
            "analytics_government_schemes": {
                "pmjay_cases": "Ayushman Bharat Cases",
                "pmjay_revenue": "AB-PMJAY Revenue (INR)",
                "cghs_patients": "CGHS Beneficiaries",
                "cghs_reimbursement": "CGHS Reimbursement (INR)",
                "esi_cases": "ESI Cases Treated",
                "esi_settlement": "ESI Settlement Amount",
                "state_scheme_revenue": "State Scheme Revenue"
            },
            
            # Custom Hospital Dashboards
            "custom_executive_dashboard": {
                "total_patients": "Total Patients Treated",
                "average_stay": "Average Length of Stay",
                "bed_utilization": "Bed Utilization Rate",
                "revenue_growth": "Revenue Growth %",
                "cost_reduction": "Cost Reduction %",
                "quality_index": "Overall Quality Index",
                "staff_satisfaction": "Staff Satisfaction Score",
                "technology_adoption": "Technology Adoption Rate"
            }
        }
    
    def _load_platform_configurations(self) -> None:
        """Load analytics platform configurations"""
        
        try:
            # Sample configurations for major Indian healthcare analytics setups
            configs = [
                AnalyticsPlatformConfig(
                    platform_id="apollo_tableau",
                    platform_name="Apollo Hospitals Tableau Server",
                    platform_type=AnalyticsPlatform.TABLEAU_SERVER,
                    server_url="https://analytics.apollohospitals.com",
                    authentication={
                        "auth_type": "tableau_auth",
                        "username": "api_user",
                        "password": "encrypted_password",
                        "site_id": "apollo_health"
                    },
                    available_reports=[
                        "Hospital Performance Dashboard",
                        "Financial Analytics Report", 
                        "Quality Metrics Scorecard",
                        "Government Scheme Analytics"
                    ],
                    hospital_ids_covered=["APOLLO_001", "APOLLO_002", "APOLLO_003"]
                ),
                
                AnalyticsPlatformConfig(
                    platform_id="fortis_powerbi",
                    platform_name="Fortis Healthcare Power BI",
                    platform_type=AnalyticsPlatform.POWER_BI,
                    server_url="https://app.powerbi.com",
                    authentication={
                        "auth_type": "azure_ad",
                        "tenant_id": "fortis_tenant_id",
                        "client_id": "powerbi_client_id",
                        "client_secret": "encrypted_secret"
                    },
                    workspace_id="fortis_healthcare_workspace",
                    available_reports=[
                        "Clinical Performance Dashboard",
                        "Operational Metrics Report",
                        "Patient Analytics Dashboard"
                    ],
                    hospital_ids_covered=["FORTIS_001", "FORTIS_002", "FORTIS_003"]
                ),
                
                AnalyticsPlatformConfig(
                    platform_id="max_qlik",
                    platform_name="Max Healthcare QlikSense",
                    platform_type=AnalyticsPlatform.QLIK_SENSE,
                    server_url="https://qlik.maxhealthcare.in",
                    authentication={
                        "auth_type": "qlik_jwt",
                        "api_key": "encrypted_api_key",
                        "user_directory": "MAX_HEALTH",
                        "user_id": "analytics_api"
                    },
                    available_reports=[
                        "Quality Scorecard",
                        "Executive Summary Dashboard",
                        "Benchmark Comparison Report"
                    ],
                    hospital_ids_covered=["MAX_001", "MAX_002", "MAX_003"]
                ),
                
                AnalyticsPlatformConfig(
                    platform_id="aiims_custom",
                    platform_name="AIIMS Custom Analytics Platform",
                    platform_type=AnalyticsPlatform.CUSTOM_DASHBOARD,
                    server_url="https://analytics.aiims.edu",
                    authentication={
                        "auth_type": "api_key",
                        "api_key": "encrypted_aiims_key",
                        "department": "hospital_administration"
                    },
                    available_reports=[
                        "Government Scheme Analytics",
                        "Academic Hospital Metrics",
                        "Research Performance Data"
                    ],
                    hospital_ids_covered=["AIIMS_001", "AIIMS_002"]
                )
            ]
            
            for config in configs:
                self.platform_configs[config.platform_id] = config
                
            self.logger.info(f"Loaded {len(self.platform_configs)} analytics platform configurations")
            
        except Exception as e:
            self.logger.error(f"Failed to load platform configurations: {str(e)}")
    
    def _initialize_platform_integrations(self) -> None:
        """Initialize platform-specific integrations"""
        
        # Create data source configurations for each platform
        data_sources = []
        
        for platform_id, platform_config in self.platform_configs.items():
            
            if platform_config.platform_type == AnalyticsPlatform.TABLEAU_SERVER:
                # Tableau data sources
                data_sources.extend([
                    AnalyticsDataSource(
                        source_id=f"{platform_id}_performance",
                        platform_config=platform_config,
                        report_name="Hospital Performance Dashboard",
                        visualization_type=DataVisualizationType.PERFORMANCE_DASHBOARD,
                        data_fields=list(self.field_mappings["tableau_hospital_performance"].keys()),
                        hospital_filter_field="Hospital ID",
                        date_filter_field="Report Date"
                    ),
                    AnalyticsDataSource(
                        source_id=f"{platform_id}_financial",
                        platform_config=platform_config,
                        report_name="Financial Analytics Report",
                        visualization_type=DataVisualizationType.FINANCIAL_REPORT,
                        data_fields=list(self.field_mappings["tableau_financial_analytics"].keys()),
                        hospital_filter_field="Hospital ID",
                        date_filter_field="Report Date"
                    )
                ])
            
            elif platform_config.platform_type == AnalyticsPlatform.POWER_BI:
                # Power BI data sources
                data_sources.extend([
                    AnalyticsDataSource(
                        source_id=f"{platform_id}_clinical",
                        platform_config=platform_config,
                        report_name="Clinical Performance Dashboard",
                        visualization_type=DataVisualizationType.CLINICAL_METRICS,
                        data_fields=list(self.field_mappings["powerbi_clinical_dashboard"].keys()),
                        hospital_filter_field="HospitalId",
                        date_filter_field="ReportDate"
                    ),
                    AnalyticsDataSource(
                        source_id=f"{platform_id}_operational",
                        platform_config=platform_config,
                        report_name="Operational Metrics Report",
                        visualization_type=DataVisualizationType.OPERATIONAL_KPI,
                        data_fields=list(self.field_mappings["powerbi_operational_metrics"].keys()),
                        hospital_filter_field="HospitalId",
                        date_filter_field="ReportDate"
                    )
                ])
            
            elif platform_config.platform_type == AnalyticsPlatform.QLIK_SENSE:
                # QlikSense data sources
                data_sources.append(
                    AnalyticsDataSource(
                        source_id=f"{platform_id}_quality",
                        platform_config=platform_config,
                        report_name="Quality Scorecard",
                        visualization_type=DataVisualizationType.QUALITY_SCORECARD,
                        data_fields=list(self.field_mappings["qlik_quality_scorecard"].keys()),
                        hospital_filter_field="Hospital_ID",
                        date_filter_field="Measurement_Date"
                    )
                )
            
            elif platform_config.platform_type == AnalyticsPlatform.CUSTOM_DASHBOARD:
                # Custom dashboard data sources
                data_sources.extend([
                    AnalyticsDataSource(
                        source_id=f"{platform_id}_government",
                        platform_config=platform_config,
                        report_name="Government Scheme Analytics", 
                        visualization_type=DataVisualizationType.GOVERNMENT_SCHEME_REPORT,
                        data_fields=list(self.field_mappings["analytics_government_schemes"].keys()),
                        hospital_filter_field="hospital_id",
                        date_filter_field="report_date"
                    ),
                    AnalyticsDataSource(
                        source_id=f"{platform_id}_executive",
                        platform_config=platform_config,
                        report_name="Executive Summary Dashboard",
                        visualization_type=DataVisualizationType.EXECUTIVE_SUMMARY,
                        data_fields=list(self.field_mappings["custom_executive_dashboard"].keys()),
                        hospital_filter_field="hospital_id",
                        date_filter_field="report_date"
                    )
                ])
        
        # Store data sources
        for source in data_sources:
            self.data_sources[source.source_id] = source
        
        self.logger.info(f"Initialized {len(self.data_sources)} analytics data sources")
    
    async def collect_analytics_data(self, platform_id: str,
                                   hospital_ids: Optional[List[str]] = None,
                                   date_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """Collect data from analytics platform"""
        
        try:
            platform_config = self.platform_configs.get(platform_id)
            if not platform_config:
                raise ThirdPartyAnalyticsError(f"Analytics platform {platform_id} not configured")
            
            if not platform_config.active:
                raise ThirdPartyAnalyticsError(f"Analytics platform {platform_id} is inactive")
            
            # Get target hospitals
            target_hospitals = hospital_ids or platform_config.hospital_ids_covered
            
            # Set date range (default to last 30 days)
            if not date_range:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
                date_range = {"start_date": start_date, "end_date": end_date}
            
            collection_results = {
                "platform_id": platform_id,
                "platform_name": platform_config.platform_name,
                "platform_type": platform_config.platform_type.value,
                "collection_timestamp": datetime.utcnow().isoformat(),
                "target_hospitals": len(target_hospitals),
                "date_range": {
                    "start_date": date_range["start_date"].isoformat(),
                    "end_date": date_range["end_date"].isoformat()
                },
                "collected_data": {},
                "data_sources_processed": [],
                "total_data_points": 0,
                "quality_scores": {},
                "errors": []
            }
            
            # Get platform session
            session = await self._get_platform_session(platform_config)
            
            try:
                # Collect data from each configured data source
                platform_data_sources = [ds for ds in self.data_sources.values() 
                                       if ds.platform_config.platform_id == platform_id]
                
                for data_source in platform_data_sources:
                    try:
                        source_data = await self._collect_from_data_source(
                            session, data_source, target_hospitals, date_range
                        )
                        
                        if source_data:
                            collection_results["collected_data"][data_source.source_id] = source_data
                            collection_results["data_sources_processed"].append(data_source.source_id)
                            collection_results["total_data_points"] += len(source_data.get("data_points", []))
                            
                            # Calculate quality score for this data source
                            quality_score = self._calculate_data_quality_score(source_data)
                            collection_results["quality_scores"][data_source.source_id] = quality_score
                        
                    except Exception as e:
                        error_msg = f"Failed to collect from data source {data_source.source_id}: {str(e)}"
                        collection_results["errors"].append(error_msg)
                        self.logger.error(error_msg)
                
                # Calculate overall collection success
                collection_results["success"] = len(collection_results["data_sources_processed"]) > 0
                
                if collection_results["quality_scores"]:
                    scores = list(collection_results["quality_scores"].values())
                    collection_results["overall_quality_score"] = int(sum(scores) / len(scores))
                else:
                    collection_results["overall_quality_score"] = 0
                
                self.logger.info(f"Analytics collection completed for {platform_id}: {collection_results['total_data_points']} data points")
                
                return collection_results
                
            finally:
                if platform_id in self.platform_sessions:
                    await self.platform_sessions[platform_id].close()
                    del self.platform_sessions[platform_id]
            
        except Exception as e:
            self.logger.error(f"Analytics data collection failed for {platform_id}: {str(e)}")
            return {
                "success": False,
                "platform_id": platform_id,
                "error": str(e),
                "collection_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_platform_session(self, platform_config: AnalyticsPlatformConfig) -> ClientSession:
        """Get authenticated session for analytics platform"""
        
        if platform_config.platform_id in self.platform_sessions:
            return self.platform_sessions[platform_config.platform_id]
        
        timeout = ClientTimeout(total=60, connect=30)
        
        headers = {
            "User-Agent": "VerticalLight-Analytics-Integrator/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Apply platform-specific authentication
        if platform_config.platform_type == AnalyticsPlatform.TABLEAU_SERVER:
            session = await self._authenticate_tableau(platform_config, headers, timeout)
            
        elif platform_config.platform_type == AnalyticsPlatform.POWER_BI:
            session = await self._authenticate_power_bi(platform_config, headers, timeout)
            
        elif platform_config.platform_type == AnalyticsPlatform.QLIK_SENSE:
            session = await self._authenticate_qlik_sense(platform_config, headers, timeout)
            
        elif platform_config.platform_type == AnalyticsPlatform.CUSTOM_DASHBOARD:
            session = await self._authenticate_custom_dashboard(platform_config, headers, timeout)
            
        else:
            # Generic API key authentication
            api_key = platform_config.authentication.get("api_key")
            headers["X-API-Key"] = api_key
            session = ClientSession(headers=headers, timeout=timeout)
        
        self.platform_sessions[platform_config.platform_id] = session
        return session
    
    async def _authenticate_tableau(self, config: AnalyticsPlatformConfig, 
                                  headers: Dict[str, str], timeout: ClientTimeout) -> ClientSession:
        """Authenticate with Tableau Server"""
        
        auth_url = f"{config.server_url}/api/3.0/auth/signin"
        
        auth_payload = {
            "credentials": {
                "name": config.authentication["username"],
                "password": config.authentication["password"],
                "site": {"contentUrl": config.authentication.get("site_id", "")}
            }
        }
        
        session = ClientSession(timeout=timeout)
        
        try:
            async with session.post(auth_url, json=auth_payload) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    token = auth_data["credentials"]["token"]
                    site_id = auth_data["credentials"]["site"]["id"]
                    
                    # Update headers with auth token
                    headers["X-Tableau-Auth"] = token
                    headers["X-Tableau-Site-Id"] = site_id
                    
                    # Create new session with auth headers
                    await session.close()
                    return ClientSession(headers=headers, timeout=timeout)
                else:
                    raise ThirdPartyAnalyticsError(f"Tableau authentication failed: {response.status}")
        
        except Exception as e:
            await session.close()
            raise ThirdPartyAnalyticsError(f"Tableau authentication error: {str(e)}")
    
    async def _authenticate_power_bi(self, config: AnalyticsPlatformConfig,
                                   headers: Dict[str, str], timeout: ClientTimeout) -> ClientSession:
        """Authenticate with Power BI using Azure AD"""
        
        # Azure AD OAuth2 flow for Power BI
        token_url = f"https://login.microsoftonline.com/{config.authentication['tenant_id']}/oauth2/v2.0/token"
        
        token_payload = {
            "grant_type": "client_credentials",
            "client_id": config.authentication["client_id"],
            "client_secret": config.authentication["client_secret"],
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        }
        
        session = ClientSession(timeout=timeout)
        
        try:
            async with session.post(token_url, data=token_payload) as response:
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data["access_token"]
                    
                    # Update headers with bearer token
                    headers["Authorization"] = f"Bearer {access_token}"
                    
                    # Create new session with auth headers
                    await session.close()
                    return ClientSession(headers=headers, timeout=timeout)
                else:
                    raise ThirdPartyAnalyticsError(f"Power BI authentication failed: {response.status}")
                    
        except Exception as e:
            await session.close()
            raise ThirdPartyAnalyticsError(f"Power BI authentication error: {str(e)}")
    
    async def _authenticate_qlik_sense(self, config: AnalyticsPlatformConfig,
                                     headers: Dict[str, str], timeout: ClientTimeout) -> ClientSession:
        """Authenticate with QlikSense using JWT"""
        
        # QlikSense JWT authentication
        import jwt
        
        jwt_payload = {
            "iss": "VerticalLight",
            "aud": "qlik.api",
            "sub": config.authentication["user_id"],
            "name": config.authentication["user_id"],
            "email": f"{config.authentication['user_id']}@{config.authentication['user_directory'].lower()}.com",
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        }
        
        # Create JWT token (private key would be configured in production)
        jwt_token = jwt.encode(jwt_payload, config.authentication["api_key"], algorithm="HS256")
        
        headers["Authorization"] = f"Bearer {jwt_token}"
        
        return ClientSession(headers=headers, timeout=timeout)
    
    async def _authenticate_custom_dashboard(self, config: AnalyticsPlatformConfig,
                                           headers: Dict[str, str], timeout: ClientTimeout) -> ClientSession:
        """Authenticate with custom dashboard API"""
        
        # Custom API key authentication
        headers["X-API-Key"] = config.authentication["api_key"]
        
        if "department" in config.authentication:
            headers["X-Department"] = config.authentication["department"]
        
        return ClientSession(headers=headers, timeout=timeout)
    
    async def _collect_from_data_source(self, session: ClientSession,
                                      data_source: AnalyticsDataSource,
                                      hospital_ids: List[str],
                                      date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Collect data from specific analytics data source"""
        
        try:
            if data_source.platform_config.platform_type == AnalyticsPlatform.TABLEAU_SERVER:
                return await self._collect_tableau_data(session, data_source, hospital_ids, date_range)
                
            elif data_source.platform_config.platform_type == AnalyticsPlatform.POWER_BI:
                return await self._collect_power_bi_data(session, data_source, hospital_ids, date_range)
                
            elif data_source.platform_config.platform_type == AnalyticsPlatform.QLIK_SENSE:
                return await self._collect_qlik_data(session, data_source, hospital_ids, date_range)
                
            elif data_source.platform_config.platform_type == AnalyticsPlatform.CUSTOM_DASHBOARD:
                return await self._collect_custom_dashboard_data(session, data_source, hospital_ids, date_range)
                
            else:
                raise ThirdPartyAnalyticsError(f"Unsupported platform type: {data_source.platform_config.platform_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to collect from data source {data_source.source_id}: {str(e)}")
            raise
    
    async def _collect_tableau_data(self, session: ClientSession,
                                  data_source: AnalyticsDataSource,
                                  hospital_ids: List[str],
                                  date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Collect data from Tableau Server"""
        
        base_url = data_source.platform_config.server_url
        
        # Find workbook and view
        workbooks_url = f"{base_url}/api/3.0/sites/{data_source.platform_config.site_id}/workbooks"
        
        async with session.get(workbooks_url) as response:
            if response.status != 200:
                raise ThirdPartyAnalyticsError(f"Failed to get Tableau workbooks: {response.status}")
            
            workbooks_data = await response.json()
            
            # Find the workbook containing our report
            target_workbook = None
            for workbook in workbooks_data.get("workbooks", {}).get("workbook", []):
                if data_source.report_name.lower() in workbook.get("name", "").lower():
                    target_workbook = workbook
                    break
            
            if not target_workbook:
                raise ThirdPartyAnalyticsError(f"Workbook for report '{data_source.report_name}' not found")
        
        # Get views from workbook
        workbook_id = target_workbook["id"]
        views_url = f"{base_url}/api/3.0/sites/{data_source.platform_config.site_id}/workbooks/{workbook_id}/views"
        
        async with session.get(views_url) as response:
            if response.status != 200:
                raise ThirdPartyAnalyticsError(f"Failed to get Tableau views: {response.status}")
            
            views_data = await response.json()
            
            # Export data from each view
            collected_data_points = []
            
            for view in views_data.get("views", {}).get("view", []):
                view_id = view["id"]
                
                # Export view data as CSV
                export_url = f"{base_url}/api/3.0/sites/{data_source.platform_config.site_id}/views/{view_id}/data"
                
                # Apply filters for hospitals and date range
                params = {
                    "maxAge": "1",  # Fresh data
                    "includeAll": "true"
                }
                
                async with session.get(export_url, params=params) as export_response:
                    if export_response.status == 200:
                        csv_content = await export_response.text()
                        
                        # Parse CSV data
                        df = pd.read_csv(StringIO(csv_content))
                        
                        # Filter for target hospitals
                        if data_source.hospital_filter_field in df.columns:
                            df_filtered = df[df[data_source.hospital_filter_field].isin(hospital_ids)]
                        else:
                            df_filtered = df
                        
                        # Convert to data points
                        view_data_points = self._convert_tableau_data_to_points(
                            df_filtered, data_source, view["name"]
                        )
                        collected_data_points.extend(view_data_points)
        
        return {
            "data_source_id": data_source.source_id,
            "report_name": data_source.report_name,
            "visualization_type": data_source.visualization_type.value,
            "collection_timestamp": datetime.utcnow().isoformat(),
            "data_points": collected_data_points,
            "hospitals_covered": list(set([dp.hospital_id for dp in collected_data_points]))
        }
    
    async def _collect_power_bi_data(self, session: ClientSession,
                                   data_source: AnalyticsDataSource,
                                   hospital_ids: List[str],
                                   date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Collect data from Power BI"""
        
        workspace_id = data_source.platform_config.workspace_id
        base_url = "https://api.powerbi.com/v1.0/myorg"
        
        # Get datasets in workspace
        datasets_url = f"{base_url}/groups/{workspace_id}/datasets"
        
        async with session.get(datasets_url) as response:
            if response.status != 200:
                raise ThirdPartyAnalyticsError(f"Failed to get Power BI datasets: {response.status}")
            
            datasets_data = await response.json()
            
            collected_data_points = []
            
            for dataset in datasets_data.get("value", []):
                dataset_id = dataset["id"]
                
                # Execute DAX query to get data
                query_url = f"{base_url}/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
                
                # Build DAX query for hospital data
                dax_query = self._build_power_bi_dax_query(data_source, hospital_ids, date_range)
                
                query_payload = {
                    "queries": [{
                        "query": dax_query
                    }]
                }
                
                async with session.post(query_url, json=query_payload) as query_response:
                    if query_response.status == 200:
                        query_result = await query_response.json()
                        
                        # Process query results
                        dataset_points = self._convert_power_bi_data_to_points(
                            query_result, data_source, dataset["name"]
                        )
                        collected_data_points.extend(dataset_points)
        
        return {
            "data_source_id": data_source.source_id,
            "report_name": data_source.report_name,
            "visualization_type": data_source.visualization_type.value,
            "collection_timestamp": datetime.utcnow().isoformat(),
            "data_points": collected_data_points,
            "hospitals_covered": list(set([dp.hospital_id for dp in collected_data_points]))
        }
    
    async def _collect_qlik_data(self, session: ClientSession,
                               data_source: AnalyticsDataSource,
                               hospital_ids: List[str],
                               date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Collect data from QlikSense"""
        
        base_url = data_source.platform_config.server_url
        
        # Get apps (applications in QlikSense)
        apps_url = f"{base_url}/qrs/app"
        
        async with session.get(apps_url) as response:
            if response.status != 200:
                raise ThirdPartyAnalyticsError(f"Failed to get QlikSense apps: {response.status}")
            
            apps_data = await response.json()
            
            collected_data_points = []
            
            for app in apps_data:
                if data_source.report_name.lower() in app.get("name", "").lower():
                    app_id = app["id"]
                    
                    # Open app session
                    session_url = f"{base_url}/api/v1/apps/{app_id}"
                    
                    async with session.get(session_url) as app_response:
                        if app_response.status == 200:
                            # Execute hypercube query for data
                            hypercube_data = await self._execute_qlik_hypercube_query(
                                session, base_url, app_id, data_source, hospital_ids
                            )
                            
                            # Convert to data points
                            app_points = self._convert_qlik_data_to_points(
                                hypercube_data, data_source, app["name"]
                            )
                            collected_data_points.extend(app_points)
        
        return {
            "data_source_id": data_source.source_id,
            "report_name": data_source.report_name,
            "visualization_type": data_source.visualization_type.value,
            "collection_timestamp": datetime.utcnow().isoformat(),
            "data_points": collected_data_points,
            "hospitals_covered": list(set([dp.hospital_id for dp in collected_data_points]))
        }
    
    async def _collect_custom_dashboard_data(self, session: ClientSession,
                                           data_source: AnalyticsDataSource,
                                           hospital_ids: List[str],
                                           date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Collect data from custom dashboard API"""
        
        base_url = data_source.platform_config.server_url
        
        # Custom API endpoints for different report types
        api_endpoints = {
            DataVisualizationType.GOVERNMENT_SCHEME_REPORT: "/api/v1/government-schemes/data",
            DataVisualizationType.EXECUTIVE_SUMMARY: "/api/v1/executive/summary",
            DataVisualizationType.PERFORMANCE_DASHBOARD: "/api/v1/performance/metrics",
            DataVisualizationType.QUALITY_SCORECARD: "/api/v1/quality/scores"
        }
        
        endpoint = api_endpoints.get(data_source.visualization_type, "/api/v1/data")
        url = f"{base_url}{endpoint}"
        
        # Build query parameters
        params = {
            "hospital_ids": ",".join(hospital_ids),
            "start_date": date_range["start_date"].strftime("%Y-%m-%d"),
            "end_date": date_range["end_date"].strftime("%Y-%m-%d"),
            "fields": ",".join(data_source.data_fields),
            "format": "json"
        }
        
        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise ThirdPartyAnalyticsError(f"Custom dashboard API request failed: {response.status}")
            
            api_data = await response.json()
            
            # Convert API response to data points
            data_points = self._convert_custom_api_data_to_points(
                api_data, data_source
            )
        
        return {
            "data_source_id": data_source.source_id,
            "report_name": data_source.report_name,
            "visualization_type": data_source.visualization_type.value,
            "collection_timestamp": datetime.utcnow().isoformat(),
            "data_points": data_points,
            "hospitals_covered": list(set([dp.hospital_id for dp in data_points]))
        }
    
    def _convert_tableau_data_to_points(self, df: pd.DataFrame,
                                      data_source: AnalyticsDataSource,
                                      view_name: str) -> List[AnalyticsDataPoint]:
        """Convert Tableau CSV data to analytics data points"""
        
        data_points = []
        field_mapping = self.field_mappings.get("tableau_hospital_performance", {})
        
        for _, row in df.iterrows():
            hospital_id = row.get(data_source.hospital_filter_field, "unknown")
            measurement_date = datetime.utcnow()
            
            if data_source.date_filter_field in row:
                try:
                    measurement_date = pd.to_datetime(row[data_source.date_filter_field])
                except:
                    pass
            
            # Convert each mapped field to a data point
            for standard_field, tableau_field in field_mapping.items():
                if tableau_field in row and pd.notna(row[tableau_field]):
                    data_point = AnalyticsDataPoint(
                        hospital_id=str(hospital_id),
                        metric_name=standard_field,
                        metric_value=self._convert_metric_value(row[tableau_field]),
                        metric_category=data_source.visualization_type.value,
                        measurement_date=measurement_date,
                        data_source=f"tableau_{view_name}",
                        platform_type=AnalyticsPlatform.TABLEAU_SERVER,
                        confidence_score=90
                    )
                    data_points.append(data_point)
        
        return data_points
    
    def _build_power_bi_dax_query(self, data_source: AnalyticsDataSource,
                                hospital_ids: List[str],
                                date_range: Dict[str, datetime]) -> str:
        """Build DAX query for Power BI data extraction"""
        
        hospital_filter = "'" + "','".join(hospital_ids) + "'"
        start_date = date_range["start_date"].strftime("%Y-%m-%d")
        end_date = date_range["end_date"].strftime("%Y-%m-%d")
        
        # Sample DAX query for hospital performance data
        dax_query = f"""
        EVALUATE
        FILTER(
            ADDCOLUMNS(
                VALUES(HospitalData[{data_source.hospital_filter_field}]),
                "BedOccupancy", CALCULATE(AVERAGE(HospitalData[BedOccupancyRate])),
                "AvgLOS", CALCULATE(AVERAGE(HospitalData[LengthOfStay])),
                "PatientSatisfaction", CALCULATE(AVERAGE(HospitalData[PatientSatisfaction])),
                "TotalRevenue", CALCULATE(SUM(HospitalData[Revenue])),
                "ReportDate", MAX(HospitalData[{data_source.date_filter_field}])
            ),
            HospitalData[{data_source.hospital_filter_field}] IN {{{hospital_filter}}} &&
            HospitalData[{data_source.date_filter_field}] >= DATE({start_date}) &&
            HospitalData[{data_source.date_filter_field}] <= DATE({end_date})
        )
        """
        
        return dax_query
    
    def _convert_power_bi_data_to_points(self, query_result: Dict[str, Any],
                                       data_source: AnalyticsDataSource,
                                       dataset_name: str) -> List[AnalyticsDataPoint]:
        """Convert Power BI query results to analytics data points"""
        
        data_points = []
        
        for result in query_result.get("results", []):
            for table in result.get("tables", []):
                for row in table.get("rows", []):
                    hospital_id = row[0] if row else "unknown"
                    measurement_date = datetime.utcnow()
                    
                    # Map Power BI columns to standard metrics
                    field_mapping = self.field_mappings.get("powerbi_clinical_dashboard", {})
                    
                    for i, (standard_field, _) in enumerate(field_mapping.items()):
                        if i + 1 < len(row) and row[i + 1] is not None:
                            data_point = AnalyticsDataPoint(
                                hospital_id=str(hospital_id),
                                metric_name=standard_field,
                                metric_value=self._convert_metric_value(row[i + 1]),
                                metric_category=data_source.visualization_type.value,
                                measurement_date=measurement_date,
                                data_source=f"powerbi_{dataset_name}",
                                platform_type=AnalyticsPlatform.POWER_BI,
                                confidence_score=85
                            )
                            data_points.append(data_point)
        
        return data_points
    
    async def _execute_qlik_hypercube_query(self, session: ClientSession,
                                          base_url: str, app_id: str,
                                          data_source: AnalyticsDataSource,
                                          hospital_ids: List[str]) -> Dict[str, Any]:
        """Execute QlikSense hypercube query for data extraction"""
        
        # QlikSense hypercube definition for data extraction
        hypercube_def = {
            "qDimensions": [
                {
                    "qDef": {
                        "qFieldDefs": [data_source.hospital_filter_field],
                        "qSortCriterias": [{"qSortByAscii": 1}]
                    }
                }
            ],
            "qMeasures": [
                {"qDef": {"qDef": f"Avg([{field}])"}} 
                for field in data_source.data_fields[:10]  # Limit to 10 measures
            ],
            "qInitialDataFetch": [{
                "qTop": 0,
                "qLeft": 0,
                "qHeight": 1000,
                "qWidth": 20
            }]
        }
        
        # Create hypercube object
        hypercube_url = f"{base_url}/api/v1/apps/{app_id}/objects"
        
        hypercube_payload = {
            "qInfo": {"qType": "hypercube"},
            "qHyperCubeDef": hypercube_def
        }
        
        async with session.post(hypercube_url, json=hypercube_payload) as response:
            if response.status == 201:
                hypercube_object = await response.json()
                object_id = hypercube_object["qInfo"]["qId"]
                
                # Get data from hypercube
                data_url = f"{base_url}/api/v1/apps/{app_id}/objects/{object_id}/layout"
                
                async with session.get(data_url) as data_response:
                    if data_response.status == 200:
                        return await data_response.json()
        
        return {}
    
    def _convert_qlik_data_to_points(self, hypercube_data: Dict[str, Any],
                                   data_source: AnalyticsDataSource,
                                   app_name: str) -> List[AnalyticsDataPoint]:
        """Convert QlikSense hypercube data to analytics data points"""
        
        data_points = []
        
        layout = hypercube_data.get("qLayout", {})
        hypercube = layout.get("qHyperCube", {})
        data_pages = hypercube.get("qDataPages", [])
        
        for page in data_pages:
            for row in page.get("qMatrix", []):
                if row:
                    hospital_id = row[0].get("qText", "unknown")
                    measurement_date = datetime.utcnow()
                    
                    # Convert measures to data points
                    field_mapping = self.field_mappings.get("qlik_quality_scorecard", {})
                    
                    for i, (standard_field, _) in enumerate(field_mapping.items()):
                        if i + 1 < len(row) and row[i + 1].get("qNum") is not None:
                            data_point = AnalyticsDataPoint(
                                hospital_id=str(hospital_id),
                                metric_name=standard_field,
                                metric_value=self._convert_metric_value(row[i + 1]["qNum"]),
                                metric_category=data_source.visualization_type.value,
                                measurement_date=measurement_date,
                                data_source=f"qlik_{app_name}",
                                platform_type=AnalyticsPlatform.QLIK_SENSE,
                                confidence_score=88
                            )
                            data_points.append(data_point)
        
        return data_points
    
    def _convert_custom_api_data_to_points(self, api_data: Dict[str, Any],
                                         data_source: AnalyticsDataSource) -> List[AnalyticsDataPoint]:
        """Convert custom API data to analytics data points"""
        
        data_points = []
        
        # Handle different API response formats
        if "data" in api_data:
            records = api_data["data"]
        elif "hospitals" in api_data:
            records = api_data["hospitals"]
        else:
            records = [api_data]  # Single record response
        
        field_mapping = self.field_mappings.get("analytics_government_schemes", {})
        
        for record in records:
            hospital_id = record.get("hospital_id", record.get("id", "unknown"))
            measurement_date = datetime.utcnow()
            
            if "report_date" in record:
                try:
                    measurement_date = datetime.fromisoformat(record["report_date"])
                except:
                    pass
            
            # Convert each field to a data point
            for standard_field, api_field in field_mapping.items():
                if api_field in record and record[api_field] is not None:
                    data_point = AnalyticsDataPoint(
                        hospital_id=str(hospital_id),
                        metric_name=standard_field,
                        metric_value=self._convert_metric_value(record[api_field]),
                        metric_category=data_source.visualization_type.value,
                        measurement_date=measurement_date,
                        data_source="custom_api",
                        platform_type=AnalyticsPlatform.CUSTOM_DASHBOARD,
                        confidence_score=80
                    )
                    data_points.append(data_point)
        
        return data_points
    
    def _convert_metric_value(self, value: Any) -> Union[Decimal, int, float, str]:
        """Convert metric value to appropriate type"""
        
        if value is None:
            return "N/A"
        
        if isinstance(value, str):
            # Try to convert string to number
            cleaned_value = value.replace(",", "").replace("%", "").strip()
            try:
                if "." in cleaned_value:
                    return Decimal(cleaned_value)
                else:
                    return int(cleaned_value)
            except (ValueError, TypeError):
                return value
        
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        
        return str(value)
    
    def _calculate_data_quality_score(self, source_data: Dict[str, Any]) -> int:
        """Calculate quality score for collected data source"""
        
        data_points = source_data.get("data_points", [])
        
        if not data_points:
            return 0
        
        quality_score = 100
        
        # Completeness check
        total_expected_fields = len(source_data.get("data_fields", []))
        actual_fields = len(set([dp.metric_name for dp in data_points]))
        
        if total_expected_fields > 0:
            completeness = (actual_fields / total_expected_fields) * 100
            if completeness < 80:
                quality_score -= (80 - completeness) * 0.5
        
        # Freshness check
        recent_data = [dp for dp in data_points 
                      if (datetime.utcnow() - dp.measurement_date).days <= 7]
        
        if len(recent_data) / len(data_points) < 0.8:
            quality_score -= 15
        
        # Consistency check (no null/invalid values)
        invalid_values = [dp for dp in data_points 
                         if dp.metric_value in ["N/A", None, "", "null"]]
        
        if len(invalid_values) > 0:
            invalid_ratio = len(invalid_values) / len(data_points)
            quality_score -= invalid_ratio * 20
        
        return max(1, int(quality_score))
    
    async def batch_analytics_collection(self, hospital_ids: List[str],
                                       platform_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Collect analytics data from multiple platforms for multiple hospitals"""
        
        target_platforms = platform_ids or list(self.platform_configs.keys())
        
        batch_results = {
            "batch_id": f"analytics_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "batch_start": datetime.utcnow().isoformat(),
            "target_hospitals": len(hospital_ids),
            "target_platforms": len(target_platforms),
            "platform_results": {},
            "consolidated_data": {},
            "batch_analytics": {}
        }
        
        try:
            # Collect from each platform
            for platform_id in target_platforms:
                try:
                    platform_result = await self.collect_analytics_data(
                        platform_id, hospital_ids
                    )
                    batch_results["platform_results"][platform_id] = platform_result
                    
                except Exception as e:
                    batch_results["platform_results"][platform_id] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Consolidate data across platforms
            consolidated_data = self._consolidate_analytics_data(
                batch_results["platform_results"]
            )
            batch_results["consolidated_data"] = consolidated_data
            
            # Calculate batch analytics
            successful_platforms = [r for r in batch_results["platform_results"].values() 
                                  if r.get("success")]
            
            if successful_platforms:
                total_data_points = sum(r.get("total_data_points", 0) for r in successful_platforms)
                avg_quality = sum(r.get("overall_quality_score", 0) for r in successful_platforms) / len(successful_platforms)
                
                batch_results["batch_analytics"] = {
                    "success_rate": len(successful_platforms) / len(target_platforms) * 100,
                    "total_data_points_collected": total_data_points,
                    "average_quality_score": round(avg_quality, 1),
                    "platforms_successful": len(successful_platforms),
                    "hospitals_with_data": len(set([
                        hospital_id for result in successful_platforms
                        for hospital_id in result.get("collected_data", {}).get("hospitals_covered", [])
                    ]))
                }
            
            batch_results["batch_end"] = datetime.utcnow().isoformat()
            batch_results["success"] = len(successful_platforms) > 0
            
            self.logger.info(f"Analytics batch collection completed: {batch_results['batch_analytics']}")
            
            return batch_results
            
        except Exception as e:
            batch_results["batch_end"] = datetime.utcnow().isoformat()
            batch_results["success"] = False
            batch_results["error"] = str(e)
            
            self.logger.error(f"Analytics batch collection failed: {str(e)}")
            
            return batch_results
    
    def _consolidate_analytics_data(self, platform_results: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate analytics data from multiple platforms"""
        
        consolidated = {
            "hospitals": {},
            "metrics_summary": {},
            "data_sources": [],
            "quality_overview": {}
        }
        
        all_data_points = []
        
        # Collect all data points from successful platforms
        for platform_id, result in platform_results.items():
            if result.get("success") and result.get("collected_data"):
                for source_id, source_data in result["collected_data"].items():
                    data_points = source_data.get("data_points", [])
                    all_data_points.extend(data_points)
                    consolidated["data_sources"].append({
                        "platform_id": platform_id,
                        "source_id": source_id,
                        "data_points_count": len(data_points)
                    })
        
        # Group data points by hospital
        for data_point in all_data_points:
            hospital_id = data_point.hospital_id
            
            if hospital_id not in consolidated["hospitals"]:
                consolidated["hospitals"][hospital_id] = {
                    "hospital_id": hospital_id,
                    "metrics": {},
                    "data_sources": [],
                    "last_updated": None
                }
            
            hospital_data = consolidated["hospitals"][hospital_id]
            
            # Add metric data
            metric_key = f"{data_point.metric_category}_{data_point.metric_name}"
            hospital_data["metrics"][metric_key] = {
                "value": str(data_point.metric_value),
                "measurement_date": data_point.measurement_date.isoformat(),
                "data_source": data_point.data_source,
                "confidence_score": data_point.confidence_score
            }
            
            # Track data sources
            if data_point.data_source not in hospital_data["data_sources"]:
                hospital_data["data_sources"].append(data_point.data_source)
            
            # Update last updated timestamp
            if (not hospital_data["last_updated"] or 
                data_point.measurement_date > datetime.fromisoformat(hospital_data["last_updated"])):
                hospital_data["last_updated"] = data_point.measurement_date.isoformat()
        
        # Generate metrics summary
        metric_names = set()
        for hospital_data in consolidated["hospitals"].values():
            metric_names.update(hospital_data["metrics"].keys())
        
        for metric_name in metric_names:
            values = []
            for hospital_data in consolidated["hospitals"].values():
                if metric_name in hospital_data["metrics"]:
                    try:
                        value = float(hospital_data["metrics"][metric_name]["value"])
                        values.append(value)
                    except (ValueError, TypeError):
                        pass
            
            if values:
                consolidated["metrics_summary"][metric_name] = {
                    "hospitals_reporting": len(values),
                    "min_value": min(values),
                    "max_value": max(values),
                    "average_value": sum(values) / len(values),
                    "total_hospitals": len(consolidated["hospitals"])
                }
        
        return consolidated
    
    def get_analytics_integration_status(self) -> Dict[str, Any]:
        """Get status of analytics integration services"""
        
        status = {
            "configured_platforms": len(self.platform_configs),
            "active_platforms": len([p for p in self.platform_configs.values() if p.active]),
            "configured_data_sources": len(self.data_sources),
            "platform_summary": {},
            "active_sessions": len(self.platform_sessions)
        }
        
        # Platform-wise summary
        for platform_id, config in self.platform_configs.items():
            platform_sources = [ds for ds in self.data_sources.values() 
                              if ds.platform_config.platform_id == platform_id]
            
            status["platform_summary"][platform_id] = {
                "platform_name": config.platform_name,
                "platform_type": config.platform_type.value,
                "active": config.active,
                "hospitals_covered": len(config.hospital_ids_covered),
                "available_reports": len(config.available_reports),
                "configured_data_sources": len(platform_sources),
                "data_refresh_schedule": config.data_refresh_schedule
            }
        
        return status