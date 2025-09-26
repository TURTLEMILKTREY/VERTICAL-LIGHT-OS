"""
Hospital Management System (HMS) Real API Integration
Production-ready integration with Indian HMS systems like MedTech, Birlamedisoft, etc.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import aiohttp
from aiohttp import ClientSession, ClientTimeout, BasicAuth
from cryptography.fernet import Fernet
import hashlib
import hmac
import base64
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from ...models.hospital_benchmarks import (
 Hospital, PerformanceMetrics, FinancialMetrics, 
 GovernmentSchemeData, CityTier, HospitalType, SpecialtyType
)
from ...config.advanced_config_manager import ConfigManager
from ...services.shared.error_handling import ApplicationError


class HMSType(Enum):
 """Supported HMS Systems in India"""
 MEDTECH = "medtech"
 BIRLAMEDISOFT = "birlamedisoft" 
 HMIS_PLUS = "hmis_plus"
 GHANSHYAM_DIGITAL = "ghanshyam_digital"
 NEXGEN_EMR = "nexgen_emr"
 CARESOFT = "caresoft"
 ORION_HEALTHSOFT = "orion_healthsoft"
 HMS_INDIA = "hms_india"
 CUSTOM_API = "custom_api"


@dataclass
class HMSCredentials:
 """HMS System Authentication Credentials"""
 api_key: str
 api_secret: str
 username: Optional[str] = None
 password: Optional[str] = None
 base_url: str = ""
 auth_type: str = "api_key" # api_key, oauth, basic_auth, custom
 additional_headers: Dict[str, str] = None
 tenant_id: Optional[str] = None

 def __post_init__(self):
 if self.additional_headers is None:
 self.additional_headers = {}


@dataclass
class HMSDataMapping:
 """Data field mappings between HMS and our standard format"""
 performance_metrics: Dict[str, str]
 financial_metrics: Dict[str, str]
 patient_data: Dict[str, str]
 staff_metrics: Dict[str, str]
 government_schemes: Dict[str, str]

 @classmethod
 def get_medtech_mapping(cls) -> 'HMSDataMapping':
 """Standard mapping for MedTech HMS"""
 return cls(
 performance_metrics={
 "bed_occupancy_rate": "occupancy.bed_occupancy_percentage",
 "average_length_of_stay": "patients.avg_los_days", 
 "patient_satisfaction_score": "feedback.patient_satisfaction_avg",
 "or_utilization_rate": "operations.or_utilization_pct",
 "ed_average_wait_time": "emergency.avg_wait_time_minutes",
 "staff_patient_ratio": "staffing.nurse_patient_ratio",
 "readmission_rate": "quality.readmission_rate_30day",
 "mortality_rate": "quality.mortality_rate",
 "infection_rate": "quality.hospital_acquired_infection_rate"
 },
 financial_metrics={
 "total_revenue": "finance.total_revenue_monthly",
 "total_costs": "finance.total_costs_monthly", 
 "accounts_receivable_days": "finance.ar_days",
 "cash_percentage": "finance.cash_payer_percentage",
 "insurance_percentage": "finance.insurance_payer_percentage",
 "government_scheme_percentage": "finance.govt_scheme_percentage",
 "bad_debt_percentage": "finance.bad_debt_percentage",
 "ebitda_margin": "finance.ebitda_margin_pct"
 },
 patient_data={
 "total_admissions": "census.total_admissions_monthly",
 "emergency_admissions": "census.emergency_admissions",
 "planned_admissions": "census.planned_admissions", 
 "outpatient_visits": "census.opd_visits_monthly",
 "surgery_cases": "operations.total_surgeries_monthly",
 "icu_admissions": "census.icu_admissions"
 },
 staff_metrics={
 "total_doctors": "staff.doctors_count",
 "total_nurses": "staff.nurses_count",
 "support_staff": "staff.support_staff_count",
 "staff_turnover_rate": "hr.turnover_rate_monthly",
 "staff_satisfaction": "hr.staff_satisfaction_score"
 },
 government_schemes={
 "ayushman_bharat_cases": "schemes.ayushman_cases_monthly",
 "cghs_cases": "schemes.cghs_cases_monthly", 
 "esi_cases": "schemes.esi_cases_monthly",
 "state_scheme_cases": "schemes.state_scheme_cases_monthly",
 "total_scheme_revenue": "schemes.total_revenue_monthly",
 "average_reimbursement_days": "schemes.avg_reimbursement_days"
 }
 )


class HMSAPIIntegrationError(ApplicationError):
 """HMS API Integration specific errors"""
 pass


class HMSAPIIntegrator:
 """Production HMS API Integration Service"""

 def __init__(self, config: ConfigManager):
 self.config = config
 self.logger = logging.getLogger(__name__)
 self.encryption_key = self._get_encryption_key()
 self.session_cache: Dict[str, ClientSession] = {}
 self.rate_limits: Dict[str, datetime] = {}

 def _get_encryption_key(self) -> bytes:
 """Get encryption key for sensitive data"""
 key = self.config.get("security.encryption_key")
 if not key:
 # Generate new key if not exists
 key = Fernet.generate_key()
 self.logger.warning("Generated new encryption key - store this securely!")
 return key if isinstance(key, bytes) else key.encode()

 def encrypt_credentials(self, credentials: str) -> str:
 """Encrypt sensitive credential data"""
 f = Fernet(self.encryption_key)
 return f.encrypt(credentials.encode()).decode()

 def decrypt_credentials(self, encrypted_data: str) -> str:
 """Decrypt credential data"""
 f = Fernet(self.encryption_key)
 return f.decrypt(encrypted_data.encode()).decode()

 async def register_hospital_hms(self, hospital_id: str, hms_type: HMSType, 
 credentials: HMSCredentials) -> Dict[str, Any]:
 """Register a hospital's HMS system for data collection"""

 try:
 # Test connection first
 test_result = await self._test_hms_connection(hms_type, credentials)
 if not test_result["success"]:
 raise HMSAPIIntegrationError(f"HMS connection test failed: {test_result['error']}")

 # Store encrypted credentials
 encrypted_creds = {
 "api_key": self.encrypt_credentials(credentials.api_key),
 "api_secret": self.encrypt_credentials(credentials.api_secret),
 "base_url": credentials.base_url,
 "auth_type": credentials.auth_type,
 "additional_headers": credentials.additional_headers,
 "tenant_id": credentials.tenant_id
 }

 # Store in configuration
 hms_config_key = f"hospitals.{hospital_id}.hms_config"
 self.config.set(hms_config_key, {
 "hms_type": hms_type.value,
 "credentials": encrypted_creds,
 "data_mapping": self._get_data_mapping(hms_type).to_dict(),
 "last_sync": None,
 "sync_frequency": "daily",
 "active": True
 })

 self.logger.info(f"Successfully registered HMS {hms_type.value} for hospital {hospital_id}")

 return {
 "success": True,
 "hospital_id": hospital_id,
 "hms_type": hms_type.value,
 "test_result": test_result,
 "message": "HMS system registered successfully"
 }

 except Exception as e:
 self.logger.error(f"Failed to register HMS for hospital {hospital_id}: {str(e)}")
 raise HMSAPIIntegrationError(f"HMS registration failed: {str(e)}")

 async def collect_hospital_data(self, hospital_id: str) -> Dict[str, Any]:
 """Collect real-time data from hospital's HMS system"""

 try:
 # Get HMS configuration
 hms_config = self._get_hospital_hms_config(hospital_id)
 if not hms_config:
 raise HMSAPIIntegrationError(f"No HMS configuration found for hospital {hospital_id}")

 hms_type = HMSType(hms_config["hms_type"])
 credentials = self._decrypt_credentials(hms_config["credentials"])
 data_mapping = HMSDataMapping.from_dict(hms_config["data_mapping"])

 # Rate limiting check
 if not self._check_rate_limit(hospital_id):
 return {
 "success": False,
 "error": "Rate limit exceeded",
 "retry_after": 300
 }

 # Collect data based on HMS type
 if hms_type == HMSType.MEDTECH:
 raw_data = await self._collect_medtech_data(credentials)
 elif hms_type == HMSType.BIRLAMEDISOFT:
 raw_data = await self._collect_birlamedisoft_data(credentials)
 elif hms_type == HMSType.HMIS_PLUS:
 raw_data = await self._collect_hmis_plus_data(credentials)
 else:
 raw_data = await self._collect_generic_hms_data(hms_type, credentials)

 # Transform to standard format
 standardized_data = await self._transform_hms_data(raw_data, data_mapping)

 # Validate data quality
 quality_score = await self._validate_data_quality(standardized_data)

 # Update sync timestamp
 self._update_last_sync(hospital_id)

 return {
 "success": True,
 "hospital_id": hospital_id,
 "hms_type": hms_type.value,
 "data_collected": standardized_data,
 "quality_score": quality_score,
 "collection_timestamp": datetime.utcnow().isoformat(),
 "data_source": "hms_api_real"
 }

 except Exception as e:
 self.logger.error(f"Failed to collect HMS data for hospital {hospital_id}: {str(e)}")
 return {
 "success": False,
 "error": str(e),
 "hospital_id": hospital_id,
 "collection_timestamp": datetime.utcnow().isoformat()
 }

 async def _collect_medtech_data(self, credentials: HMSCredentials) -> Dict[str, Any]:
 """Collect data from MedTech HMS API"""

 session = await self._get_authenticated_session(HMSType.MEDTECH, credentials)

 try:
 # MedTech API endpoints
 endpoints = {
 "occupancy": "/api/v1/reports/occupancy/current",
 "finance": "/api/v1/reports/finance/monthly", 
 "patients": "/api/v1/reports/patients/summary",
 "operations": "/api/v1/reports/operations/monthly",
 "emergency": "/api/v1/reports/emergency/stats",
 "quality": "/api/v1/reports/quality/indicators",
 "staffing": "/api/v1/reports/staffing/current",
 "schemes": "/api/v1/reports/schemes/monthly"
 }

 raw_data = {}

 # Collect data from each endpoint
 for category, endpoint in endpoints.items():
 try:
 url = f"{credentials.base_url}{endpoint}"

 # Add query parameters for date range
 params = {
 "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
 "end_date": datetime.now().strftime("%Y-%m-%d"),
 "format": "json"
 }

 async with session.get(url, params=params) as response:
 if response.status == 200:
 data = await response.json()
 raw_data[category] = data
 self.logger.info(f"Successfully collected {category} data from MedTech")
 else:
 self.logger.warning(f"Failed to collect {category} data: {response.status}")
 raw_data[category] = {}

 except Exception as e:
 self.logger.error(f"Error collecting {category} data: {str(e)}")
 raw_data[category] = {}

 return raw_data

 finally:
 await session.close()

 async def _collect_birlamedisoft_data(self, credentials: HMSCredentials) -> Dict[str, Any]:
 """Collect data from Birlamedisoft HMS API"""

 session = await self._get_authenticated_session(HMSType.BIRLAMEDISOFT, credentials)

 try:
 # Birlamedisoft uses different API structure
 base_endpoint = "/RestAPI/api/Reports"

 # Authentication for Birlamedisoft
 auth_payload = {
 "username": credentials.username,
 "password": credentials.password,
 "database": credentials.tenant_id
 }

 # Get authentication token
 async with session.post(f"{credentials.base_url}/RestAPI/api/Auth/Login", 
 json=auth_payload) as auth_response:
 if auth_response.status != 200:
 raise HMSAPIIntegrationError("Birlamedisoft authentication failed")

 auth_data = await auth_response.json()
 token = auth_data.get("token")

 if not token:
 raise HMSAPIIntegrationError("No token received from Birlamedisoft")

 # Set authorization header
 session.headers.update({"Authorization": f"Bearer {token}"})

 # Birlamedisoft report types
 reports = {
 "census": "IPDCensusReport",
 "finance": "RevenueReport", 
 "operations": "OperationTheaterReport",
 "outpatient": "OPDReport",
 "emergency": "EmergencyReport",
 "schemes": "GovernmentSchemeReport"
 }

 raw_data = {}
 current_date = datetime.now()

 for category, report_type in reports.items():
 try:
 report_params = {
 "reportType": report_type,
 "fromDate": (current_date - timedelta(days=30)).strftime("%d/%m/%Y"),
 "toDate": current_date.strftime("%d/%m/%Y"),
 "format": "JSON"
 }

 async with session.post(f"{credentials.base_url}{base_endpoint}/GenerateReport",
 json=report_params) as response:
 if response.status == 200:
 data = await response.json()
 raw_data[category] = data
 self.logger.info(f"Successfully collected {category} data from Birlamedisoft")
 else:
 self.logger.warning(f"Failed to collect {category} data: {response.status}")
 raw_data[category] = {}

 except Exception as e:
 self.logger.error(f"Error collecting {category} data from Birlamedisoft: {str(e)}")
 raw_data[category] = {}

 return raw_data

 finally:
 await session.close()

 async def _collect_hmis_plus_data(self, credentials: HMSCredentials) -> Dict[str, Any]:
 """Collect data from HMIS Plus (Government HMS) API"""

 session = await self._get_authenticated_session(HMSType.HMIS_PLUS, credentials)

 try:
 # HMIS Plus uses SOAP-based API
 soap_endpoints = {
 "facility_data": "/HMISPlusWebService/FacilityService.asmx",
 "performance_data": "/HMISPlusWebService/PerformanceService.asmx",
 "financial_data": "/HMISPlusWebService/FinancialService.asmx"
 }

 raw_data = {}

 # SOAP request template
 soap_template = """<?xml version="1.0" encoding="utf-8"?>
 <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
 xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
 <soap:Header>
 <AuthHeader xmlns="http://hmisplus.gov.in/">
 <Username>{username}</Username>
 <Password>{password}</Password>
 <FacilityCode>{facility_code}</FacilityCode>
 </AuthHeader>
 </soap:Header>
 <soap:Body>
 <{method_name} xmlns="http://hmisplus.gov.in/">
 <fromDate>{from_date}</fromDate>
 <toDate>{to_date}</toDate>
 </{method_name}>
 </soap:Body>
 </soap:Envelope>"""

 # Collect facility performance data
 for category, endpoint in soap_endpoints.items():
 try:
 method_name = "GetFacilityPerformanceData"

 soap_body = soap_template.format(
 username=credentials.username,
 password=credentials.password,
 facility_code=credentials.tenant_id,
 method_name=method_name,
 from_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
 to_date=datetime.now().strftime("%Y-%m-%d")
 )

 headers = {
 "Content-Type": "text/xml; charset=utf-8",
 "SOAPAction": f"http://hmisplus.gov.in/{method_name}"
 }

 async with session.post(f"{credentials.base_url}{endpoint}",
 data=soap_body, headers=headers) as response:
 if response.status == 200:
 xml_content = await response.text()
 # Parse SOAP XML response
 root = ET.fromstring(xml_content)

 # Extract data from SOAP response
 data = self._parse_hmis_soap_response(root)
 raw_data[category] = data
 self.logger.info(f"Successfully collected {category} data from HMIS Plus")
 else:
 self.logger.warning(f"Failed to collect {category} data: {response.status}")
 raw_data[category] = {}

 except Exception as e:
 self.logger.error(f"Error collecting {category} data from HMIS Plus: {str(e)}")
 raw_data[category] = {}

 return raw_data

 finally:
 await session.close()

 async def _collect_generic_hms_data(self, hms_type: HMSType, 
 credentials: HMSCredentials) -> Dict[str, Any]:
 """Generic HMS data collection for custom APIs"""

 session = await self._get_authenticated_session(hms_type, credentials)

 try:
 # Generic REST API approach
 common_endpoints = [
 "/api/reports/occupancy",
 "/api/reports/finance", 
 "/api/reports/patients",
 "/api/reports/operations",
 "/api/reports/emergency",
 "/api/reports/quality"
 ]

 raw_data = {}

 for endpoint in common_endpoints:
 try:
 url = f"{credentials.base_url}{endpoint}"

 # Common query parameters
 params = {
 "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
 "end_date": datetime.now().strftime("%Y-%m-%d")
 }

 async with session.get(url, params=params) as response:
 if response.status == 200:
 content_type = response.headers.get('Content-Type', '')

 if 'application/json' in content_type:
 data = await response.json()
 elif 'application/xml' in content_type or 'text/xml' in content_type:
 xml_content = await response.text()
 data = self._parse_xml_to_dict(xml_content)
 else:
 # Assume JSON if not specified
 data = await response.json()

 category = endpoint.split('/')[-1]
 raw_data[category] = data
 self.logger.info(f"Successfully collected {category} data from {hms_type.value}")
 else:
 self.logger.warning(f"Failed to collect data from {endpoint}: {response.status}")

 except Exception as e:
 self.logger.error(f"Error collecting data from {endpoint}: {str(e)}")

 return raw_data

 finally:
 await session.close()

 async def _get_authenticated_session(self, hms_type: HMSType, 
 credentials: HMSCredentials) -> ClientSession:
 """Get authenticated HTTP session for HMS API"""

 timeout = ClientTimeout(total=30, connect=10)

 # Base headers
 headers = {
 "User-Agent": "VerticalLight-HMS-Integrator/1.0",
 "Accept": "application/json",
 "Content-Type": "application/json"
 }

 # Add custom headers
 headers.update(credentials.additional_headers)

 # Authentication based on type
 auth = None

 if credentials.auth_type == "api_key":
 headers["X-API-Key"] = credentials.api_key
 if credentials.api_secret:
 headers["X-API-Secret"] = credentials.api_secret
 elif credentials.auth_type == "basic_auth":
 auth = BasicAuth(credentials.username or credentials.api_key, 
 credentials.password or credentials.api_secret)
 elif credentials.auth_type == "oauth":
 # OAuth token would be handled separately
 pass

 session = ClientSession(
 headers=headers,
 auth=auth,
 timeout=timeout,
 connector=aiohttp.TCPConnector(limit=10)
 )

 return session

 async def _test_hms_connection(self, hms_type: HMSType, 
 credentials: HMSCredentials) -> Dict[str, Any]:
 """Test HMS API connection and authentication"""

 try:
 session = await self._get_authenticated_session(hms_type, credentials)

 # Common test endpoints
 test_endpoints = [
 "/api/health",
 "/api/status", 
 "/api/ping",
 "/health",
 "/status"
 ]

 for endpoint in test_endpoints:
 try:
 url = f"{credentials.base_url}{endpoint}"

 async with session.get(url) as response:
 if response.status == 200:
 return {
 "success": True,
 "message": "HMS connection successful",
 "endpoint_tested": endpoint,
 "response_time_ms": response.headers.get("X-Response-Time", "N/A")
 }
 elif response.status == 401:
 return {
 "success": False,
 "error": "Authentication failed",
 "status_code": 401
 }
 elif response.status == 403:
 return {
 "success": False,
 "error": "Access forbidden - check permissions",
 "status_code": 403
 }

 except Exception as e:
 continue # Try next endpoint

 # If no standard endpoint works, try a basic connection
 try:
 async with session.get(credentials.base_url) as response:
 return {
 "success": True,
 "message": "Basic connection successful",
 "status_code": response.status,
 "note": "Standard health endpoints not available"
 }
 except Exception as e:
 return {
 "success": False,
 "error": f"Connection failed: {str(e)}"
 }

 except Exception as e:
 return {
 "success": False,
 "error": f"HMS connection test failed: {str(e)}"
 }
 finally:
 if 'session' in locals():
 await session.close()

 def _get_hospital_hms_config(self, hospital_id: str) -> Optional[Dict[str, Any]]:
 """Get HMS configuration for a hospital"""
 config_key = f"hospitals.{hospital_id}.hms_config"
 return self.config.get(config_key)

 def _decrypt_credentials(self, encrypted_creds: Dict[str, Any]) -> HMSCredentials:
 """Decrypt stored credentials"""
 return HMSCredentials(
 api_key=self.decrypt_credentials(encrypted_creds["api_key"]),
 api_secret=self.decrypt_credentials(encrypted_creds["api_secret"]),
 username=encrypted_creds.get("username"),
 password=encrypted_creds.get("password"), 
 base_url=encrypted_creds["base_url"],
 auth_type=encrypted_creds["auth_type"],
 additional_headers=encrypted_creds.get("additional_headers", {}),
 tenant_id=encrypted_creds.get("tenant_id")
 )

 def _get_data_mapping(self, hms_type: HMSType) -> HMSDataMapping:
 """Get data field mapping for HMS type"""
 if hms_type == HMSType.MEDTECH:
 return HMSDataMapping.get_medtech_mapping()
 else:
 # Return default mapping for other HMS types
 return HMSDataMapping.get_medtech_mapping() # Use as default

 async def _transform_hms_data(self, raw_data: Dict[str, Any], 
 mapping: HMSDataMapping) -> Dict[str, Any]:
 """Transform raw HMS data to standard format"""

 standardized = {
 "performance_metrics": {},
 "financial_metrics": {},
 "patient_data": {},
 "staff_metrics": {},
 "government_schemes": {}
 }

 try:
 # Transform performance metrics
 for std_field, hms_path in mapping.performance_metrics.items():
 value = self._extract_nested_value(raw_data, hms_path)
 if value is not None:
 standardized["performance_metrics"][std_field] = self._convert_data_type(value)

 # Transform financial metrics
 for std_field, hms_path in mapping.financial_metrics.items():
 value = self._extract_nested_value(raw_data, hms_path)
 if value is not None:
 standardized["financial_metrics"][std_field] = self._convert_data_type(value)

 # Transform patient data
 for std_field, hms_path in mapping.patient_data.items():
 value = self._extract_nested_value(raw_data, hms_path)
 if value is not None:
 standardized["patient_data"][std_field] = self._convert_data_type(value)

 # Transform staff metrics
 for std_field, hms_path in mapping.staff_metrics.items():
 value = self._extract_nested_value(raw_data, hms_path)
 if value is not None:
 standardized["staff_metrics"][std_field] = self._convert_data_type(value)

 # Transform government scheme data
 for std_field, hms_path in mapping.government_schemes.items():
 value = self._extract_nested_value(raw_data, hms_path)
 if value is not None:
 standardized["government_schemes"][std_field] = self._convert_data_type(value)

 return standardized

 except Exception as e:
 self.logger.error(f"Error transforming HMS data: {str(e)}")
 raise HMSAPIIntegrationError(f"Data transformation failed: {str(e)}")

 def _extract_nested_value(self, data: Dict[str, Any], path: str) -> Any:
 """Extract value from nested dictionary using dot notation path"""
 try:
 keys = path.split('.')
 current = data

 for key in keys:
 if isinstance(current, dict) and key in current:
 current = current[key]
 elif isinstance(current, list) and key.isdigit():
 current = current[int(key)]
 else:
 return None

 return current

 except (KeyError, IndexError, TypeError):
 return None

 def _convert_data_type(self, value: Any) -> Union[Decimal, int, float, str]:
 """Convert data to appropriate type"""
 if value is None:
 return None

 # Convert to Decimal for financial data
 if isinstance(value, (int, float)):
 return Decimal(str(value))

 # Try to convert string numbers
 if isinstance(value, str):
 try:
 if '.' in value:
 return Decimal(value)
 else:
 return int(value) if value.isdigit() else value
 except (ValueError, TypeError):
 return value

 return value

 async def _validate_data_quality(self, data: Dict[str, Any]) -> int:
 """Validate data quality and return score 1-10"""

 total_fields = 0
 populated_fields = 0
 quality_issues = []

 for category, fields in data.items():
 if isinstance(fields, dict):
 for field, value in fields.items():
 total_fields += 1

 if value is not None and value != "":
 populated_fields += 1

 # Check for realistic ranges
 if field == "bed_occupancy_rate" and isinstance(value, (int, float, Decimal)):
 if not (0 <= float(value) <= 100):
 quality_issues.append(f"Bed occupancy rate out of range: {value}")

 elif field == "patient_satisfaction_score" and isinstance(value, (int, float, Decimal)):
 if not (0 <= float(value) <= 10):
 quality_issues.append(f"Patient satisfaction score out of range: {value}")

 # Calculate completeness score
 completeness_score = (populated_fields / total_fields * 100) if total_fields > 0 else 0

 # Deduct points for quality issues
 quality_deduction = len(quality_issues) * 5

 # Final score calculation
 final_score = max(1, min(10, int((completeness_score - quality_deduction) / 10)))

 if quality_issues:
 self.logger.warning(f"Data quality issues found: {quality_issues}")

 return final_score

 def _check_rate_limit(self, hospital_id: str) -> bool:
 """Check if rate limit allows API call"""
 last_call = self.rate_limits.get(hospital_id)
 if last_call and (datetime.now() - last_call).seconds < 300: # 5 min limit
 return False

 self.rate_limits[hospital_id] = datetime.now()
 return True

 def _update_last_sync(self, hospital_id: str) -> None:
 """Update last sync timestamp for hospital"""
 config_key = f"hospitals.{hospital_id}.hms_config.last_sync"
 self.config.set(config_key, datetime.utcnow().isoformat())

 def _parse_hmis_soap_response(self, xml_root) -> Dict[str, Any]:
 """Parse HMIS Plus SOAP XML response to dictionary"""
 try:
 # Find the response data in SOAP envelope
 namespaces = {
 'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
 'hmis': 'http://hmisplus.gov.in/'
 }

 # Extract data from SOAP body
 body = xml_root.find('soap:Body', namespaces)
 if body is not None:
 response = body.find('hmis:GetFacilityPerformanceDataResponse', namespaces)
 if response is not None:
 result = response.find('hmis:GetFacilityPerformanceDataResult', namespaces)
 if result is not None:
 return self._xml_element_to_dict(result)

 return {}

 except Exception as e:
 self.logger.error(f"Error parsing HMIS SOAP response: {str(e)}")
 return {}

 def _parse_xml_to_dict(self, xml_string: str) -> Dict[str, Any]:
 """Parse XML string to dictionary"""
 try:
 root = ET.fromstring(xml_string)
 return self._xml_element_to_dict(root)
 except Exception as e:
 self.logger.error(f"Error parsing XML: {str(e)}")
 return {}

 def _xml_element_to_dict(self, element) -> Dict[str, Any]:
 """Convert XML element to dictionary"""
 result = {}

 # Add element text
 if element.text and element.text.strip():
 if len(element) == 0:
 return element.text.strip()

 # Add attributes
 for key, value in element.attrib.items():
 result[f"@{key}"] = value

 # Add child elements
 for child in element:
 child_data = self._xml_element_to_dict(child)

 if child.tag in result:
 # Multiple elements with same tag
 if not isinstance(result[child.tag], list):
 result[child.tag] = [result[child.tag]]
 result[child.tag].append(child_data)
 else:
 result[child.tag] = child_data

 return result


