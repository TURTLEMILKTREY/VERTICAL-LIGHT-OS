#!/usr/bin/env python3

"""
Hospital Security Module
========================

Production-ready security implementation for single hospital deployment.
Includes authentication, input validation, and basic HIPAA compliance measures.
"""

import os
import hashlib
import secrets
import hmac
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
 """Security configuration for hospital deployment"""
 api_key: str
 encryption_key: Optional[bytes] = None
 session_timeout: int = 3600 # 1 hour
 max_request_size: int = 10_000_000 # 10MB
 rate_limit_requests: int = 100 # requests per minute
 enable_audit_logging: bool = True
 hipaa_compliance: bool = True

class HospitalAuthentication:
 """
 Authentication system for hospital API
 Supports API key authentication with audit logging
 """

 def __init__(self, config: SecurityConfig):
 self.config = config
 self.valid_api_keys = {
 config.api_key: {
 "name": "Hospital System",
 "permissions": ["read", "write", "admin"],
 "created": datetime.now(timezone.utc),
 "last_used": None
 }
 }
 self.audit_log = []

 def verify_api_key(self, api_key: str, client_ip: str = None) -> Dict[str, Any]:
 """
 Verify API key and return authentication result

 Args:
 api_key: API key to verify
 client_ip: Client IP address for audit logging

 Returns:
 Dictionary with authentication result
 """
 try:
 if not api_key:
 return self._create_auth_result(False, "Missing API key")

 # Check if API key is valid
 if api_key not in self.valid_api_keys:
 self._log_security_event("INVALID_API_KEY", {
 "api_key_prefix": api_key[:10] + "...",
 "client_ip": client_ip,
 "timestamp": datetime.now(timezone.utc)
 })
 return self._create_auth_result(False, "Invalid API key")

 # Update last used timestamp
 self.valid_api_keys[api_key]["last_used"] = datetime.now(timezone.utc)

 # Log successful authentication
 if self.config.enable_audit_logging:
 self._log_security_event("SUCCESSFUL_AUTH", {
 "client_ip": client_ip,
 "timestamp": datetime.now(timezone.utc),
 "api_key_name": self.valid_api_keys[api_key]["name"]
 })

 return self._create_auth_result(True, "Authentication successful", {
 "permissions": self.valid_api_keys[api_key]["permissions"],
 "name": self.valid_api_keys[api_key]["name"]
 })

 except Exception as e:
 logger.error(f"Authentication error: {e}")
 return self._create_auth_result(False, "Authentication system error")

 def _create_auth_result(self, success: bool, message: str, data: Dict = None) -> Dict[str, Any]:
 """Create standardized authentication result"""
 return {
 "success": success,
 "message": message,
 "data": data or {},
 "timestamp": datetime.now(timezone.utc)
 }

 def _log_security_event(self, event_type: str, details: Dict[str, Any]):
 """Log security events for audit trail"""
 event = {
 "event_type": event_type,
 "details": details,
 "timestamp": datetime.now(timezone.utc)
 }
 self.audit_log.append(event)

 # Log to file for persistence
 logger.info(f"Security Event: {event_type} - {details}")

 def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
 """Get recent security audit log entries"""
 return self.audit_log[-limit:]

