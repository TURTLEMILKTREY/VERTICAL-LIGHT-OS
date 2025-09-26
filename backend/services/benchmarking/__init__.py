"""
Benchmarking Services
====================

Intelligent benchmarking services for hospital performance analysis.

This module provides:
- Lifecycle-aware benchmarking algorithms
- Intelligent target generation
- Growth velocity assessment
- Stage progression analysis
"""

from .intelligent_benchmarking_engine import (
 IntelligentLifecycleBenchmarkingEngine,
 IntelligentHospitalInput,
 IntelligentBenchmarkResult
)

__all__ = [
 "IntelligentLifecycleBenchmarkingEngine",
 "IntelligentHospitalInput", 
 "IntelligentBenchmarkResult"
]

__version__ = "2.0.0"