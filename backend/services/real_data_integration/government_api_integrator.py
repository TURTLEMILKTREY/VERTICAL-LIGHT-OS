"""
Government Health API Integration Service
Real integration with Indian government health data systems
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
from aiohttp import ClientSession, ClientTimeout
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote
import hashlib
import hmac
import base64
from bs4 import BeautifulSoup
import re

from ...models.hospital_benchmarks import (
    GovernmentScheme, CityTier, HospitalType
)
from ...config.advanced_config_manager import ConfigManager
from ...services.shared.error_handling import ApplicationError


class GovernmentAPI(Enum):
    """Indian Government Health APIs"""
    NATIONAL_HEALTH_PORTAL = "nhp"
    AYUSHMAN_BHARAT_PMJAY = "pmjay"
    CGHS_PORTAL = "cghs"
    ESIC_PORTAL = "esic"
    HMIS_INDIA = "hmis_india"
    NATIONAL_SAMPLE_SURVEY = "nss"
    HEALTH_FACILITY_REGISTRY = "hfr"
    NABH_PORTAL = "nabh"
    STATE_HEALTH_DEPARTMENTS = "state_health"


@dataclass
class GovernmentAPICredentials:
    """Government API access credentials"""
    api_type: GovernmentAPI
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    base_url: str = ""
    auth_endpoint: str = ""
    additional_params: Dict[str, str] = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


class GovernmentAPIError(ApplicationError):
    """Government API integration errors"""
    pass


class GovernmentDataIntegrator:
    """Production Government Health Data Integration Service"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Government API configurations
        self.api_configs = {
            GovernmentAPI.NATIONAL_HEALTH_PORTAL: {
                "base_url": "https://www.nhp.gov.in/api",
                "auth_type": "api_key",
                "rate_limit": 100  # requests per hour
            },
            GovernmentAPI.AYUSHMAN_BHARAT_PMJAY: {
                "base_url": "https://pmjay.gov.in/api/v1",
                "auth_type": "oauth",
                "rate_limit": 500
            },
            GovernmentAPI.CGHS_PORTAL: {
                "base_url": "https://cghs.nic.in/api",
                "auth_type": "token",
                "rate_limit": 200
            },
            GovernmentAPI.ESIC_PORTAL: {
                "base_url": "https://www.esic.in/api",
                "auth_type": "basic_auth",
                "rate_limit": 150
            },
            GovernmentAPI.HMIS_INDIA: {
                "base_url": "https://hmis.in/api/v2",
                "auth_type": "hmac",
                "rate_limit": 300
            },
            GovernmentAPI.HEALTH_FACILITY_REGISTRY: {
                "base_url": "https://facility.nha.gov.in/api",
                "auth_type": "api_key",
                "rate_limit": 250
            },
            GovernmentAPI.NABH_PORTAL: {
                "base_url": "https://www.nabh.co/api",
                "auth_type": "certificate",
                "rate_limit": 100
            }
        }
        
        self.rate_limits = {}
        self.auth_tokens = {}
    
    async def collect_government_scheme_data(self, hospital_id: str, 
                                           schemes: List[GovernmentScheme]) -> Dict[str, Any]:
        """Collect real government scheme data for a hospital"""
        
        try:
            collected_data = {
                "hospital_id": hospital_id,
                "collection_timestamp": datetime.utcnow().isoformat(),
                "schemes_data": {},
                "quality_score": 0,
                "success": True,
                "errors": []
            }
            
            total_score = 0
            successful_collections = 0
            
            # Collect data for each requested scheme
            for scheme in schemes:
                try:
                    if scheme == GovernmentScheme.AYUSHMAN_BHARAT:
                        scheme_data = await self._collect_ayushman_bharat_data(hospital_id)
                    elif scheme == GovernmentScheme.CGHS:
                        scheme_data = await self._collect_cghs_data(hospital_id)
                    elif scheme == GovernmentScheme.ESI:
                        scheme_data = await self._collect_esi_data(hospital_id)
                    elif scheme == GovernmentScheme.STATE_SCHEMES:
                        scheme_data = await self._collect_state_schemes_data(hospital_id)
                    else:
                        scheme_data = {"error": "Unsupported scheme"}
                    
                    collected_data["schemes_data"][scheme.value] = scheme_data
                    
                    if "error" not in scheme_data:
                        successful_collections += 1
                        total_score += scheme_data.get("quality_score", 5)
                    
                except Exception as e:
                    error_msg = f"Failed to collect {scheme.value} data: {str(e)}"
                    collected_data["errors"].append(error_msg)
                    self.logger.error(error_msg)
            
            # Calculate overall quality score
            if successful_collections > 0:
                collected_data["quality_score"] = int(total_score / successful_collections)
            else:
                collected_data["quality_score"] = 0
                collected_data["success"] = False
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Government scheme data collection failed: {str(e)}")
            return {
                "hospital_id": hospital_id,
                "success": False,
                "error": str(e),
                "collection_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _collect_ayushman_bharat_data(self, hospital_id: str) -> Dict[str, Any]:
        """Collect Ayushman Bharat (PM-JAY) data"""
        
        try:
            # Get hospital empanelment status first
            empanelment_data = await self._get_pmjay_hospital_empanelment(hospital_id)
            
            if not empanelment_data.get("is_empaneled"):
                return {
                    "scheme": "ayushman_bharat",
                    "is_empaneled": False,
                    "message": "Hospital not empaneled under PM-JAY",
                    "quality_score": 3
                }
            
            # Collect transaction data
            transactions = await self._get_pmjay_transactions(hospital_id)
            
            # Calculate metrics
            current_month = datetime.now().strftime("%Y-%m")
            monthly_data = self._process_pmjay_transactions(transactions, current_month)
            
            return {
                "scheme": "ayushman_bharat",
                "is_empaneled": True,
                "empanelment_code": empanelment_data.get("empanelment_code"),
                "empanelment_date": empanelment_data.get("empanelment_date"),
                "data_period": current_month,
                "total_cases": monthly_data.get("total_cases", 0),
                "total_patients": monthly_data.get("total_patients", 0),
                "total_billed_amount": monthly_data.get("total_billed", Decimal("0")),
                "total_approved_amount": monthly_data.get("total_approved", Decimal("0")),
                "total_received_amount": monthly_data.get("total_received", Decimal("0")),
                "approval_rate": monthly_data.get("approval_rate", Decimal("0")),
                "rejection_rate": monthly_data.get("rejection_rate", Decimal("0")),
                "average_reimbursement_days": monthly_data.get("avg_reimbursement_days", 0),
                "emergency_cases": monthly_data.get("emergency_cases", 0),
                "planned_cases": monthly_data.get("planned_cases", 0),
                "surgery_cases": monthly_data.get("surgery_cases", 0),
                "medical_cases": monthly_data.get("medical_cases", 0),
                "average_case_value": monthly_data.get("avg_case_value", Decimal("0")),
                "price_variance_percentage": monthly_data.get("price_variance", Decimal("0")),
                "quality_score": 8,
                "data_source": "pmjay_api"
            }
            
        except Exception as e:
            self.logger.error(f"Ayushman Bharat data collection failed: {str(e)}")
            return {
                "scheme": "ayushman_bharat", 
                "error": str(e),
                "quality_score": 2
            }
    
    async def _get_pmjay_hospital_empanelment(self, hospital_id: str) -> Dict[str, Any]:
        """Get hospital empanelment status from PM-JAY API"""
        
        session = await self._get_authenticated_session(GovernmentAPI.AYUSHMAN_BHARAT_PMJAY)
        
        try:
            # PM-JAY Hospital Search API
            url = f"{self.api_configs[GovernmentAPI.AYUSHMAN_BHARAT_PMJAY]['base_url']}/hospitals/search"
            
            params = {
                "hospitalCode": hospital_id,
                "status": "active"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("hospitals") and len(data["hospitals"]) > 0:
                        hospital_info = data["hospitals"][0]
                        
                        return {
                            "is_empaneled": True,
                            "empanelment_code": hospital_info.get("empanelmentCode"),
                            "empanelment_date": hospital_info.get("empanelmentDate"),
                            "hospital_name": hospital_info.get("hospitalName"),
                            "district": hospital_info.get("district"),
                            "state": hospital_info.get("state"),
                            "bed_count": hospital_info.get("bedCount"),
                            "specialties": hospital_info.get("specialties", [])
                        }
                    else:
                        return {"is_empaneled": False}
                else:
                    self.logger.warning(f"PM-JAY empanelment check failed: {response.status}")
                    return {"is_empaneled": False, "error": f"API error: {response.status}"}
                    
        finally:
            await session.close()
    
    async def _get_pmjay_transactions(self, hospital_id: str) -> List[Dict[str, Any]]:
        """Get PM-JAY transaction data for hospital"""
        
        session = await self._get_authenticated_session(GovernmentAPI.AYUSHMAN_BHARAT_PMJAY)
        
        try:
            # PM-JAY Transaction API
            url = f"{self.api_configs[GovernmentAPI.AYUSHMAN_BHARAT_PMJAY]['base_url']}/transactions"
            
            # Get last 3 months of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            params = {
                "hospitalCode": hospital_id,
                "fromDate": start_date.strftime("%Y-%m-%d"),
                "toDate": end_date.strftime("%Y-%m-%d"),
                "pageSize": 1000,
                "pageNumber": 1
            }
            
            all_transactions = []
            
            # Handle pagination
            while True:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = data.get("transactions", [])
                        
                        if not transactions:
                            break
                        
                        all_transactions.extend(transactions)
                        
                        # Check if more pages available
                        if len(transactions) < params["pageSize"]:
                            break
                        
                        params["pageNumber"] += 1
                    else:
                        self.logger.warning(f"PM-JAY transactions API error: {response.status}")
                        break
            
            return all_transactions
            
        finally:
            await session.close()
    
    def _process_pmjay_transactions(self, transactions: List[Dict], 
                                  target_month: str) -> Dict[str, Any]:
        """Process PM-JAY transactions for monthly metrics"""
        
        monthly_transactions = []
        
        # Filter transactions for target month
        for txn in transactions:
            txn_date = txn.get("transactionDate", "")
            if txn_date.startswith(target_month):
                monthly_transactions.append(txn)
        
        if not monthly_transactions:
            return {}
        
        # Calculate metrics
        total_cases = len(monthly_transactions)
        total_patients = len(set(txn.get("beneficiaryId") for txn in monthly_transactions))
        
        total_billed = sum(Decimal(str(txn.get("billedAmount", 0))) for txn in monthly_transactions)
        total_approved = sum(Decimal(str(txn.get("approvedAmount", 0))) for txn in monthly_transactions)
        total_received = sum(Decimal(str(txn.get("settledAmount", 0))) for txn in monthly_transactions)
        
        approved_cases = len([txn for txn in monthly_transactions if txn.get("status") == "approved"])
        rejected_cases = len([txn for txn in monthly_transactions if txn.get("status") == "rejected"])
        
        approval_rate = Decimal(str(approved_cases * 100 / total_cases)) if total_cases > 0 else Decimal("0")
        rejection_rate = Decimal(str(rejected_cases * 100 / total_cases)) if total_cases > 0 else Decimal("0")
        
        # Calculate reimbursement days
        reimbursement_days = []
        for txn in monthly_transactions:
            if txn.get("settledDate") and txn.get("approvedDate"):
                approved_date = datetime.fromisoformat(txn["approvedDate"])
                settled_date = datetime.fromisoformat(txn["settledDate"])
                days = (settled_date - approved_date).days
                reimbursement_days.append(days)
        
        avg_reimbursement_days = int(sum(reimbursement_days) / len(reimbursement_days)) if reimbursement_days else 0
        
        # Case type analysis
        emergency_cases = len([txn for txn in monthly_transactions if txn.get("admissionType") == "emergency"])
        planned_cases = total_cases - emergency_cases
        
        surgery_cases = len([txn for txn in monthly_transactions if txn.get("procedureType", "").lower().find("surgery") != -1])
        medical_cases = total_cases - surgery_cases
        
        avg_case_value = total_approved / total_cases if total_cases > 0 else Decimal("0")
        
        # Price variance calculation
        if total_billed > 0:
            price_variance = ((total_billed - total_approved) / total_billed * 100)
        else:
            price_variance = Decimal("0")
        
        return {
            "total_cases": total_cases,
            "total_patients": total_patients,
            "total_billed": total_billed,
            "total_approved": total_approved,
            "total_received": total_received,
            "approval_rate": approval_rate,
            "rejection_rate": rejection_rate,
            "avg_reimbursement_days": avg_reimbursement_days,
            "emergency_cases": emergency_cases,
            "planned_cases": planned_cases,
            "surgery_cases": surgery_cases,
            "medical_cases": medical_cases,
            "avg_case_value": avg_case_value,
            "price_variance": price_variance
        }
    
    async def _collect_cghs_data(self, hospital_id: str) -> Dict[str, Any]:
        """Collect CGHS (Central Government Health Scheme) data"""
        
        try:
            session = await self._get_authenticated_session(GovernmentAPI.CGHS_PORTAL)
            
            # CGHS Hospital Panel API
            url = f"{self.api_configs[GovernmentAPI.CGHS_PORTAL]['base_url']}/hospitals/panel-status"
            
            params = {
                "hospitalId": hospital_id,
                "includeTransactions": True,
                "fromDate": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "toDate": datetime.now().strftime("%Y-%m-%d")
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get("isPanelHospital"):
                        return {
                            "scheme": "cghs",
                            "is_empaneled": False,
                            "message": "Hospital not panelled under CGHS",
                            "quality_score": 3
                        }
                    
                    # Process CGHS transaction data
                    transactions = data.get("transactions", [])
                    current_month = datetime.now().strftime("%Y-%m")
                    
                    metrics = self._process_cghs_transactions(transactions, current_month)
                    
                    return {
                        "scheme": "cghs",
                        "is_empaneled": True,
                        "panel_code": data.get("panelCode"),
                        "panel_date": data.get("panelDate"),
                        "data_period": current_month,
                        **metrics,
                        "quality_score": 8,
                        "data_source": "cghs_api"
                    }
                else:
                    return {
                        "scheme": "cghs",
                        "error": f"CGHS API error: {response.status}",
                        "quality_score": 2
                    }
                    
        except Exception as e:
            self.logger.error(f"CGHS data collection failed: {str(e)}")
            return {
                "scheme": "cghs",
                "error": str(e), 
                "quality_score": 2
            }
        finally:
            if 'session' in locals():
                await session.close()
    
    def _process_cghs_transactions(self, transactions: List[Dict], 
                                 target_month: str) -> Dict[str, Any]:
        """Process CGHS transactions for monthly metrics"""
        
        monthly_transactions = [
            txn for txn in transactions 
            if txn.get("treatmentDate", "").startswith(target_month)
        ]
        
        if not monthly_transactions:
            return {
                "total_cases": 0,
                "total_patients": 0,
                "total_billed_amount": Decimal("0"),
                "total_approved_amount": Decimal("0"),
                "approval_rate": Decimal("0")
            }
        
        total_cases = len(monthly_transactions)
        total_patients = len(set(txn.get("cghs_number") for txn in monthly_transactions))
        
        total_billed = sum(Decimal(str(txn.get("billAmount", 0))) for txn in monthly_transactions)
        total_approved = sum(Decimal(str(txn.get("approvedAmount", 0))) for txn in monthly_transactions)
        
        approved_count = len([txn for txn in monthly_transactions if txn.get("status") == "approved"])
        approval_rate = Decimal(str(approved_count * 100 / total_cases)) if total_cases > 0 else Decimal("0")
        
        return {
            "total_cases": total_cases,
            "total_patients": total_patients,
            "total_billed_amount": total_billed,
            "total_approved_amount": total_approved,
            "approval_rate": approval_rate,
            "average_case_value": total_approved / total_cases if total_cases > 0 else Decimal("0")
        }
    
    async def _collect_esi_data(self, hospital_id: str) -> Dict[str, Any]:
        """Collect ESI (Employee State Insurance) data"""
        
        try:
            session = await self._get_authenticated_session(GovernmentAPI.ESIC_PORTAL)
            
            # ESI Hospital Agreement API
            url = f"{self.api_configs[GovernmentAPI.ESIC_PORTAL]['base_url']}/hospitals/agreement-status"
            
            params = {
                "hospitalCode": hospital_id,
                "includeClaimData": True,
                "reportPeriod": datetime.now().strftime("%Y-%m")
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get("hasActiveAgreement"):
                        return {
                            "scheme": "esi",
                            "is_empaneled": False,
                            "message": "Hospital has no active ESI agreement",
                            "quality_score": 3
                        }
                    
                    # Process ESI claims data
                    claims = data.get("claims", [])
                    metrics = self._process_esi_claims(claims)
                    
                    return {
                        "scheme": "esi",
                        "is_empaneled": True,
                        "agreement_number": data.get("agreementNumber"),
                        "agreement_date": data.get("agreementDate"),
                        "data_period": datetime.now().strftime("%Y-%m"),
                        **metrics,
                        "quality_score": 7,
                        "data_source": "esic_api"
                    }
                else:
                    return {
                        "scheme": "esi",
                        "error": f"ESI API error: {response.status}",
                        "quality_score": 2
                    }
                    
        except Exception as e:
            self.logger.error(f"ESI data collection failed: {str(e)}")
            return {
                "scheme": "esi",
                "error": str(e),
                "quality_score": 2
            }
        finally:
            if 'session' in locals():
                await session.close()
    
    def _process_esi_claims(self, claims: List[Dict]) -> Dict[str, Any]:
        """Process ESI claims for metrics"""
        
        if not claims:
            return {
                "total_cases": 0,
                "total_patients": 0,
                "total_billed_amount": Decimal("0"),
                "total_approved_amount": Decimal("0"),
                "approval_rate": Decimal("0")
            }
        
        total_cases = len(claims)
        total_patients = len(set(claim.get("esi_number") for claim in claims))
        
        total_billed = sum(Decimal(str(claim.get("claimedAmount", 0))) for claim in claims)
        total_approved = sum(Decimal(str(claim.get("settledAmount", 0))) for claim in claims)
        
        approved_count = len([claim for claim in claims if claim.get("status") == "settled"])
        approval_rate = Decimal(str(approved_count * 100 / total_cases)) if total_cases > 0 else Decimal("0")
        
        return {
            "total_cases": total_cases,
            "total_patients": total_patients,
            "total_billed_amount": total_billed,
            "total_approved_amount": total_approved,
            "approval_rate": approval_rate
        }
    
    async def _collect_state_schemes_data(self, hospital_id: str) -> Dict[str, Any]:
        """Collect State Government Health Schemes data"""
        
        try:
            # This would integrate with various state health department APIs
            # For now, implementing a generic state scheme collector
            
            state_apis = [
                {"name": "Maharashtra Mahatma Jyotirao Phule Jan Arogya Yojana", "api_endpoint": "/mjpjay"},
                {"name": "Tamil Nadu Chief Minister's Comprehensive Health Insurance Scheme", "api_endpoint": "/cmchis"},
                {"name": "Karnataka Arogya Karnataka", "api_endpoint": "/arogya_karnataka"},
                {"name": "West Bengal Swasthya Sathi", "api_endpoint": "/swasthya_sathi"}
            ]
            
            collected_schemes = []
            total_cases = 0
            total_amount = Decimal("0")
            
            # Try to collect from available state APIs
            for state_scheme in state_apis:
                try:
                    scheme_data = await self._collect_generic_state_scheme(
                        hospital_id, state_scheme["name"], state_scheme["api_endpoint"]
                    )
                    
                    if scheme_data.get("success"):
                        collected_schemes.append(scheme_data)
                        total_cases += scheme_data.get("total_cases", 0)
                        total_amount += scheme_data.get("total_approved_amount", Decimal("0"))
                        
                except Exception as e:
                    self.logger.warning(f"Failed to collect {state_scheme['name']}: {str(e)}")
                    continue
            
            return {
                "scheme": "state_schemes",
                "collected_schemes": collected_schemes,
                "total_state_cases": total_cases,
                "total_state_amount": total_amount,
                "number_of_schemes": len(collected_schemes),
                "data_period": datetime.now().strftime("%Y-%m"),
                "quality_score": 6 if collected_schemes else 3,
                "data_source": "state_apis"
            }
            
        except Exception as e:
            self.logger.error(f"State schemes data collection failed: {str(e)}")
            return {
                "scheme": "state_schemes",
                "error": str(e),
                "quality_score": 2
            }
    
    async def _collect_generic_state_scheme(self, hospital_id: str, 
                                          scheme_name: str, 
                                          api_endpoint: str) -> Dict[str, Any]:
        """Generic collector for state health schemes"""
        
        # This would be implemented per state API
        # For now, return a placeholder structure
        return {
            "scheme_name": scheme_name,
            "success": False,
            "message": "State scheme APIs require individual implementation",
            "total_cases": 0,
            "total_approved_amount": Decimal("0")
        }
    
    async def _get_authenticated_session(self, api_type: GovernmentAPI) -> ClientSession:
        """Get authenticated session for government API"""
        
        config = self.api_configs[api_type]
        timeout = ClientTimeout(total=30, connect=10)
        
        headers = {
            "User-Agent": "VerticalLight-Gov-Integrator/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Get credentials from config
        creds = self._get_api_credentials(api_type)
        
        # Authentication handling
        if config["auth_type"] == "api_key":
            headers["X-API-Key"] = creds.api_key
        elif config["auth_type"] == "oauth":
            token = await self._get_oauth_token(api_type, creds)
            headers["Authorization"] = f"Bearer {token}"
        elif config["auth_type"] == "token":
            headers["Authorization"] = f"Token {creds.api_key}"
        elif config["auth_type"] == "hmac":
            headers.update(self._generate_hmac_headers(creds))
        
        session = ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=5)
        )
        
        return session
    
    def _get_api_credentials(self, api_type: GovernmentAPI) -> GovernmentAPICredentials:
        """Get API credentials from configuration"""
        
        config_key = f"government_apis.{api_type.value}"
        creds_config = self.config.get(config_key, {})
        
        return GovernmentAPICredentials(
            api_type=api_type,
            api_key=creds_config.get("api_key"),
            client_id=creds_config.get("client_id"),
            client_secret=creds_config.get("client_secret"),
            username=creds_config.get("username"),
            password=creds_config.get("password"),
            base_url=creds_config.get("base_url", self.api_configs[api_type]["base_url"]),
            auth_endpoint=creds_config.get("auth_endpoint", "")
        )
    
    async def _get_oauth_token(self, api_type: GovernmentAPI, 
                             creds: GovernmentAPICredentials) -> str:
        """Get OAuth token for API access"""
        
        # Check if we have a valid cached token
        cached_token = self.auth_tokens.get(api_type.value)
        if cached_token and cached_token["expires_at"] > datetime.utcnow():
            return cached_token["access_token"]
        
        # Get new token
        token_url = f"{creds.base_url}{creds.auth_endpoint}"
        
        token_data = {
            "grant_type": "client_credentials",
            "client_id": creds.client_id,
            "client_secret": creds.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=token_data) as response:
                if response.status == 200:
                    token_response = await response.json()
                    
                    # Cache token
                    expires_in = token_response.get("expires_in", 3600)
                    self.auth_tokens[api_type.value] = {
                        "access_token": token_response["access_token"],
                        "expires_at": datetime.utcnow() + timedelta(seconds=expires_in - 300)  # 5 min buffer
                    }
                    
                    return token_response["access_token"]
                else:
                    raise GovernmentAPIError(f"OAuth token request failed: {response.status}")
    
    def _generate_hmac_headers(self, creds: GovernmentAPICredentials) -> Dict[str, str]:
        """Generate HMAC authentication headers"""
        
        timestamp = str(int(datetime.utcnow().timestamp()))
        message = f"{creds.client_id}{timestamp}"
        
        signature = hmac.new(
            creds.client_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "X-Client-ID": creds.client_id,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }
    
    async def get_hospital_accreditation_data(self, hospital_id: str) -> Dict[str, Any]:
        """Get hospital accreditation data from NABH and other bodies"""
        
        try:
            accreditation_data = {
                "hospital_id": hospital_id,
                "nabh_status": await self._get_nabh_accreditation(hospital_id),
                "jci_status": await self._get_jci_accreditation(hospital_id),
                "state_accreditations": await self._get_state_accreditations(hospital_id),
                "collection_timestamp": datetime.utcnow().isoformat()
            }
            
            return accreditation_data
            
        except Exception as e:
            self.logger.error(f"Accreditation data collection failed: {str(e)}")
            return {
                "hospital_id": hospital_id,
                "error": str(e),
                "collection_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_nabh_accreditation(self, hospital_id: str) -> Dict[str, Any]:
        """Get NABH accreditation status"""
        
        try:
            session = await self._get_authenticated_session(GovernmentAPI.NABH_PORTAL)
            
            url = f"{self.api_configs[GovernmentAPI.NABH_PORTAL]['base_url']}/hospitals/accreditation"
            
            params = {"hospitalId": hospital_id}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "is_nabh_accredited": data.get("isAccredited", False),
                        "accreditation_level": data.get("level"),
                        "accreditation_date": data.get("accreditationDate"),
                        "validity_till": data.get("validityTill"),
                        "nabh_score": data.get("score"),
                        "certificate_number": data.get("certificateNumber")
                    }
                else:
                    return {"is_nabh_accredited": False, "error": f"API error: {response.status}"}
                    
        except Exception as e:
            return {"is_nabh_accredited": False, "error": str(e)}
        finally:
            if 'session' in locals():
                await session.close()
    
    async def _get_jci_accreditation(self, hospital_id: str) -> Dict[str, Any]:
        """Get JCI accreditation status (if available via API)"""
        
        # JCI doesn't have public API, so this would be manual data entry
        # or web scraping from JCI website
        return {
            "is_jci_accredited": False,
            "message": "JCI accreditation status requires manual verification"
        }
    
    async def _get_state_accreditations(self, hospital_id: str) -> List[Dict[str, Any]]:
        """Get state-level accreditations"""
        
        # This would query various state health department APIs
        return []
    
    def register_government_api_credentials(self, api_type: GovernmentAPI,
                                         credentials: GovernmentAPICredentials) -> Dict[str, Any]:
        """Register government API credentials"""
        
        try:
            config_key = f"government_apis.{api_type.value}"
            
            creds_dict = {
                "api_key": credentials.api_key,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "username": credentials.username,
                "password": credentials.password,
                "base_url": credentials.base_url,
                "auth_endpoint": credentials.auth_endpoint,
                "registered_at": datetime.utcnow().isoformat()
            }
            
            # Encrypt sensitive data
            if credentials.api_key:
                creds_dict["api_key"] = self._encrypt_credential(credentials.api_key)
            if credentials.client_secret:
                creds_dict["client_secret"] = self._encrypt_credential(credentials.client_secret)
            if credentials.password:
                creds_dict["password"] = self._encrypt_credential(credentials.password)
            
            self.config.set(config_key, creds_dict)
            
            return {
                "success": True,
                "api_type": api_type.value,
                "message": "Government API credentials registered successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to register {api_type.value} credentials: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _encrypt_credential(self, credential: str) -> str:
        """Encrypt sensitive credential"""
        # Simple base64 encoding - in production, use proper encryption
        return base64.b64encode(credential.encode()).decode()
    
    def _decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt credential"""
        return base64.b64decode(encrypted_credential.encode()).decode()


# Additional utility functions
class GovernmentDataValidator:
    """Validator for government scheme data"""
    
    @staticmethod
    def validate_pmjay_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PM-JAY data quality"""
        
        validation_result = {
            "is_valid": True,
            "quality_score": 10,
            "issues": []
        }
        
        # Check required fields
        required_fields = ["total_cases", "total_approved_amount", "approval_rate"]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                validation_result["issues"].append(f"Missing required field: {field}")
                validation_result["quality_score"] -= 2
        
        # Validate data ranges
        if "approval_rate" in data:
            approval_rate = float(data["approval_rate"])
            if not (0 <= approval_rate <= 100):
                validation_result["issues"].append(f"Approval rate out of range: {approval_rate}")
                validation_result["quality_score"] -= 3
        
        if "average_reimbursement_days" in data:
            reimb_days = data["average_reimbursement_days"]
            if reimb_days and (reimb_days < 0 or reimb_days > 180):
                validation_result["issues"].append(f"Reimbursement days unrealistic: {reimb_days}")
                validation_result["quality_score"] -= 2
        
        validation_result["is_valid"] = validation_result["quality_score"] >= 6
        
        return validation_result