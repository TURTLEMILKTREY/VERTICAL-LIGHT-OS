"""
HMS Integration Connectors for Indian Hospital Management Systems
Supports major HMS platforms used in Indian hospitals
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class HMSType(Enum):
    """Supported HMS types in Indian hospitals"""
    BIRLAMEDISOFT = "birlamedisoft"
    MEDEIL = "medeil"
    EHOSPITAL = "ehospital"  # Government NIC system
    LIFELINE = "lifeline"
    SMART_HMS = "smart_hms"
    JEEVANDAAN = "jeevandaan"
    EPIC = "epic"  # Used by Apollo
    CERNER = "cerner"  # Used by Fortis
    GENERIC_HL7 = "generic_hl7"
    GENERIC_FHIR = "generic_fhir"

@dataclass
class HMSConnectionConfig:
    """HMS connection configuration"""
    hms_type: HMSType
    api_endpoint: str
    username: str
    password: str
    database_name: Optional[str] = None
    api_key: Optional[str] = None
    additional_config: Dict[str, Any] = None

@dataclass 
class PatientRecord:
    """Standardized patient record from HMS"""
    patient_id: str
    admission_id: Optional[str]
    name: str
    age: int
    gender: str
    admission_date: Optional[datetime]
    discharge_date: Optional[datetime]
    department: str
    doctor_name: str
    diagnosis: List[str]
    procedures: List[str]
    bed_number: Optional[str]
    room_type: str
    insurance_details: Dict[str, Any]
    total_bill: Optional[float]
    payment_status: str

class BaseHMSConnector(ABC):
    """Base class for all HMS connectors"""
    
    def __init__(self, config: HMSConnectionConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_connected = False
        
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to HMS"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close connection to HMS"""
        pass
    
    @abstractmethod
    async def get_patient_data(self, start_date: datetime, end_date: datetime) -> List[PatientRecord]:
        """Get patient data for date range"""
        pass
    
    @abstractmethod
    async def get_real_time_admissions(self) -> List[PatientRecord]:
        """Get real-time admission data"""
        pass
    
    @abstractmethod
    async def get_bed_status(self) -> Dict[str, Any]:
        """Get current bed occupancy status"""
        pass
    
    @abstractmethod
    async def get_department_statistics(self) -> Dict[str, Any]:
        """Get department-wise statistics"""
        pass

