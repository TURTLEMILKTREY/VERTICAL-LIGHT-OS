"""
Data Quality Validation and Enrichment Service
Comprehensive data quality validation, enrichment, and standardization for hospital benchmark data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import pandas as pd
import numpy as np
from pathlib import Path
import re
from statistics import mean, median, mode, stdev
import unicodedata

from ...models.hospital_benchmarks import (
    Hospital, CityTier, HospitalType, SpecialtyType
)
from ...config.advanced_config_manager import ConfigManager
from ...services.shared.error_handling import ApplicationError


class ValidationSeverity(Enum):
    """Data validation severity levels"""
    CRITICAL = "critical"     # Data cannot be used
    HIGH = "high"            # Data has significant issues
    MEDIUM = "medium"        # Data has minor issues
    LOW = "low"             # Data has cosmetic issues
    INFO = "info"           # Informational notices


class DataSource(Enum):
    """Data source types"""
    HMS_API = "hms_api"
    GOVERNMENT_API = "government_api"
    SURVEY_MANUAL = "survey_manual"
    PARTNER_NETWORK = "partner_network"
    EXTERNAL_IMPORT = "external_import"
    USER_INPUT = "user_input"


@dataclass
class ValidationRule:
    """Data validation rule definition"""
    rule_id: str
    field_name: str
    rule_type: str  # range, format, required, consistency, logic
    severity: ValidationSeverity
    description: str
    validation_function: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    

@dataclass
class ValidationResult:
    """Result of data validation"""
    rule_id: str
    field_name: str
    severity: ValidationSeverity
    passed: bool
    message: str
    suggested_fix: Optional[str] = None
    original_value: Any = None
    corrected_value: Any = None


@dataclass
class DataQualityReport:
    """Comprehensive data quality report"""
    hospital_id: str
    data_source: DataSource
    validation_timestamp: datetime
    overall_score: int  # 1-100
    total_validations: int
    passed_validations: int
    failed_validations: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    validation_results: List[ValidationResult] = field(default_factory=list)
    enrichment_applied: List[str] = field(default_factory=list)
    standardization_applied: List[str] = field(default_factory=list)
    

class DataQualityError(ApplicationError):
    """Data quality validation errors"""
    pass


class DataQualityValidator:
    """Production Data Quality Validation and Enrichment Service"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Validation rules registry
        self.validation_rules: Dict[str, ValidationRule] = {}
        
        # Data enrichment sources
        self.enrichment_sources = {}
        
        # Standardization mappings
        self.standardization_mappings = self._initialize_standardization_mappings()
        
        # Indian city tier mappings
        self.city_tier_mapping = self._load_city_tier_mapping()
        
        # Hospital specialty mappings
        self.specialty_mapping = self._load_specialty_mapping()
        
        # Initialize validation rules
        self._initialize_validation_rules()
        
        # Load external data sources for enrichment
        self._load_enrichment_sources()
    
    def _initialize_validation_rules(self) -> None:
        """Initialize comprehensive validation rules for hospital data"""
        
        rules = [
            # Hospital identification rules
            ValidationRule(
                rule_id="hospital_name_required",
                field_name="hospital_name",
                rule_type="required",
                severity=ValidationSeverity.CRITICAL,
                description="Hospital name is required",
                validation_function="validate_required"
            ),
            
            ValidationRule(
                rule_id="hospital_name_format",
                field_name="hospital_name",
                rule_type="format",
                severity=ValidationSeverity.MEDIUM,
                description="Hospital name should be properly formatted",
                validation_function="validate_hospital_name_format"
            ),
            
            # Geographic validation
            ValidationRule(
                rule_id="city_tier_valid",
                field_name="city_tier",
                rule_type="range",
                severity=ValidationSeverity.HIGH,
                description="City tier must be 1, 2, 3, or 4",
                validation_function="validate_city_tier",
                parameters={"valid_values": ["1", "2", "3", "4", "tier_1", "tier_2", "tier_3", "tier_4"]}
            ),
            
            ValidationRule(
                rule_id="pincode_format",
                field_name="pincode",
                rule_type="format",
                severity=ValidationSeverity.HIGH,
                description="Pincode must be 6-digit Indian postal code",
                validation_function="validate_pincode_format"
            ),
            
            # Performance metrics validation
            ValidationRule(
                rule_id="bed_occupancy_range",
                field_name="bed_occupancy_rate",
                rule_type="range",
                severity=ValidationSeverity.HIGH,
                description="Bed occupancy rate must be between 0-100%",
                validation_function="validate_percentage_range",
                parameters={"min_value": 0, "max_value": 100}
            ),
            
            ValidationRule(
                rule_id="alos_reasonable",
                field_name="average_length_of_stay",
                rule_type="range",
                severity=ValidationSeverity.HIGH,
                description="Average length of stay must be reasonable (0.1-30 days)",
                validation_function="validate_numeric_range",
                parameters={"min_value": 0.1, "max_value": 30.0}
            ),
            
            ValidationRule(
                rule_id="or_utilization_range",
                field_name="or_utilization_rate",
                rule_type="range",
                severity=ValidationSeverity.HIGH,
                description="OR utilization rate must be between 0-100%",
                validation_function="validate_percentage_range",
                parameters={"min_value": 0, "max_value": 100}
            ),
            
            # Financial validation
            ValidationRule(
                rule_id="revenue_positive",
                field_name="total_revenue",
                rule_type="range",
                severity=ValidationSeverity.CRITICAL,
                description="Total revenue must be positive",
                validation_function="validate_positive_value"
            ),
            
            ValidationRule(
                rule_id="cost_positive",
                field_name="total_costs",
                rule_type="range",
                severity=ValidationSeverity.CRITICAL,
                description="Total costs must be positive",
                validation_function="validate_positive_value"
            ),
            
            ValidationRule(
                rule_id="profit_margin_reasonable",
                field_name="profit_margin",
                rule_type="range",
                severity=ValidationSeverity.MEDIUM,
                description="Profit margin should be reasonable (-50% to +50%)",
                validation_function="validate_percentage_range",
                parameters={"min_value": -50, "max_value": 50}
            ),
            
            # Quality metrics validation
            ValidationRule(
                rule_id="patient_satisfaction_range",
                field_name="patient_satisfaction_score",
                rule_type="range",
                severity=ValidationSeverity.HIGH,
                description="Patient satisfaction score must be between 1-10",
                validation_function="validate_numeric_range",
                parameters={"min_value": 1.0, "max_value": 10.0}
            ),
            
            ValidationRule(
                rule_id="readmission_rate_range",
                field_name="readmission_rate",
                rule_type="range",
                severity=ValidationSeverity.HIGH,
                description="Readmission rate must be between 0-50%",
                validation_function="validate_percentage_range",
                parameters={"min_value": 0, "max_value": 50}
            ),
            
            ValidationRule(
                rule_id="infection_rate_range",
                field_name="infection_rate",
                rule_type="range",
                severity=ValidationSeverity.HIGH,
                description="Hospital infection rate must be between 0-25%",
                validation_function="validate_percentage_range",
                parameters={"min_value": 0, "max_value": 25}
            ),
            
            # Government scheme validation
            ValidationRule(
                rule_id="scheme_revenue_consistency",
                field_name="government_scheme_revenue",
                rule_type="consistency",
                severity=ValidationSeverity.MEDIUM,
                description="Government scheme revenue should be consistent with total revenue",
                validation_function="validate_scheme_revenue_consistency"
            ),
            
            # Data completeness rules
            ValidationRule(
                rule_id="essential_metrics_complete",
                field_name="data_completeness",
                rule_type="logic",
                severity=ValidationSeverity.HIGH,
                description="Essential performance metrics must be complete",
                validation_function="validate_data_completeness"
            ),
            
            # Time-based validation
            ValidationRule(
                rule_id="data_timestamp_recent",
                field_name="data_timestamp",
                rule_type="logic",
                severity=ValidationSeverity.MEDIUM,
                description="Data timestamp should be recent (within 90 days)",
                validation_function="validate_data_freshness",
                parameters={"max_age_days": 90}
            )
        ]
        
        for rule in rules:
            self.validation_rules[rule.rule_id] = rule
    
    def _initialize_standardization_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize standardization mappings for consistent data format"""
        
        return {
            "hospital_types": {
                # Common variations to standard types
                "govt": "Government",
                "government": "Government",
                "pvt": "Private",
                "private": "Private",
                "trust": "Trust",
                "charitable": "Trust",
                "multispecialty": "Multi-Specialty",
                "multi specialty": "Multi-Specialty",
                "super specialty": "Super-Specialty",
                "superspecialty": "Super-Specialty",
                "speciality": "Specialty",
                "maternity": "Specialty"
            },
            
            "city_names": {
                # Common city name variations
                "bombay": "Mumbai",
                "calcutta": "Kolkata",
                "madras": "Chennai",
                "bangalore": "Bengaluru",
                "poona": "Pune",
                "mysore": "Mysuru",
                "delhi": "New Delhi",
                "gurgaon": "Gurugram",
                "noida": "Noida"
            },
            
            "state_names": {
                # State name standardization
                "karnataka": "Karnataka",
                "maharashtra": "Maharashtra",
                "tamil nadu": "Tamil Nadu",
                "west bengal": "West Bengal",
                "uttar pradesh": "Uttar Pradesh",
                "andhra pradesh": "Andhra Pradesh",
                "madhya pradesh": "Madhya Pradesh",
                "himachal pradesh": "Himachal Pradesh",
                "arunachal pradesh": "Arunachal Pradesh"
            },
            
            "specialty_names": {
                # Medical specialty standardization
                "cardio": "Cardiology",
                "ortho": "Orthopedics",
                "neuro": "Neurology",
                "gastro": "Gastroenterology",
                "nephro": "Nephrology",
                "onco": "Oncology",
                "gyne": "Gynecology",
                "pediatrics": "Pediatrics",
                "paediatrics": "Pediatrics",
                "ent": "ENT",
                "ophthalmology": "Ophthalmology",
                "dermatology": "Dermatology"
            },
            
            "currency_formats": {
                # Currency standardization (to INR)
                "rs": "INR",
                "rs.": "INR",
                "rupees": "INR",
                "inr": "INR",
                "₹": "INR"
            }
        }
    
    def _load_city_tier_mapping(self) -> Dict[str, str]:
        """Load comprehensive Indian city tier mapping"""
        
        return {
            # Tier 1 cities
            "mumbai": "1", "delhi": "1", "new delhi": "1", "bengaluru": "1",
            "bangalore": "1", "kolkata": "1", "calcutta": "1", "chennai": "1",
            "madras": "1", "hyderabad": "1", "pune": "1", "poona": "1",
            "ahmedabad": "1", "surat": "1",
            
            # Tier 2 cities
            "jaipur": "2", "lucknow": "2", "kanpur": "2", "nagpur": "2",
            "indore": "2", "thane": "2", "bhopal": "2", "visakhapatnam": "2",
            "pimpri-chinchwad": "2", "patna": "2", "vadodara": "2",
            "ghaziabad": "2", "ludhiana": "2", "agra": "2", "nashik": "2",
            "faridabad": "2", "meerut": "2", "rajkot": "2", "kalyan-dombivli": "2",
            "vasai-virar": "2", "varanasi": "2", "srinagar": "2", "aurangabad": "2",
            "dhanbad": "2", "amritsar": "2", "navi mumbai": "2", "allahabad": "2",
            "ranchi": "2", "howrah": "2", "coimbatore": "2", "jabalpur": "2",
            "gwalior": "2", "vijayawada": "2", "jodhpur": "2", "madurai": "2",
            "raipur": "2", "kota": "2", "guwahati": "2", "chandigarh": "2",
            "solapur": "2", "hubli-dharwad": "2", "tiruchirappalli": "2",
            "bareilly": "2", "mysuru": "2", "mysore": "2", "tiruppur": "2",
            
            # Tier 3 cities (sample)
            "salem": "3", "mira-bhayandar": "3", "warangal": "3", "thiruvananthapuram": "3",
            "guntur": "3", "bhiwandi": "3", "saharanpur": "3", "gorakhpur": "3",
            "bikaner": "3", "amravati": "3", "noida": "3", "jamshedpur": "3",
            "bhilai": "3", "cuttak": "3", "firozabad": "3", "kochi": "3",
            "nellore": "3", "bhavnagar": "3", "dehradun": "3", "durgapur": "3",
            "asansol": "3", "rourkela": "3", "nanded": "3", "kolhapur": "3",
            "ajmer": "3", "gulbarga": "3", "jamnagar": "3", "ujjain": "3",
            "loni": "3", "siliguri": "3", "jhansi": "3", "ulhasnagar": "3",
            "jammu": "3", "sangli-miraj": "3", "mangalore": "3", "erode": "3",
            "belgaum": "3", "ambattur": "3", "tirunelveli": "3", "malegaon": "3",
            "gaya": "3", "jalgaon": "3", "udaipur": "3", "maheshtala": "3"
        }
    
    def _load_specialty_mapping(self) -> Dict[str, str]:
        """Load medical specialty standardization mapping"""
        
        return {
            # Cardiology variations
            "cardiology": "Cardiology",
            "cardiac": "Cardiology", 
            "heart": "Cardiology",
            "cardiovascular": "Cardiology",
            
            # Orthopedics variations
            "orthopedics": "Orthopedics",
            "orthopaedics": "Orthopedics",
            "ortho": "Orthopedics",
            "bone": "Orthopedics",
            "joint": "Orthopedics",
            
            # Neurology variations
            "neurology": "Neurology",
            "neuro": "Neurology",
            "brain": "Neurology",
            "neurological": "Neurology",
            
            # Oncology variations
            "oncology": "Oncology",
            "cancer": "Oncology",
            "tumor": "Oncology",
            "chemotherapy": "Oncology",
            
            # Pediatrics variations
            "pediatrics": "Pediatrics",
            "paediatrics": "Pediatrics",
            "children": "Pediatrics",
            "child": "Pediatrics",
            
            # Gynecology variations
            "gynecology": "Gynecology",
            "gynaecology": "Gynecology",
            "womens": "Gynecology",
            "obstetrics": "Obstetrics & Gynecology",
            
            # General Medicine
            "internal medicine": "Internal Medicine",
            "general medicine": "Internal Medicine",
            "physician": "Internal Medicine",
            
            # Emergency
            "emergency": "Emergency Medicine",
            "casualty": "Emergency Medicine",
            "trauma": "Emergency Medicine"
        }
    
    def _load_enrichment_sources(self) -> None:
        """Load external data sources for enrichment"""
        
        # This would load reference data for enrichment
        # Including hospital accreditation data, demographic data, etc.
        
        self.enrichment_sources = {
            "nabh_accreditation": {},  # NABH accreditation database
            "jci_accreditation": {},   # JCI accreditation database
            "census_data": {},         # Indian census data for demographics
            "pincode_mapping": {},     # Pincode to city/state mapping
            "medical_colleges": {},    # Medical college affiliations
            "insurance_networks": {}   # Insurance network participation
        }
    
    async def validate_hospital_data(self, hospital_data: Dict[str, Any], 
                                   data_source: DataSource,
                                   hospital_id: str) -> DataQualityReport:
        """Comprehensive validation of hospital data"""
        
        validation_start = datetime.utcnow()
        validation_results = []
        
        try:
            # Run all validation rules
            for rule_id, rule in self.validation_rules.items():
                if not rule.enabled:
                    continue
                
                try:
                    result = await self._execute_validation_rule(rule, hospital_data)
                    validation_results.append(result)
                    
                except Exception as e:
                    self.logger.error(f"Validation rule {rule_id} failed: {str(e)}")
                    # Create error result
                    error_result = ValidationResult(
                        rule_id=rule_id,
                        field_name=rule.field_name,
                        severity=ValidationSeverity.CRITICAL,
                        passed=False,
                        message=f"Validation rule execution failed: {str(e)}"
                    )
                    validation_results.append(error_result)
            
            # Calculate quality metrics
            total_validations = len(validation_results)
            passed_validations = len([r for r in validation_results if r.passed])
            failed_validations = total_validations - passed_validations
            
            # Count issues by severity
            critical_issues = len([r for r in validation_results if r.severity == ValidationSeverity.CRITICAL and not r.passed])
            high_issues = len([r for r in validation_results if r.severity == ValidationSeverity.HIGH and not r.passed])
            medium_issues = len([r for r in validation_results if r.severity == ValidationSeverity.MEDIUM and not r.passed])
            low_issues = len([r for r in validation_results if r.severity == ValidationSeverity.LOW and not r.passed])
            
            # Calculate overall quality score (1-100)
            if total_validations == 0:
                overall_score = 0
            else:
                base_score = int((passed_validations / total_validations) * 100)
                
                # Apply severity penalties
                penalty = (critical_issues * 20) + (high_issues * 10) + (medium_issues * 5) + (low_issues * 2)
                overall_score = max(1, min(100, base_score - penalty))
            
            # Create quality report
            report = DataQualityReport(
                hospital_id=hospital_id,
                data_source=data_source,
                validation_timestamp=validation_start,
                overall_score=overall_score,
                total_validations=total_validations,
                passed_validations=passed_validations,
                failed_validations=failed_validations,
                critical_issues=critical_issues,
                high_issues=high_issues,
                medium_issues=medium_issues,
                low_issues=low_issues,
                validation_results=validation_results
            )
            
            self.logger.info(f"Data validation completed for {hospital_id}. Score: {overall_score}/100")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Data validation failed for {hospital_id}: {str(e)}")
            raise DataQualityError(f"Data validation failed: {str(e)}")
    
    async def _execute_validation_rule(self, rule: ValidationRule, 
                                     data: Dict[str, Any]) -> ValidationResult:
        """Execute a single validation rule"""
        
        field_value = data.get(rule.field_name)
        
        try:
            if rule.validation_function == "validate_required":
                passed, message = self._validate_required(field_value)
            
            elif rule.validation_function == "validate_hospital_name_format":
                passed, message = self._validate_hospital_name_format(field_value)
            
            elif rule.validation_function == "validate_city_tier":
                passed, message = self._validate_city_tier(field_value, rule.parameters)
            
            elif rule.validation_function == "validate_pincode_format":
                passed, message = self._validate_pincode_format(field_value)
            
            elif rule.validation_function == "validate_percentage_range":
                passed, message = self._validate_percentage_range(field_value, rule.parameters)
            
            elif rule.validation_function == "validate_numeric_range":
                passed, message = self._validate_numeric_range(field_value, rule.parameters)
            
            elif rule.validation_function == "validate_positive_value":
                passed, message = self._validate_positive_value(field_value)
            
            elif rule.validation_function == "validate_scheme_revenue_consistency":
                passed, message = self._validate_scheme_revenue_consistency(data)
            
            elif rule.validation_function == "validate_data_completeness":
                passed, message = self._validate_data_completeness(data)
            
            elif rule.validation_function == "validate_data_freshness":
                passed, message = self._validate_data_freshness(field_value, rule.parameters)
            
            else:
                passed, message = False, f"Unknown validation function: {rule.validation_function}"
            
            result = ValidationResult(
                rule_id=rule.rule_id,
                field_name=rule.field_name,
                severity=rule.severity,
                passed=passed,
                message=message,
                original_value=field_value
            )
            
            # Generate suggested fix for failed validations
            if not passed:
                result.suggested_fix = self._generate_suggested_fix(rule, field_value, data)
            
            return result
            
        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                field_name=rule.field_name,
                severity=ValidationSeverity.CRITICAL,
                passed=False,
                message=f"Validation execution error: {str(e)}",
                original_value=field_value
            )
    
    def _validate_required(self, value: Any) -> Tuple[bool, str]:
        """Validate that required field has a value"""
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return False, "Required field is empty or missing"
        return True, "Required field validation passed"
    
    def _validate_hospital_name_format(self, value: Any) -> Tuple[bool, str]:
        """Validate hospital name format"""
        if not value or not isinstance(value, str):
            return False, "Hospital name must be a non-empty string"
        
        name = value.strip()
        
        # Check minimum length
        if len(name) < 3:
            return False, "Hospital name too short (minimum 3 characters)"
        
        # Check for suspicious patterns
        if name.lower() in ['test', 'demo', 'sample', 'example']:
            return False, "Hospital name appears to be test data"
        
        # Check for proper capitalization (basic check)
        if name.islower() or name.isupper():
            return False, "Hospital name should use proper capitalization"
        
        return True, "Hospital name format validation passed"
    
    def _validate_city_tier(self, value: Any, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate city tier value"""
        if not value:
            return False, "City tier is required"
        
        valid_values = parameters.get("valid_values", [])
        value_str = str(value).lower().strip()
        
        if value_str not in [v.lower() for v in valid_values]:
            return False, f"Invalid city tier '{value}'. Valid values: {', '.join(valid_values)}"
        
        return True, "City tier validation passed"
    
    def _validate_pincode_format(self, value: Any) -> Tuple[bool, str]:
        """Validate Indian pincode format"""
        if not value:
            return False, "Pincode is required"
        
        pincode_str = str(value).strip()
        
        # Indian pincode must be exactly 6 digits
        if not re.match(r'^\d{6}$', pincode_str):
            return False, "Pincode must be exactly 6 digits"
        
        # Basic range validation (Indian pincodes start from 100000)
        pincode_int = int(pincode_str)
        if not (100000 <= pincode_int <= 999999):
            return False, "Invalid pincode range"
        
        return True, "Pincode format validation passed"
    
    def _validate_percentage_range(self, value: Any, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate percentage value within range"""
        if value is None:
            return False, "Percentage value is required"
        
        try:
            num_value = float(value)
            min_val = parameters.get("min_value", 0)
            max_val = parameters.get("max_value", 100)
            
            if not (min_val <= num_value <= max_val):
                return False, f"Value {num_value}% is outside valid range ({min_val}%-{max_val}%)"
            
            return True, "Percentage range validation passed"
            
        except (ValueError, TypeError):
            return False, f"Invalid percentage value: {value}"
    
    def _validate_numeric_range(self, value: Any, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate numeric value within range"""
        if value is None:
            return False, "Numeric value is required"
        
        try:
            num_value = float(value)
            min_val = parameters.get("min_value")
            max_val = parameters.get("max_value")
            
            if min_val is not None and num_value < min_val:
                return False, f"Value {num_value} is below minimum ({min_val})"
            
            if max_val is not None and num_value > max_val:
                return False, f"Value {num_value} is above maximum ({max_val})"
            
            return True, "Numeric range validation passed"
            
        except (ValueError, TypeError):
            return False, f"Invalid numeric value: {value}"
    
    def _validate_positive_value(self, value: Any) -> Tuple[bool, str]:
        """Validate that value is positive"""
        if value is None:
            return False, "Value is required"
        
        try:
            num_value = float(value)
            if num_value <= 0:
                return False, f"Value must be positive, got: {num_value}"
            
            return True, "Positive value validation passed"
            
        except (ValueError, TypeError):
            return False, f"Invalid numeric value: {value}"
    
    def _validate_scheme_revenue_consistency(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate government scheme revenue consistency"""
        try:
            total_revenue = float(data.get("total_revenue", 0))
            scheme_revenue = float(data.get("government_scheme_revenue", 0))
            
            if scheme_revenue > total_revenue:
                return False, "Government scheme revenue cannot exceed total revenue"
            
            # Check if scheme revenue percentage is reasonable
            if total_revenue > 0:
                scheme_percentage = (scheme_revenue / total_revenue) * 100
                if scheme_percentage > 80:  # More than 80% seems unusual
                    return False, f"Government scheme revenue ({scheme_percentage:.1f}%) seems unusually high"
            
            return True, "Scheme revenue consistency validation passed"
            
        except (ValueError, TypeError):
            return False, "Invalid revenue values for consistency check"
    
    def _validate_data_completeness(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate essential data completeness"""
        
        essential_fields = [
            "hospital_name", "bed_occupancy_rate", "average_length_of_stay",
            "total_revenue", "patient_satisfaction_score"
        ]
        
        missing_fields = []
        for field in essential_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing essential fields: {', '.join(missing_fields)}"
        
        return True, "Data completeness validation passed"
    
    def _validate_data_freshness(self, value: Any, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate data timestamp freshness"""
        if not value:
            return False, "Data timestamp is required"
        
        try:
            if isinstance(value, str):
                timestamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif isinstance(value, datetime):
                timestamp = value
            else:
                return False, "Invalid timestamp format"
            
            max_age_days = parameters.get("max_age_days", 90)
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
            
            if timestamp < cutoff_date:
                age_days = (datetime.utcnow() - timestamp).days
                return False, f"Data is {age_days} days old (maximum {max_age_days} days)"
            
            return True, "Data freshness validation passed"
            
        except (ValueError, TypeError):
            return False, "Invalid timestamp value"
    
    def _generate_suggested_fix(self, rule: ValidationRule, 
                              current_value: Any, 
                              full_data: Dict[str, Any]) -> Optional[str]:
        """Generate suggested fix for validation failures"""
        
        if rule.rule_type == "required" and not current_value:
            return f"Provide a valid value for {rule.field_name}"
        
        elif rule.rule_type == "format" and rule.field_name == "hospital_name":
            if isinstance(current_value, str):
                return f"Standardize name to: {self._standardize_hospital_name(current_value)}"
        
        elif rule.rule_type == "format" and rule.field_name == "pincode":
            if current_value:
                # Try to extract digits
                digits = re.sub(r'\D', '', str(current_value))
                if len(digits) == 6:
                    return f"Use standard format: {digits}"
        
        elif rule.rule_type == "range":
            min_val = rule.parameters.get("min_value")
            max_val = rule.parameters.get("max_value")
            if min_val is not None and max_val is not None:
                return f"Value should be between {min_val} and {max_val}"
            elif min_val is not None:
                return f"Value should be at least {min_val}"
            elif max_val is not None:
                return f"Value should be at most {max_val}"
        
        return None
    
    async def enrich_hospital_data(self, hospital_data: Dict[str, Any], 
                                 hospital_id: str) -> Dict[str, Any]:
        """Enrich hospital data with additional information"""
        
        enriched_data = hospital_data.copy()
        enrichments_applied = []
        
        try:
            # City tier enrichment
            if "city" in enriched_data and "city_tier" not in enriched_data:
                city_name = enriched_data["city"].lower().strip()
                tier = self.city_tier_mapping.get(city_name)
                if tier:
                    enriched_data["city_tier"] = tier
                    enrichments_applied.append("city_tier_mapping")
            
            # Pincode-based enrichment
            if "pincode" in enriched_data:
                pincode = str(enriched_data["pincode"])
                location_data = self._get_location_from_pincode(pincode)
                if location_data:
                    enriched_data.update(location_data)
                    enrichments_applied.append("pincode_location_mapping")
            
            # Hospital type standardization
            if "hospital_type" in enriched_data:
                original_type = enriched_data["hospital_type"]
                standardized_type = self._standardize_hospital_type(original_type)
                if standardized_type != original_type:
                    enriched_data["hospital_type"] = standardized_type
                    enrichments_applied.append("hospital_type_standardization")
            
            # Specialty standardization
            if "primary_specialty" in enriched_data:
                original_specialty = enriched_data["primary_specialty"]
                standardized_specialty = self._standardize_specialty(original_specialty)
                if standardized_specialty != original_specialty:
                    enriched_data["primary_specialty"] = standardized_specialty
                    enrichments_applied.append("specialty_standardization")
            
            # Calculate derived metrics
            derived_metrics = self._calculate_derived_metrics(enriched_data)
            enriched_data.update(derived_metrics)
            if derived_metrics:
                enrichments_applied.append("derived_metrics")
            
            # Add benchmarking context
            benchmark_context = await self._add_benchmark_context(enriched_data)
            enriched_data.update(benchmark_context)
            if benchmark_context:
                enrichments_applied.append("benchmark_context")
            
            enriched_data["enrichments_applied"] = enrichments_applied
            
            self.logger.info(f"Data enrichment completed for {hospital_id}. Applied: {enrichments_applied}")
            
            return enriched_data
            
        except Exception as e:
            self.logger.error(f"Data enrichment failed for {hospital_id}: {str(e)}")
            # Return original data if enrichment fails
            return hospital_data
    
    def _standardize_hospital_name(self, name: str) -> str:
        """Standardize hospital name format"""
        if not name:
            return name
        
        # Remove extra whitespace and normalize
        standardized = ' '.join(name.strip().split())
        
        # Proper case conversion
        standardized = standardized.title()
        
        # Fix common abbreviations
        standardized = re.sub(r'\bHosp\b', 'Hospital', standardized, flags=re.IGNORECASE)
        standardized = re.sub(r'\bMed\b', 'Medical', standardized, flags=re.IGNORECASE)
        standardized = re.sub(r'\bCtr\b', 'Center', standardized, flags=re.IGNORECASE)
        standardized = re.sub(r'\bCentre\b', 'Center', standardized, flags=re.IGNORECASE)
        
        return standardized
    
    def _standardize_hospital_type(self, hospital_type: str) -> str:
        """Standardize hospital type"""
        if not hospital_type:
            return hospital_type
        
        type_lower = hospital_type.lower().strip()
        return self.standardization_mappings["hospital_types"].get(type_lower, hospital_type)
    
    def _standardize_specialty(self, specialty: str) -> str:
        """Standardize medical specialty"""
        if not specialty:
            return specialty
        
        specialty_lower = specialty.lower().strip()
        return self.specialty_mapping.get(specialty_lower, specialty)
    
    def _get_location_from_pincode(self, pincode: str) -> Dict[str, Any]:
        """Get location information from pincode"""
        
        # This would integrate with postal code database
        # For now, return basic validation
        
        if not re.match(r'^\d{6}$', pincode):
            return {}
        
        # Basic state mapping based on pincode ranges
        pincode_int = int(pincode)
        
        if 100000 <= pincode_int <= 199999:
            return {"state": "Delhi", "region": "North"}
        elif 200000 <= pincode_int <= 299999:
            return {"state": "Uttar Pradesh", "region": "North"}
        elif 300000 <= pincode_int <= 399999:
            return {"state": "Rajasthan", "region": "West"}
        elif 400000 <= pincode_int <= 499999:
            return {"state": "Maharashtra", "region": "West"}
        elif 500000 <= pincode_int <= 599999:
            return {"state": "Telangana", "region": "South"}
        elif 600000 <= pincode_int <= 699999:
            return {"state": "Tamil Nadu", "region": "South"}
        elif 700000 <= pincode_int <= 799999:
            return {"state": "West Bengal", "region": "East"}
        elif 800000 <= pincode_int <= 899999:
            return {"state": "Bihar", "region": "East"}
        
        return {}
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived metrics from base data"""
        
        derived = {}
        
        try:
            # Profit margin calculation
            if "total_revenue" in data and "total_costs" in data:
                revenue = float(data["total_revenue"] or 0)
                costs = float(data["total_costs"] or 0)
                
                if revenue > 0:
                    profit_margin = ((revenue - costs) / revenue) * 100
                    derived["profit_margin"] = round(profit_margin, 2)
            
            # Revenue per bed
            if "total_revenue" in data and "total_beds" in data:
                revenue = float(data["total_revenue"] or 0)
                beds = float(data["total_beds"] or 0)
                
                if beds > 0:
                    revenue_per_bed = revenue / beds
                    derived["revenue_per_bed"] = round(revenue_per_bed, 2)
            
            # Occupancy-adjusted revenue
            if "total_revenue" in data and "bed_occupancy_rate" in data:
                revenue = float(data["total_revenue"] or 0)
                occupancy = float(data["bed_occupancy_rate"] or 0)
                
                if occupancy > 0:
                    adjusted_revenue = revenue / (occupancy / 100)
                    derived["occupancy_adjusted_revenue"] = round(adjusted_revenue, 2)
            
            # Government scheme dependency
            if "government_scheme_revenue" in data and "total_revenue" in data:
                scheme_revenue = float(data["government_scheme_revenue"] or 0)
                total_revenue = float(data["total_revenue"] or 0)
                
                if total_revenue > 0:
                    scheme_dependency = (scheme_revenue / total_revenue) * 100
                    derived["government_scheme_dependency"] = round(scheme_dependency, 2)
            
        except (ValueError, TypeError, ZeroDivisionError) as e:
            self.logger.warning(f"Failed to calculate some derived metrics: {str(e)}")
        
        return derived
    
    async def _add_benchmark_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add benchmarking context based on peer comparison"""
        
        context = {}
        
        try:
            # This would compare against peer hospitals
            # For now, add basic context
            
            city_tier = data.get("city_tier", "unknown")
            hospital_type = data.get("hospital_type", "unknown")
            
            context["benchmark_peer_group"] = f"{hospital_type}_{city_tier}"
            context["benchmark_timestamp"] = datetime.utcnow().isoformat()
            
            # Add performance indicators
            if "bed_occupancy_rate" in data:
                occupancy = float(data["bed_occupancy_rate"] or 0)
                if occupancy >= 80:
                    context["occupancy_performance"] = "above_average"
                elif occupancy >= 60:
                    context["occupancy_performance"] = "average"
                else:
                    context["occupancy_performance"] = "below_average"
            
        except Exception as e:
            self.logger.warning(f"Failed to add benchmark context: {str(e)}")
        
        return context
    
    async def standardize_data_format(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize data format for consistency"""
        
        standardized = {}
        standardizations_applied = []
        
        for field_name, value in raw_data.items():
            try:
                # Apply field-specific standardization
                if field_name in ["hospital_name", "name"]:
                    standardized["hospital_name"] = self._standardize_hospital_name(str(value))
                    standardizations_applied.append("hospital_name")
                
                elif field_name in ["city", "city_name"]:
                    city_name = str(value).strip()
                    standardized_city = self.standardization_mappings["city_names"].get(city_name.lower(), city_name)
                    standardized["city"] = standardized_city.title()
                    standardizations_applied.append("city_name")
                
                elif field_name in ["state", "state_name"]:
                    state_name = str(value).strip()
                    standardized_state = self.standardization_mappings["state_names"].get(state_name.lower(), state_name)
                    standardized["state"] = standardized_state
                    standardizations_applied.append("state_name")
                
                elif field_name in ["hospital_type", "type"]:
                    standardized["hospital_type"] = self._standardize_hospital_type(str(value))
                    standardizations_applied.append("hospital_type")
                
                elif field_name in ["specialty", "primary_specialty"]:
                    standardized["primary_specialty"] = self._standardize_specialty(str(value))
                    standardizations_applied.append("specialty")
                
                elif field_name == "pincode":
                    # Standardize pincode format
                    pincode_digits = re.sub(r'\D', '', str(value))
                    if len(pincode_digits) == 6:
                        standardized["pincode"] = pincode_digits
                        standardizations_applied.append("pincode")
                
                elif field_name in ["bed_occupancy_rate", "occupancy_rate"]:
                    # Ensure percentage format
                    try:
                        rate = float(value)
                        if rate > 1 and rate <= 100:  # Already in percentage
                            standardized["bed_occupancy_rate"] = round(rate, 2)
                        elif rate <= 1:  # Convert from decimal
                            standardized["bed_occupancy_rate"] = round(rate * 100, 2)
                        standardizations_applied.append("occupancy_rate")
                    except (ValueError, TypeError):
                        pass
                
                elif "revenue" in field_name or "cost" in field_name:
                    # Standardize financial values
                    try:
                        financial_value = self._standardize_financial_value(value)
                        if financial_value is not None:
                            standardized[field_name] = financial_value
                            standardizations_applied.append("financial_values")
                    except (ValueError, TypeError):
                        pass
                
                else:
                    # Keep original value for other fields
                    standardized[field_name] = value
            
            except Exception as e:
                self.logger.warning(f"Failed to standardize field {field_name}: {str(e)}")
                standardized[field_name] = value
        
        standardized["standardizations_applied"] = standardizations_applied
        return standardized
    
    def _standardize_financial_value(self, value: Any) -> Optional[Decimal]:
        """Standardize financial values to consistent format"""
        
        if value is None:
            return None
        
        try:
            # Convert to string and clean
            value_str = str(value).strip()
            
            # Remove common currency symbols and words
            cleaned = value_str.lower()
            cleaned = re.sub(r'[₹$,\s]', '', cleaned)
            cleaned = re.sub(r'(rs\.?|rupees?|inr)', '', cleaned)
            
            # Handle lakhs and crores
            if 'lakh' in cleaned or 'lac' in cleaned:
                number = re.sub(r'(lakh|lac)', '', cleaned)
                return Decimal(number) * Decimal('100000')
            elif 'crore' in cleaned:
                number = re.sub(r'crore', '', cleaned)
                return Decimal(number) * Decimal('10000000')
            else:
                # Direct conversion
                return Decimal(cleaned)
                
        except (ValueError, TypeError, InvalidOperation):
            return None
    
    def get_validation_summary(self, reports: List[DataQualityReport]) -> Dict[str, Any]:
        """Generate comprehensive validation summary across multiple reports"""
        
        if not reports:
            return {"error": "No validation reports provided"}
        
        summary = {
            "total_hospitals": len(reports),
            "validation_timestamp": datetime.utcnow().isoformat(),
            "overall_metrics": {},
            "quality_distribution": {},
            "common_issues": {},
            "data_source_analysis": {},
            "improvement_recommendations": []
        }
        
        # Calculate overall metrics
        total_score = sum(report.overall_score for report in reports)
        summary["overall_metrics"] = {
            "average_quality_score": round(total_score / len(reports), 1),
            "total_validations": sum(report.total_validations for report in reports),
            "total_passed": sum(report.passed_validations for report in reports),
            "total_failed": sum(report.failed_validations for report in reports),
            "critical_issues": sum(report.critical_issues for report in reports),
            "high_issues": sum(report.high_issues for report in reports),
            "medium_issues": sum(report.medium_issues for report in reports),
            "low_issues": sum(report.low_issues for report in reports)
        }
        
        # Quality score distribution
        score_ranges = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "below_60": 0}
        for report in reports:
            if report.overall_score >= 90:
                score_ranges["90-100"] += 1
            elif report.overall_score >= 80:
                score_ranges["80-89"] += 1
            elif report.overall_score >= 70:
                score_ranges["70-79"] += 1
            elif report.overall_score >= 60:
                score_ranges["60-69"] += 1
            else:
                score_ranges["below_60"] += 1
        
        summary["quality_distribution"] = score_ranges
        
        # Analyze common issues
        issue_counts = {}
        for report in reports:
            for result in report.validation_results:
                if not result.passed:
                    issue_counts[result.rule_id] = issue_counts.get(result.rule_id, 0) + 1
        
        # Get top 10 common issues
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        summary["common_issues"] = {
            rule_id: {
                "count": count, 
                "percentage": round((count / len(reports)) * 100, 1),
                "rule_description": self.validation_rules.get(rule_id, {}).get("description", "Unknown")
            }
            for rule_id, count in common_issues
        }
        
        # Data source analysis
        source_analysis = {}
        for report in reports:
            source = report.data_source.value
            if source not in source_analysis:
                source_analysis[source] = {
                    "count": 0,
                    "total_score": 0,
                    "critical_issues": 0,
                    "high_issues": 0
                }
            
            source_analysis[source]["count"] += 1
            source_analysis[source]["total_score"] += report.overall_score
            source_analysis[source]["critical_issues"] += report.critical_issues
            source_analysis[source]["high_issues"] += report.high_issues
        
        # Calculate averages for each source
        for source, data in source_analysis.items():
            data["average_score"] = round(data["total_score"] / data["count"], 1)
        
        summary["data_source_analysis"] = source_analysis
        
        # Generate improvement recommendations
        recommendations = []
        
        # Based on common issues
        if summary["overall_metrics"]["critical_issues"] > 0:
            recommendations.append("Address critical data quality issues immediately - these prevent data usage")
        
        if summary["overall_metrics"]["average_quality_score"] < 80:
            recommendations.append("Implement systematic data quality improvement process")
        
        if score_ranges["below_60"] > len(reports) * 0.2:  # More than 20% below 60
            recommendations.append("Focus on data collection process improvement for low-scoring hospitals")
        
        # Source-specific recommendations
        for source, data in source_analysis.items():
            if data["average_score"] < 70:
                recommendations.append(f"Improve data quality from {source} - currently underperforming")
        
        summary["improvement_recommendations"] = recommendations
        
        return summary