class InputValidator:
 """
 Input validation and sanitization for hospital data
 Prevents injection attacks and ensures data quality
 """

 # Validation patterns
 PATTERNS = {
 'hospital_name': r'^[a-zA-Z0-9\s\-\.\,\&]{1,255}$',
 'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
 'phone': r'^\+?[\d\s\-\(\)]{10,20}$',
 'numeric': r'^[\d\.\-\+eE]+$',
 'alphanumeric': r'^[a-zA-Z0-9\s]{1,100}$'
 }

 # SQL injection patterns to detect
 SQL_INJECTION_PATTERNS = [
 r"('|(\\x27)|(\\x2D))", # Quotes
 r"(;|(\\x3B))", # Semicolon
 r"(\\x00)", # Null bytes
 r"(union|select|insert|update|delete|drop|create|alter)", # SQL keywords
 r"(script|javascript|vbscript)", # Script injections
 r"(<|>|&lt;|&gt;)" # HTML/XML tags
 ]

 def __init__(self):
 self.compiled_patterns = {}
 for name, pattern in self.PATTERNS.items():
 self.compiled_patterns[name] = re.compile(pattern, re.IGNORECASE)

 self.injection_patterns = [
 re.compile(pattern, re.IGNORECASE) 
 for pattern in self.SQL_INJECTION_PATTERNS
 ]

 def validate_hospital_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
 """
 Validate and sanitize hospital input data

 Args:
 data: Input data dictionary

 Returns:
 Validation result with cleaned data and errors
 """
 result = {
 "valid": True,
 "errors": [],
 "warnings": [],
 "cleaned_data": {},
 "security_issues": []
 }

 try:
 # Validate each field
 for field_name, field_value in data.items():
 validation = self._validate_field(field_name, field_value)

 if validation["valid"]:
 result["cleaned_data"][field_name] = validation["cleaned_value"]
 else:
 result["valid"] = False
 result["errors"].extend(validation["errors"])

 # Check for security issues
 if validation["security_issues"]:
 result["security_issues"].extend(validation["security_issues"])

 # Additional business rule validation
 business_validation = self._validate_business_rules(result["cleaned_data"])
 if not business_validation["valid"]:
 result["valid"] = False
 result["errors"].extend(business_validation["errors"])

 return result

 except Exception as e:
 logger.error(f"Validation error: {e}")
 result["valid"] = False
 result["errors"].append(f"Validation system error: {str(e)}")
 return result

 def _validate_field(self, field_name: str, field_value: Any) -> Dict[str, Any]:
 """Validate individual field"""
 result = {
 "valid": True,
 "errors": [],
 "security_issues": [],
 "cleaned_value": field_value
 }

 # Convert to string for pattern matching
 str_value = str(field_value) if field_value is not None else ""

 # Check for injection attacks
 for pattern in self.injection_patterns:
 if pattern.search(str_value):
 result["security_issues"].append(f"Potential injection detected in {field_name}")
 result["valid"] = False
 result["errors"].append(f"Invalid characters detected in {field_name}")
 return result

 # Field-specific validation
 if field_name == "hospital_name":
 if not self.compiled_patterns['hospital_name'].match(str_value):
 result["valid"] = False
 result["errors"].append("Invalid hospital name format")
 else:
 result["cleaned_value"] = self._sanitize_string(str_value)

 elif field_name in ["annual_revenue", "annual_operating_expenses", "net_income", "total_assets", "total_liabilities"]:
 try:
 numeric_value = float(field_value)
 if numeric_value < -1_000_000_000 or numeric_value > 100_000_000_000: # Reasonable bounds
 result["valid"] = False
 result["errors"].append(f"{field_name} value out of reasonable range")
 else:
 result["cleaned_value"] = numeric_value
 except (ValueError, TypeError):
 result["valid"] = False
 result["errors"].append(f"{field_name} must be a valid number")

 elif field_name in ["total_beds", "occupied_beds", "annual_admissions", "emergency_visits", "surgical_cases"]:
 try:
 int_value = int(field_value)
 if int_value < 0 or int_value > 100_000: # Reasonable bounds
 result["valid"] = False
 result["errors"].append(f"{field_name} value out of reasonable range")
 else:
 result["cleaned_value"] = int_value
 except (ValueError, TypeError):
 result["valid"] = False
 result["errors"].append(f"{field_name} must be a valid integer")

 elif field_name in ["patient_satisfaction_score", "readmission_rate", "infection_rate", "mortality_rate"]:
 try:
 float_value = float(field_value)
 if float_value < 0 or float_value > 100:
 result["valid"] = False
 result["errors"].append(f"{field_name} must be between 0 and 100")
 else:
 result["cleaned_value"] = float_value
 except (ValueError, TypeError):
 result["valid"] = False
 result["errors"].append(f"{field_name} must be a valid number")

 return result

 def _validate_business_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
 """Validate business rules across multiple fields"""
 result = {
 "valid": True,
 "errors": []
 }

 # Check occupied beds don't exceed total beds
 if "occupied_beds" in data and "total_beds" in data:
 if data["occupied_beds"] > data["total_beds"]:
 result["valid"] = False
 result["errors"].append("Occupied beds cannot exceed total beds")

 # Check financial consistency
 if all(key in data for key in ["annual_revenue", "annual_operating_expenses", "net_income"]):
 calculated_income = data["annual_revenue"] - data["annual_operating_expenses"]
 income_difference = abs(calculated_income - data["net_income"])

 # Allow for some variance due to other income/expenses
 if income_difference > (data["annual_revenue"] * 0.5): # 50% variance allowed
 result["errors"].append("Net income inconsistent with revenue and expenses")

 # Check staff ratios
 if "total_staff" in data and "physicians" in data and "nurses" in data:
 clinical_staff = data["physicians"] + data["nurses"]
 if clinical_staff > data["total_staff"]:
 result["valid"] = False
 result["errors"].append("Clinical staff cannot exceed total staff")

 return result

 def _sanitize_string(self, value: str) -> str:
 """Sanitize string input"""
 # Remove potentially dangerous characters
 sanitized = re.sub(r'[<>"\';()&+]', '', value)
 # Normalize whitespace
 sanitized = re.sub(r'\s+', ' ', sanitized.strip())
 return sanitized

