"""
Hospital Intelligence Application
================================

Production-ready hospital intelligence system with lifecycle-aware benchmarking.

This module provides:
- Comprehensive hospital analysis
- Intelligent lifecycle-aware benchmarking  
- Growth velocity assessment
- Strategic recommendations
- Executive reporting and dashboards
"""

from .working_hospital_system import (
    HospitalIntelligenceSystem,
    HospitalAnalysisRequest,
    HospitalAnalysisResult,
    HospitalTier
)

__all__ = [
    "HospitalIntelligenceSystem",
    "HospitalAnalysisRequest", 
    "HospitalAnalysisResult",
    "HospitalTier"
]

__version__ = "2.0.0"