# Data mapping extensions for different HMS types
class HMSDataMapping:
 """Extended with class methods for different HMS types"""

 def to_dict(self) -> Dict[str, Any]:
 """Convert to dictionary for storage"""
 return {
 "performance_metrics": self.performance_metrics,
 "financial_metrics": self.financial_metrics,
 "patient_data": self.patient_data,
 "staff_metrics": self.staff_metrics,
 "government_schemes": self.government_schemes
 }

 @classmethod
 def from_dict(cls, data: Dict[str, Any]) -> 'HMSDataMapping':
 """Create from dictionary"""
 return cls(
 performance_metrics=data.get("performance_metrics", {}),
 financial_metrics=data.get("financial_metrics", {}),
 patient_data=data.get("patient_data", {}),
 staff_metrics=data.get("staff_metrics", {}),
 government_schemes=data.get("government_schemes", {})
 )

 @classmethod
 def get_birlamedisoft_mapping(cls) -> 'HMSDataMapping':
 """Mapping for Birlamedisoft HMS"""
 return cls(
 performance_metrics={
 "bed_occupancy_rate": "census.occupancy_percentage",
 "average_length_of_stay": "ipd.average_los",
 "patient_satisfaction_score": "quality.patient_satisfaction",
 "or_utilization_rate": "ot.utilization_percentage",
 "ed_average_wait_time": "emergency.average_wait_time"
 },
 financial_metrics={
 "total_revenue": "revenue.total_monthly",
 "total_costs": "expenses.total_monthly",
 "accounts_receivable_days": "finance.ar_days",
 "cash_percentage": "payments.cash_percentage"
 },
 patient_data={
 "total_admissions": "ipd.total_admissions",
 "outpatient_visits": "opd.total_visits",
 "surgery_cases": "ot.total_procedures"
 },
 staff_metrics={
 "total_doctors": "staff.doctors",
 "total_nurses": "staff.nurses",
 "staff_turnover_rate": "hr.turnover_rate"
 },
 government_schemes={
 "ayushman_bharat_cases": "schemes.ayushman_cases",
 "cghs_cases": "schemes.cghs_cases",
 "total_scheme_revenue": "schemes.total_revenue"
 }
 )