class HIPAACompliance:
 """
 Basic HIPAA compliance implementation for single hospital
 Includes encryption, audit logging, and data protection
 """

 def __init__(self, encryption_key: bytes = None):
 """Initialize HIPAA compliance system"""
 if encryption_key:
 self.cipher = Fernet(encryption_key)
 else:
 # Generate new key if none provided
 self.cipher = Fernet(Fernet.generate_key())

 self.audit_trail = []

 def encrypt_sensitive_data(self, data: Union[str, Dict]) -> str:
 """
 Encrypt sensitive data (PHI)

 Args:
 data: Data to encrypt

 Returns:
 Encrypted data as string
 """
 try:
 if isinstance(data, dict):
 data_str = str(data) # Convert dict to string
 else:
 data_str = str(data)

 encrypted = self.cipher.encrypt(data_str.encode())
 return base64.b64encode(encrypted).decode()

 except Exception as e:
 logger.error(f"Encryption failed: {e}")
 raise

 def decrypt_sensitive_data(self, encrypted_data: str) -> str:
 """
 Decrypt sensitive data

 Args:
 encrypted_data: Encrypted data string

 Returns:
 Decrypted data
 """
 try:
 encrypted_bytes = base64.b64decode(encrypted_data.encode())
 decrypted = self.cipher.decrypt(encrypted_bytes)
 return decrypted.decode()

 except Exception as e:
 logger.error(f"Decryption failed: {e}")
 raise

 def create_audit_entry(self, action: str, user_id: str, data_accessed: str, 
 ip_address: str = None) -> Dict[str, Any]:
 """
 Create HIPAA audit log entry

 Args:
 action: Action performed (CREATE, READ, UPDATE, DELETE)
 user_id: User identifier
 data_accessed: Description of data accessed
 ip_address: Client IP address

 Returns:
 Audit entry dictionary
 """
 audit_entry = {
 "audit_id": secrets.token_hex(16),
 "timestamp": datetime.now(timezone.utc),
 "action": action,
 "user_id": user_id,
 "data_hash": hashlib.sha256(data_accessed.encode()).hexdigest(),
 "ip_address": ip_address,
 "compliance_version": "1.0"
 }

 self.audit_trail.append(audit_entry)

 # Log to file for persistence
 logger.info(f"HIPAA Audit: {audit_entry}")

 return audit_entry

 def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
 """Get recent audit trail entries"""
 return self.audit_trail[-limit:]

 def validate_data_retention(self, data_age_days: int) -> bool:
 """
 Validate data retention compliance

 Args:
 data_age_days: Age of data in days

 Returns:
 True if data is within retention policy
 """
 # HIPAA requires 6 years retention for most data
 max_retention_days = 365 * 6 # 6 years
 return data_age_days <= max_retention_days

