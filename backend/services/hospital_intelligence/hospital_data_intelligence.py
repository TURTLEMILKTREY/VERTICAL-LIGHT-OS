"""
Hospital Data Intelligence Layer - Core Implementation
Real-time data ingestion system for Indian hospitals
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Configuration imports
from config.config_manager import get_config_manager

# Hospital schema imports
from models.hospital_schemas_simple import HospitalProfile

# HMS connector imports
from services.hospital_intelligence.hms_connectors import HMSConnectorFactory, HMSType

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
 """Types of hospital data sources"""
 HMS = "hospital_management_system"
 FINANCIAL = "financial_system" 
 PATIENT_FLOW = "patient_flow_system"
 STAFF = "staff_management_system"
 EQUIPMENT = "equipment_monitoring_system"
 GOVERNMENT = "government_reporting_system"

@dataclass
class DataIngestionConfig:
 """Configuration for data ingestion from hospital systems"""
 hospital_id: str
 source_type: DataSourceType
 connection_config: Dict[str, Any]
 sync_frequency: int = 300 # seconds
 data_retention_days: int = 365
 quality_threshold: float = 0.95
 real_time_enabled: bool = True

@dataclass
class DataQualityReport:
 """Data quality assessment report"""
 source_id: str
 timestamp: datetime
 completeness_score: float
 accuracy_score: float
 consistency_score: float
 timeliness_score: float
 overall_score: float
 issues: List[str] = field(default_factory=list)

class HospitalDataIntelligence:
 """
 Core hospital data intelligence system for real-time data collection
 and analysis from multiple hospital systems in India
 """

 def __init__(self):
 self.config_manager = get_config_manager()
 self.active_connections: Dict[str, Any] = {}
 self.data_streams: Dict[str, asyncio.Queue] = {}
 self.quality_scores: Dict[str, DataQualityReport] = {}

 # Load hospital-specific configuration
 self.hospital_config = self.config_manager.get('hospital_consulting_config', {})

 # Initialize data connectors
 self.hms_connector = HMSIntegrationManager()
 self.financial_connector = FinancialSystemConnector()
 self.patient_flow_tracker = PatientFlowTracker()
 self.staff_tracker = StaffProductivityTracker()
 self.equipment_monitor = EquipmentUtilizationMonitor()

 async def initialize_hospital_data_collection(self, hospital_profile: HospitalProfile) -> Dict[str, Any]:
 """
 Initialize comprehensive data collection for a hospital
 """
 try:
 hospital_id = hospital_profile.hospital_id

 # Create data ingestion configurations
 ingestion_configs = await self._create_ingestion_configs(hospital_profile)

 # Initialize all data connectors
 connection_results = {}

 for config in ingestion_configs:
 try:
 connector = self._get_connector(config.source_type)
 connection = await connector.establish_connection(config)

 if connection.get('status') == 'success':
 self.active_connections[f"{hospital_id}_{config.source_type.value}"] = connection

 # Start real-time data streaming if enabled
 if config.real_time_enabled:
 await self._start_real_time_stream(hospital_id, config)

 connection_results[config.source_type.value] = {
 'status': 'connected',
 'last_sync': datetime.now().isoformat(),
 'config': config.__dict__
 }
 else:
 connection_results[config.source_type.value] = {
 'status': 'failed',
 'error': connection.get('error', 'Unknown error')
 }

 except Exception as e:
 logger.error(f"Failed to connect {config.source_type.value} for hospital {hospital_id}: {str(e)}")
 connection_results[config.source_type.value] = {
 'status': 'error',
 'error': str(e)
 }

 return {
 'hospital_id': hospital_id,
 'initialization_status': 'completed',
 'connections': connection_results,
 'timestamp': datetime.now().isoformat()
 }

 except Exception as e:
 logger.error(f"Failed to initialize data collection for hospital {hospital_profile.hospital_id}: {str(e)}")
 raise

 async def collect_real_time_hospital_data(self, hospital_id: str) -> Dict[str, Any]:
 """
 Collect real-time data from all connected hospital systems
 """
 try:
 current_data = {
 'hospital_id': hospital_id,
 'collection_timestamp': datetime.now().isoformat(),
 'data_sources': {}
 }

 # Collect HMS data
 hms_data = await self.hms_connector.get_current_data(hospital_id)
 if hms_data:
 current_data['data_sources']['hms'] = hms_data

 # Collect financial data
 financial_data = await self.financial_connector.get_current_financial_snapshot(hospital_id)
 if financial_data:
 current_data['data_sources']['financial'] = financial_data

 # Collect patient flow data
 patient_flow_data = await self.patient_flow_tracker.get_current_flow_status(hospital_id)
 if patient_flow_data:
 current_data['data_sources']['patient_flow'] = patient_flow_data

 # Collect staff data
 staff_data = await self.staff_tracker.get_current_staff_status(hospital_id)
 if staff_data:
 current_data['data_sources']['staff'] = staff_data

 # Collect equipment data
 equipment_data = await self.equipment_monitor.get_current_equipment_status(hospital_id)
 if equipment_data:
 current_data['data_sources']['equipment'] = equipment_data

 # Assess data quality
 quality_report = await self._assess_data_quality(hospital_id, current_data)
 current_data['data_quality'] = quality_report.__dict__

 return current_data

 except Exception as e:
 logger.error(f"Failed to collect real-time data for hospital {hospital_id}: {str(e)}")
 raise

 async def get_hospital_data_summary(self, hospital_id: str, timeframe: str = "24h") -> Dict[str, Any]:
 """
 Get comprehensive data summary for specified timeframe
 """
 try:
 # Parse timeframe
 hours = self._parse_timeframe(timeframe)
 start_time = datetime.now() - timedelta(hours=hours)

 summary = {
 'hospital_id': hospital_id,
 'timeframe': timeframe,
 'summary_generated': datetime.now().isoformat(),
 'metrics': {}
 }

 # Financial metrics summary
 financial_summary = await self.financial_connector.get_financial_summary(
 hospital_id, start_time, datetime.now()
 )
 summary['metrics']['financial'] = financial_summary

 # Patient flow summary
 flow_summary = await self.patient_flow_tracker.get_flow_summary(
 hospital_id, start_time, datetime.now()
 )
 summary['metrics']['patient_flow'] = flow_summary

 # Staff productivity summary
 staff_summary = await self.staff_tracker.get_productivity_summary(
 hospital_id, start_time, datetime.now()
 )
 summary['metrics']['staff_productivity'] = staff_summary

 # Equipment utilization summary
 equipment_summary = await self.equipment_monitor.get_utilization_summary(
 hospital_id, start_time, datetime.now()
 )
 summary['metrics']['equipment_utilization'] = equipment_summary

 # Calculate overall performance indicators
 performance_indicators = await self._calculate_performance_indicators(summary['metrics'])
 summary['performance_indicators'] = performance_indicators

 return summary

 except Exception as e:
 logger.error(f"Failed to generate data summary for hospital {hospital_id}: {str(e)}")
 raise

 async def _create_ingestion_configs(self, hospital_profile: HospitalProfile) -> List[DataIngestionConfig]:
 """Create data ingestion configurations based on hospital profile"""
 configs = []

 # HMS configuration
 if hospital_profile.systems_integration.get('hms_system'):
 hms_config = DataIngestionConfig(
 hospital_id=hospital_profile.hospital_id,
 source_type=DataSourceType.HMS,
 connection_config={
 'system_type': hospital_profile.systems_integration['hms_system'],
 'api_endpoint': hospital_profile.systems_integration.get('hms_api_endpoint'),
 'credentials': hospital_profile.systems_integration.get('hms_credentials', {}),
 'data_elements': ['patients', 'admissions', 'procedures', 'outcomes']
 },
 sync_frequency=300, # 5 minutes
 real_time_enabled=True
 )
 configs.append(hms_config)

 # Financial system configuration
 if hospital_profile.systems_integration.get('financial_system'):
 financial_config = DataIngestionConfig(
 hospital_id=hospital_profile.hospital_id,
 source_type=DataSourceType.FINANCIAL,
 connection_config={
 'system_type': hospital_profile.systems_integration['financial_system'],
 'api_endpoint': hospital_profile.systems_integration.get('financial_api_endpoint'),
 'credentials': hospital_profile.systems_integration.get('financial_credentials', {}),
 'data_elements': ['revenue', 'costs', 'receivables', 'payer_mix']
 },
 sync_frequency=600, # 10 minutes
 real_time_enabled=False # Financial data typically not real-time
 )
 configs.append(financial_config)

 # Add other system configurations as needed

 return configs

 def _get_connector(self, source_type: DataSourceType):
 """Get appropriate connector for data source type"""
 connector_map = {
 DataSourceType.HMS: self.hms_connector,
 DataSourceType.FINANCIAL: self.financial_connector,
 DataSourceType.PATIENT_FLOW: self.patient_flow_tracker,
 DataSourceType.STAFF: self.staff_tracker,
 DataSourceType.EQUIPMENT: self.equipment_monitor
 }
 return connector_map.get(source_type)

 async def _start_real_time_stream(self, hospital_id: str, config: DataIngestionConfig):
 """Start real-time data streaming for a hospital system"""
 stream_id = f"{hospital_id}_{config.source_type.value}"
 self.data_streams[stream_id] = asyncio.Queue()

 # Start background task for data streaming
 asyncio.create_task(self._stream_data(stream_id, config))

 async def _stream_data(self, stream_id: str, config: DataIngestionConfig):
 """Background task for continuous data streaming"""
 connector = self._get_connector(config.source_type)

 while True:
 try:
 # Get real-time data from connector
 data = await connector.get_real_time_data(config)

 if data:
 # Add to stream queue
 await self.data_streams[stream_id].put({
 'timestamp': datetime.now().isoformat(),
 'source': config.source_type.value,
 'data': data
 })

 # Wait for next sync interval
 await asyncio.sleep(config.sync_frequency)

 except Exception as e:
 logger.error(f"Error in data streaming for {stream_id}: {str(e)}")
 await asyncio.sleep(60) # Wait a minute before retrying

 async def _assess_data_quality(self, hospital_id: str, data: Dict[str, Any]) -> DataQualityReport:
 """Assess quality of collected data"""

 # Initialize quality scores
 completeness_scores = []
 accuracy_scores = []
 consistency_scores = []
 timeliness_scores = []
 issues = []

 # Assess each data source
 for source_name, source_data in data.get('data_sources', {}).items():
 if not source_data:
 issues.append(f"No data available from {source_name}")
 completeness_scores.append(0.0)
 continue

 # Completeness check
 completeness = self._check_data_completeness(source_data)
 completeness_scores.append(completeness)

 # Accuracy check (basic validation)
 accuracy = self._check_data_accuracy(source_data)
 accuracy_scores.append(accuracy)

 # Consistency check
 consistency = self._check_data_consistency(source_data)
 consistency_scores.append(consistency)

 # Timeliness check
 timeliness = self._check_data_timeliness(source_data)
 timeliness_scores.append(timeliness)

 if completeness < 0.8:
 issues.append(f"Low data completeness in {source_name}: {completeness:.2f}")
 if accuracy < 0.9:
 issues.append(f"Data accuracy issues in {source_name}: {accuracy:.2f}")

 # Calculate overall scores
 overall_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
 overall_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
 overall_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
 overall_timeliness = sum(timeliness_scores) / len(timeliness_scores) if timeliness_scores else 0.0

 overall_score = (overall_completeness + overall_accuracy + overall_consistency + overall_timeliness) / 4

 return DataQualityReport(
 source_id=hospital_id,
 timestamp=datetime.now(),
 completeness_score=overall_completeness,
 accuracy_score=overall_accuracy,
 consistency_score=overall_consistency,
 timeliness_score=overall_timeliness,
 overall_score=overall_score,
 issues=issues
 )

 def _check_data_completeness(self, data: Dict[str, Any]) -> float:
 """Check completeness of data fields"""
 if not data:
 return 0.0

 total_fields = len(data)
 complete_fields = sum(1 for value in data.values() if value is not None and value != "")

 return complete_fields / total_fields if total_fields > 0 else 0.0

 def _check_data_accuracy(self, data: Dict[str, Any]) -> float:
 """Basic accuracy validation"""
 # This would include business rule validation
 # For now, simple checks
 accuracy_score = 1.0

 # Check for reasonable numeric ranges
 for key, value in data.items():
 if isinstance(value, (int, float)):
 if value < 0 and key not in ['cost_variance', 'profit_margin']:
 accuracy_score -= 0.1 # Negative values where they shouldn't be

 return max(0.0, accuracy_score)

 def _check_data_consistency(self, data: Dict[str, Any]) -> float:
 """Check internal consistency of data"""
 # Basic consistency checks
 return 1.0 # Placeholder for now

 def _check_data_timeliness(self, data: Dict[str, Any]) -> float:
 """Check if data is recent enough"""
 timestamp_field = data.get('timestamp')
 if not timestamp_field:
 return 0.5 # No timestamp available

 try:
 data_time = datetime.fromisoformat(timestamp_field.replace('Z', '+00:00'))
 time_diff = datetime.now() - data_time.replace(tzinfo=None)

 # Data is considered fresh if within 1 hour
 if time_diff.total_seconds() <= 3600:
 return 1.0
 elif time_diff.total_seconds() <= 86400: # Within 24 hours
 return 0.8
 else:
 return 0.3
 except:
 return 0.5

 def _parse_timeframe(self, timeframe: str) -> int:
 """Parse timeframe string to hours"""
 timeframe_map = {
 "1h": 1, "6h": 6, "12h": 12, "24h": 24,
 "1d": 24, "3d": 72, "7d": 168, "30d": 720
 }
 return timeframe_map.get(timeframe, 24)

 async def _calculate_performance_indicators(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
 """Calculate overall performance indicators"""
 indicators = {}

 # Financial indicators
 financial = metrics.get('financial', {})
 if financial:
 indicators['revenue_per_bed'] = financial.get('total_revenue', 0) / max(financial.get('occupied_beds', 1), 1)
 indicators['cost_per_patient'] = financial.get('total_costs', 0) / max(financial.get('patient_count', 1), 1)
 indicators['profit_margin'] = financial.get('profit_margin', 0)

 # Operational indicators
 patient_flow = metrics.get('patient_flow', {})
 if patient_flow:
 indicators['bed_occupancy_rate'] = patient_flow.get('bed_occupancy_rate', 0)
 indicators['average_los'] = patient_flow.get('average_length_of_stay', 0)
 indicators['patient_throughput'] = patient_flow.get('daily_admissions', 0)

 # Efficiency indicators
 staff_productivity = metrics.get('staff_productivity', {})
 if staff_productivity:
 indicators['patients_per_nurse'] = staff_productivity.get('patients_per_nurse', 0)
 indicators['overtime_percentage'] = staff_productivity.get('overtime_percentage', 0)

 # Equipment utilization
 equipment = metrics.get('equipment_utilization', {})
 if equipment:
 indicators['or_utilization'] = equipment.get('operating_room_utilization', 0)
 indicators['equipment_downtime'] = equipment.get('average_downtime_percentage', 0)

 return indicators


# Placeholder connector classes to be implemented
class HMSIntegrationManager:
 async def establish_connection(self, config: DataIngestionConfig):
 return {'status': 'success', 'connection_id': str(uuid.uuid4())}

 async def get_current_data(self, hospital_id: str):
 return {'patients': 150, 'admissions_today': 25, 'timestamp': datetime.now().isoformat()}

 async def get_real_time_data(self, config: DataIngestionConfig):
 return {'live_data': True, 'timestamp': datetime.now().isoformat()}

class FinancialSystemConnector:
 async def establish_connection(self, config: DataIngestionConfig):
 return {'status': 'success', 'connection_id': str(uuid.uuid4())}

 async def get_current_financial_snapshot(self, hospital_id: str):
 return {
 'total_revenue': 1500000, 'total_costs': 1200000, 
 'profit_margin': 0.2, 'timestamp': datetime.now().isoformat()
 }

 async def get_financial_summary(self, hospital_id: str, start_time: datetime, end_time: datetime):
 return {
 'total_revenue': 1500000, 'total_costs': 1200000,
 'occupied_beds': 85, 'patient_count': 200
 }

class PatientFlowTracker:
 async def establish_connection(self, config: DataIngestionConfig):
 return {'status': 'success', 'connection_id': str(uuid.uuid4())}

 async def get_current_flow_status(self, hospital_id: str):
 return {
 'bed_occupancy_rate': 0.85, 'daily_admissions': 25,
 'timestamp': datetime.now().isoformat()
 }

 async def get_flow_summary(self, hospital_id: str, start_time: datetime, end_time: datetime):
 return {
 'bed_occupancy_rate': 0.85, 'average_length_of_stay': 4.2,
 'daily_admissions': 25
 }

class StaffProductivityTracker:
 async def establish_connection(self, config: DataIngestionConfig):
 return {'status': 'success', 'connection_id': str(uuid.uuid4())}

 async def get_current_staff_status(self, hospital_id: str):
 return {
 'total_staff': 200, 'staff_on_duty': 150,
 'timestamp': datetime.now().isoformat()
 }

 async def get_productivity_summary(self, hospital_id: str, start_time: datetime, end_time: datetime):
 return {
 'patients_per_nurse': 8.5, 'overtime_percentage': 12.5
 }

class EquipmentUtilizationMonitor:
 async def establish_connection(self, config: DataIngestionConfig):
 return {'status': 'success', 'connection_id': str(uuid.uuid4())}

 async def get_current_equipment_status(self, hospital_id: str):
 return {
 'total_equipment': 50, 'operational_equipment': 48,
 'timestamp': datetime.now().isoformat()
 }

 async def get_utilization_summary(self, hospital_id: str, start_time: datetime, end_time: datetime):
 return {
 'operating_room_utilization': 0.75, 'average_downtime_percentage': 5.0
 }