class BirlamedisoftConnector(BaseHMSConnector):
    """Connector for Birlamedisoft HMS - Popular in Indian hospitals"""
    
    async def connect(self) -> bool:
        """Connect to Birlamedisoft HMS API"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Birlamedisoft typically uses REST API with token authentication
            login_url = f"{self.config.api_endpoint}/api/auth/login"
            login_data = {
                "username": self.config.username,
                "password": self.config.password,
                "database": self.config.database_name
            }
            
            async with self.session.post(login_url, json=login_data) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    self.auth_token = auth_data.get('token')
                    self.is_connected = True
                    logger.info("Successfully connected to Birlamedisoft HMS")
                    return True
                else:
                    logger.error(f"Failed to connect to Birlamedisoft: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error connecting to Birlamedisoft HMS: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from Birlamedisoft HMS"""
        if self.session:
            await self.session.close()
        self.is_connected = False
    
    async def get_patient_data(self, start_date: datetime, end_date: datetime) -> List[PatientRecord]:
        """Get patient admission data from Birlamedisoft"""
        if not self.is_connected:
            await self.connect()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            url = f"{self.config.api_endpoint}/api/patients/admissions"
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._parse_birla_patient_record(record) for record in data.get('patients', [])]
                else:
                    logger.error(f"Failed to get patient data: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting patient data from Birlamedisoft: {str(e)}")
            return []
    
    async def get_real_time_admissions(self) -> List[PatientRecord]:
        """Get real-time admission data"""
        # Get admissions from today
        today = datetime.now().date()
        return await self.get_patient_data(
            datetime.combine(today, datetime.min.time()),
            datetime.now()
        )
    
    async def get_bed_status(self) -> Dict[str, Any]:
        """Get current bed occupancy from Birlamedisoft"""
        if not self.is_connected:
            await self.connect()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            url = f"{self.config.api_endpoint}/api/beds/status"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'total_beds': data.get('total_beds', 0),
                        'occupied_beds': data.get('occupied_beds', 0),
                        'available_beds': data.get('available_beds', 0),
                        'occupancy_rate': data.get('occupancy_rate', 0.0),
                        'department_wise': data.get('department_wise', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    logger.error(f"Failed to get bed status: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting bed status from Birlamedisoft: {str(e)}")
            return {}
    
    async def get_department_statistics(self) -> Dict[str, Any]:
        """Get department-wise statistics"""
        if not self.is_connected:
            await self.connect()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            url = f"{self.config.api_endpoint}/api/departments/statistics"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting department statistics: {str(e)}")
            return {}
    
    def _parse_birla_patient_record(self, record: Dict[str, Any]) -> PatientRecord:
        """Parse Birlamedisoft patient record to standard format"""
        return PatientRecord(
            patient_id=record.get('patient_id', ''),
            admission_id=record.get('admission_id'),
            name=record.get('patient_name', ''),
            age=record.get('age', 0),
            gender=record.get('gender', ''),
            admission_date=self._parse_date(record.get('admission_date')),
            discharge_date=self._parse_date(record.get('discharge_date')),
            department=record.get('department', ''),
            doctor_name=record.get('consulting_doctor', ''),
            diagnosis=record.get('diagnosis', []),
            procedures=record.get('procedures', []),
            bed_number=record.get('bed_number'),
            room_type=record.get('room_type', ''),
            insurance_details=record.get('insurance', {}),
            total_bill=record.get('total_amount'),
            payment_status=record.get('payment_status', 'pending')
        )
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        except:
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except:
                return None

class MedeilConnector(BaseHMSConnector):
    """Connector for Medeil HMS - Popular retail pharmacy and hospital software"""
    
    async def connect(self) -> bool:
        """Connect to Medeil HMS"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Medeil uses different API structure
            auth_url = f"{self.config.api_endpoint}/medeil/authenticate"
            auth_data = {
                "loginId": self.config.username,
                "password": self.config.password,
                "hospitalCode": self.config.database_name
            }
            
            async with self.session.post(auth_url, json=auth_data) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    if auth_response.get('status') == 'success':
                        self.session_id = auth_response.get('sessionId')
                        self.is_connected = True
                        logger.info("Successfully connected to Medeil HMS")
                        return True
                    
            logger.error("Failed to authenticate with Medeil HMS")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to Medeil HMS: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from Medeil HMS"""
        if self.session and self.is_connected:
            try:
                logout_url = f"{self.config.api_endpoint}/medeil/logout"
                await self.session.post(logout_url, json={"sessionId": self.session_id})
            except:
                pass
            await self.session.close()
        self.is_connected = False
    
    async def get_patient_data(self, start_date: datetime, end_date: datetime) -> List[PatientRecord]:
        """Get patient data from Medeil HMS"""
        if not self.is_connected:
            await self.connect()
        
        try:
            url = f"{self.config.api_endpoint}/medeil/patients/list"
            params = {
                "sessionId": self.session_id,
                "fromDate": start_date.strftime("%d/%m/%Y"),
                "toDate": end_date.strftime("%d/%m/%Y")
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        return [self._parse_medeil_patient_record(record) 
                               for record in data.get('data', [])]
                return []
                
        except Exception as e:
            logger.error(f"Error getting patient data from Medeil: {str(e)}")
            return []
    
    async def get_real_time_admissions(self) -> List[PatientRecord]:
        """Get today's admissions from Medeil"""
        today = datetime.now().date()
        return await self.get_patient_data(
            datetime.combine(today, datetime.min.time()),
            datetime.now()
        )
    
    async def get_bed_status(self) -> Dict[str, Any]:
        """Get bed status from Medeil HMS"""
        if not self.is_connected:
            await self.connect()
        
        try:
            url = f"{self.config.api_endpoint}/medeil/beds/occupancy"
            params = {"sessionId": self.session_id}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        bed_data = data.get('data', {})
                        return {
                            'total_beds': bed_data.get('totalBeds', 0),
                            'occupied_beds': bed_data.get('occupiedBeds', 0),
                            'available_beds': bed_data.get('availableBeds', 0),
                            'occupancy_rate': bed_data.get('occupancyPercentage', 0.0) / 100,
                            'timestamp': datetime.now().isoformat()
                        }
                return {}
                
        except Exception as e:
            logger.error(f"Error getting bed status from Medeil: {str(e)}")
            return {}
    
    async def get_department_statistics(self) -> Dict[str, Any]:
        """Get department statistics from Medeil"""
        # Medeil might not have this endpoint, return empty for now
        return {}
    
    def _parse_medeil_patient_record(self, record: Dict[str, Any]) -> PatientRecord:
        """Parse Medeil patient record to standard format"""
        return PatientRecord(
            patient_id=record.get('patientId', ''),
            admission_id=record.get('admissionNo'),
            name=record.get('patientName', ''),
            age=record.get('age', 0),
            gender=record.get('sex', ''),
            admission_date=self._parse_medeil_date(record.get('admissionDate')),
            discharge_date=self._parse_medeil_date(record.get('dischargeDate')),
            department=record.get('department', ''),
            doctor_name=record.get('doctorName', ''),
            diagnosis=record.get('diagnosis', '').split(',') if record.get('diagnosis') else [],
            procedures=record.get('procedures', []),
            bed_number=record.get('bedNo'),
            room_type=record.get('roomType', ''),
            insurance_details=record.get('insuranceDetails', {}),
            total_bill=record.get('totalAmount'),
            payment_status=record.get('paymentStatus', 'pending')
        )
    
    def _parse_medeil_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse Medeil date format (DD/MM/YYYY)"""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, "%d/%m/%Y %H:%M:%S")
        except:
            try:
                return datetime.strptime(date_string, "%d/%m/%Y")
            except:
                return None

class EHospitalConnector(BaseHMSConnector):
    """Connector for eHospital (NIC) - Government hospital system"""
    
    async def connect(self) -> bool:
        """Connect to eHospital system"""
        try:
            self.session = aiohttp.ClientSession()
            
            # eHospital uses SOAP-based web services
            soap_url = f"{self.config.api_endpoint}/HISIntegrationService"
            soap_body = f"""
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Header>
                    <Authentication>
                        <Username>{self.config.username}</Username>
                        <Password>{self.config.password}</Password>
                        <HospitalCode>{self.config.database_name}</HospitalCode>
                    </Authentication>
                </soap:Header>
                <soap:Body>
                    <ValidateUser/>
                </soap:Body>
            </soap:Envelope>
            """
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'ValidateUser'
            }
            
            async with self.session.post(soap_url, data=soap_body, headers=headers) as response:
                if response.status == 200:
                    xml_response = await response.text()
                    # Parse XML response
                    root = ET.fromstring(xml_response)
                    # Check for successful authentication
                    if "success" in xml_response.lower():
                        self.is_connected = True
                        logger.info("Successfully connected to eHospital")
                        return True
                        
            logger.error("Failed to authenticate with eHospital")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to eHospital: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from eHospital"""
        if self.session:
            await self.session.close()
        self.is_connected = False
    
    async def get_patient_data(self, start_date: datetime, end_date: datetime) -> List[PatientRecord]:
        """Get patient data from eHospital using SOAP"""
        if not self.is_connected:
            await self.connect()
        
        try:
            soap_url = f"{self.config.api_endpoint}/HISIntegrationService"
            soap_body = f"""
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <GetPatientAdmissions>
                        <StartDate>{start_date.strftime('%Y-%m-%d')}</StartDate>
                        <EndDate>{end_date.strftime('%Y-%m-%d')}</EndDate>
                        <HospitalCode>{self.config.database_name}</HospitalCode>
                    </GetPatientAdmissions>
                </soap:Body>
            </soap:Envelope>
            """
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'GetPatientAdmissions'
            }
            
            async with self.session.post(soap_url, data=soap_body, headers=headers) as response:
                if response.status == 200:
                    xml_response = await response.text()
                    return self._parse_ehospital_xml_response(xml_response)
                return []
                
        except Exception as e:
            logger.error(f"Error getting patient data from eHospital: {str(e)}")
            return []
    
    async def get_real_time_admissions(self) -> List[PatientRecord]:
        """Get today's admissions from eHospital"""
        today = datetime.now().date()
        return await self.get_patient_data(
            datetime.combine(today, datetime.min.time()),
            datetime.now()
        )
    
    async def get_bed_status(self) -> Dict[str, Any]:
        """Get bed status from eHospital"""
        if not self.is_connected:
            await self.connect()
        
        try:
            soap_url = f"{self.config.api_endpoint}/HISIntegrationService"
            soap_body = f"""
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <GetBedOccupancy>
                        <HospitalCode>{self.config.database_name}</HospitalCode>
                    </GetBedOccupancy>
                </soap:Body>
            </soap:Envelope>
            """
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'GetBedOccupancy'
            }
            
            async with self.session.post(soap_url, data=soap_body, headers=headers) as response:
                if response.status == 200:
                    xml_response = await response.text()
                    return self._parse_ehospital_bed_status(xml_response)
                return {}
                
        except Exception as e:
            logger.error(f"Error getting bed status from eHospital: {str(e)}")
            return {}
    
    async def get_department_statistics(self) -> Dict[str, Any]:
        """Get department statistics from eHospital"""
        # Implementation would depend on eHospital SOAP services
        return {}
    
    def _parse_ehospital_xml_response(self, xml_response: str) -> List[PatientRecord]:
        """Parse eHospital XML response to patient records"""
        try:
            root = ET.fromstring(xml_response)
            patients = []
            
            # Navigate XML structure based on eHospital schema
            for patient_elem in root.findall('.//Patient'):
                patient = PatientRecord(
                    patient_id=patient_elem.find('PatientId').text if patient_elem.find('PatientId') is not None else '',
                    admission_id=patient_elem.find('AdmissionNo').text if patient_elem.find('AdmissionNo') is not None else None,
                    name=patient_elem.find('PatientName').text if patient_elem.find('PatientName') is not None else '',
                    age=int(patient_elem.find('Age').text) if patient_elem.find('Age') is not None else 0,
                    gender=patient_elem.find('Gender').text if patient_elem.find('Gender') is not None else '',
                    admission_date=self._parse_ehospital_date(patient_elem.find('AdmissionDate').text if patient_elem.find('AdmissionDate') is not None else None),
                    discharge_date=self._parse_ehospital_date(patient_elem.find('DischargeDate').text if patient_elem.find('DischargeDate') is not None else None),
                    department=patient_elem.find('Department').text if patient_elem.find('Department') is not None else '',
                    doctor_name=patient_elem.find('DoctorName').text if patient_elem.find('DoctorName') is not None else '',
                    diagnosis=[],  # Would need to parse diagnosis elements
                    procedures=[],  # Would need to parse procedure elements
                    bed_number=patient_elem.find('BedNumber').text if patient_elem.find('BedNumber') is not None else None,
                    room_type=patient_elem.find('RoomType').text if patient_elem.find('RoomType') is not None else '',
                    insurance_details={},
                    total_bill=None,
                    payment_status='unknown'
                )
                patients.append(patient)
            
            return patients
            
        except Exception as e:
            logger.error(f"Error parsing eHospital XML response: {str(e)}")
            return []
    
    def _parse_ehospital_bed_status(self, xml_response: str) -> Dict[str, Any]:
        """Parse eHospital bed status XML"""
        try:
            root = ET.fromstring(xml_response)
            bed_elem = root.find('.//BedStatus')
            
            if bed_elem is not None:
                return {
                    'total_beds': int(bed_elem.find('TotalBeds').text) if bed_elem.find('TotalBeds') is not None else 0,
                    'occupied_beds': int(bed_elem.find('OccupiedBeds').text) if bed_elem.find('OccupiedBeds') is not None else 0,
                    'available_beds': int(bed_elem.find('AvailableBeds').text) if bed_elem.find('AvailableBeds') is not None else 0,
                    'occupancy_rate': float(bed_elem.find('OccupancyRate').text) if bed_elem.find('OccupancyRate') is not None else 0.0,
                    'timestamp': datetime.now().isoformat()
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error parsing eHospital bed status: {str(e)}")
            return {}
    
    def _parse_ehospital_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse eHospital date format"""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        except:
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except:
                return None

class HMSConnectorFactory:
    """Factory class to create appropriate HMS connectors"""
    
    @staticmethod
    def create_connector(hms_type: HMSType, config: HMSConnectionConfig) -> BaseHMSConnector:
        """Create HMS connector based on type"""
        connector_map = {
            HMSType.BIRLAMEDISOFT: BirlamedisoftConnector,
            HMSType.MEDEIL: MedeilConnector,
            HMSType.EHOSPITAL: EHospitalConnector,
            # Add other connectors as implemented
        }
        
        connector_class = connector_map.get(hms_type)
        if not connector_class:
            raise ValueError(f"Unsupported HMS type: {hms_type}")
        
        return connector_class(config)
    
    @staticmethod
    def get_supported_hms_types() -> List[str]:
        """Get list of supported HMS types"""
        return [hms_type.value for hms_type in HMSType]


# HMS Integration Manager that uses these connectors
class HMSIntegrationManager:
    """Main HMS integration manager"""
    
    def __init__(self):
        self.active_connectors: Dict[str, BaseHMSConnector] = {}
    
    async def establish_connection(self, config) -> Dict[str, Any]:
        """Establish connection to HMS"""
        try:
            hms_type = HMSType(config.connection_config.get('system_type', 'generic_hl7'))
            
            hms_config = HMSConnectionConfig(
                hms_type=hms_type,
                api_endpoint=config.connection_config.get('api_endpoint', ''),
                username=config.connection_config.get('credentials', {}).get('username', ''),
                password=config.connection_config.get('credentials', {}).get('password', ''),
                database_name=config.connection_config.get('credentials', {}).get('database', ''),
                api_key=config.connection_config.get('credentials', {}).get('api_key')
            )
            
            connector = HMSConnectorFactory.create_connector(hms_type, hms_config)
            
            if await connector.connect():
                self.active_connectors[config.hospital_id] = connector
                return {
                    'status': 'success',
                    'connection_id': config.hospital_id,
                    'hms_type': hms_type.value
                }
            else:
                return {
                    'status': 'failed',
                    'error': 'Connection failed'
                }
                
        except Exception as e:
            logger.error(f"Failed to establish HMS connection: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def get_current_data(self, hospital_id: str) -> Dict[str, Any]:
        """Get current HMS data"""
        connector = self.active_connectors.get(hospital_id)
        if not connector:
            return {}
        
        try:
            # Get real-time admissions
            admissions = await connector.get_real_time_admissions()
            
            # Get bed status
            bed_status = await connector.get_bed_status()
            
            # Get department statistics
            dept_stats = await connector.get_department_statistics()
            
            return {
                'admissions_today': len(admissions),
                'bed_status': bed_status,
                'department_statistics': dept_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting current HMS data: {str(e)}")
            return {}
    
    async def get_real_time_data(self, config) -> Dict[str, Any]:
        """Get real-time HMS data"""
        return await self.get_current_data(config.hospital_id)