class RateLimiter:
 """
 Rate limiting for API endpoints
 Prevents abuse and ensures system stability
 """

 def __init__(self, max_requests: int = 100, time_window: int = 60):
 """
 Initialize rate limiter

 Args:
 max_requests: Maximum requests allowed
 time_window: Time window in seconds
 """
 self.max_requests = max_requests
 self.time_window = time_window
 self.request_counts = {} # {client_id: [timestamp, ...]}

 def is_allowed(self, client_id: str) -> bool:
 """
 Check if request is allowed for client

 Args:
 client_id: Client identifier (IP address, API key, etc.)

 Returns:
 True if request is allowed
 """
 now = datetime.now(timezone.utc)

 # Initialize if new client
 if client_id not in self.request_counts:
 self.request_counts[client_id] = []

 # Remove old requests outside time window
 cutoff_time = now - timedelta(seconds=self.time_window)
 self.request_counts[client_id] = [
 timestamp for timestamp in self.request_counts[client_id]
 if timestamp > cutoff_time
 ]

 # Check if under limit
 if len(self.request_counts[client_id]) < self.max_requests:
 self.request_counts[client_id].append(now)
 return True

 return False

 def get_client_stats(self, client_id: str) -> Dict[str, Any]:
 """Get rate limiting stats for client"""
 if client_id not in self.request_counts:
 return {
 "requests_made": 0,
 "requests_remaining": self.max_requests,
 "reset_time": datetime.now(timezone.utc) + timedelta(seconds=self.time_window)
 }

 current_requests = len(self.request_counts[client_id])
 return {
 "requests_made": current_requests,
 "requests_remaining": max(0, self.max_requests - current_requests),
 "reset_time": min(self.request_counts[client_id]) + timedelta(seconds=self.time_window)
 }

# Initialize security components for hospital deployment
def create_hospital_security(api_key: str = None) -> Dict[str, Any]:
 """
 Create hospital security configuration

 Args:
 api_key: API key for authentication

 Returns:
 Dictionary with security components
 """
 # Generate secure API key if not provided
 if not api_key:
 api_key = secrets.token_urlsafe(32)

 # Create security configuration
 config = SecurityConfig(
 api_key=api_key,
 encryption_key=Fernet.generate_key(),
 enable_audit_logging=True,
 hipaa_compliance=True
 )

 # Initialize security components
 auth = HospitalAuthentication(config)
 validator = InputValidator()
 hipaa = HIPAACompliance(config.encryption_key)
 rate_limiter = RateLimiter(max_requests=100, time_window=60)

 return {
 "config": config,
 "authentication": auth,
 "validator": validator,
 "hipaa": hipaa,
 "rate_limiter": rate_limiter
 }

# Example usage
if __name__ == "__main__":
 # Create security system
 security = create_hospital_security()

 print("Hospital Security System Initialized")
 print(f"API Key: {security['config'].api_key}")
 print(f"HIPAA Compliance: {security['config'].hipaa_compliance}")

 # Test input validation
 test_data = {
 "hospital_name": "Test Hospital",
 "annual_revenue": 50000000,
 "total_beds": 200,
 "occupied_beds": 150
 }

 validation_result = security['validator'].validate_hospital_data(test_data)
 print(f"Validation Result: {validation_result['valid']}")

 # Test authentication
 auth_result = security['authentication'].verify_api_key(
 security['config'].api_key, 
 "192.168.1.100"
 )
 print(f"Authentication Result: {auth_result['success']}")