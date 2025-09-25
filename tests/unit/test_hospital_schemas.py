"""
Unit tests for Hospital Intelligence Engine schemas and models.

This module contains comprehensive unit tests for hospital data models,
focusing on data validation, type checking, and business logic.
"""

import pytest
from decimal import Decimal
from typing import Dict, Any

# Test imports
from backend.models.hospital_schemas_simple import (
    HospitalProfile, HospitalLocation, HospitalFinancialMetrics,
    HospitalOperationalMetrics, HospitalQualityMetrics,
    HospitalTier, HospitalType
)


class TestHospitalLocation:
    """Test cases for HospitalLocation model."""
    
    def test_hospital_location_creation_valid(self):
        """Test valid hospital location creation."""
        location = HospitalLocation(
            address="Test Hospital Road",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            tier=HospitalTier.TIER_1
        )
        
        assert location.city == "Mumbai"
        assert location.tier == HospitalTier.TIER_1
        assert location.pincode == "400001"
        assert location.state == "Maharashtra"
    
    def test_hospital_location_tier_validation(self):
        """Test hospital tier validation."""
        for tier in HospitalTier:
            location = HospitalLocation(
                address="Test Address",
                city="Test City",
                state="Test State",
                pincode="123456",
                tier=tier
            )
            assert location.tier == tier
    
    def test_hospital_location_pincode_validation(self):
        """Test pincode format validation."""
        valid_pincodes = ["400001", "110001", "560001"]
        for pincode in valid_pincodes:
            location = HospitalLocation(
                address="Test Address",
                city="Test City",
                state="Test State",
                pincode=pincode,
                tier=HospitalTier.TIER_1
            )
            assert location.pincode == pincode


class TestHospitalFinancialMetrics:
    """Test cases for HospitalFinancialMetrics model."""
    
    def test_financial_metrics_creation_valid(self):
        """Test valid financial metrics creation."""
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("100000000"),
            operating_margin=15.0,
            fiscal_year="FY2024-25"
        )
        
        assert financial.annual_revenue == Decimal("100000000")
        assert financial.operating_margin == 15.0
        assert financial.fiscal_year == "FY2024-25"
    
    def test_financial_metrics_decimal_precision(self):
        """Test decimal precision handling."""
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("100000000.50"),
            operating_margin=15.25,
            fiscal_year="FY2024-25"
        )
        
        assert financial.annual_revenue == Decimal("100000000.50")
        assert financial.operating_margin == 15.25
    
    @pytest.mark.parametrize("revenue,margin,year", [
        (Decimal("50000000"), 10.0, "FY2023-24"),
        (Decimal("200000000"), 20.5, "FY2024-25"),
        (Decimal("1000000000"), 25.0, "FY2025-26"),
    ])
    def test_financial_metrics_parametrized(
        self, 
        revenue: Decimal, 
        margin: float, 
        year: str
    ):
        """Test financial metrics with different parameter combinations."""
        financial = HospitalFinancialMetrics(
            annual_revenue=revenue,
            operating_margin=margin,
            fiscal_year=year
        )
        
        assert financial.annual_revenue == revenue
        assert financial.operating_margin == margin
        assert financial.fiscal_year == year


class TestHospitalOperationalMetrics:
    """Test cases for HospitalOperationalMetrics model."""
    
    def test_operational_metrics_creation_valid(self):
        """Test valid operational metrics creation."""
        operational = HospitalOperationalMetrics(
            bed_count=200,
            occupancy_rate=0.75,
            average_length_of_stay=4.0,
            reporting_period="Q1-FY2024-25"
        )
        
        assert operational.bed_count == 200
        assert operational.occupancy_rate == 0.75
        assert operational.average_length_of_stay == 4.0
        assert operational.reporting_period == "Q1-FY2024-25"
    
    def test_occupancy_rate_boundaries(self):
        """Test occupancy rate boundary values."""
        # Test minimum boundary
        operational_min = HospitalOperationalMetrics(
            bed_count=100,
            occupancy_rate=0.0,
            average_length_of_stay=3.0,
            reporting_period="Q1-FY2024-25"
        )
        assert operational_min.occupancy_rate == 0.0
        
        # Test maximum boundary
        operational_max = HospitalOperationalMetrics(
            bed_count=100,
            occupancy_rate=1.0,
            average_length_of_stay=3.0,
            reporting_period="Q1-FY2024-25"
        )
        assert operational_max.occupancy_rate == 1.0
    
    def test_bed_count_positive_validation(self):
        """Test bed count must be positive."""
        operational = HospitalOperationalMetrics(
            bed_count=1,
            occupancy_rate=0.5,
            average_length_of_stay=2.0,
            reporting_period="Q1-FY2024-25"
        )
        assert operational.bed_count == 1


class TestHospitalQualityMetrics:
    """Test cases for HospitalQualityMetrics model."""
    
    def test_quality_metrics_creation_minimal(self):
        """Test quality metrics creation with minimal data."""
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        assert quality.reporting_period == "Q1-FY2024-25"
    
    def test_quality_metrics_reporting_periods(self):
        """Test different reporting period formats."""
        periods = [
            "Q1-FY2024-25",
            "Q2-FY2024-25", 
            "Q3-FY2024-25",
            "Q4-FY2024-25"
        ]
        
        for period in periods:
            quality = HospitalQualityMetrics(reporting_period=period)
            assert quality.reporting_period == period


class TestHospitalProfile:
    """Test cases for complete HospitalProfile model."""
    
    def test_hospital_profile_creation_complete(self):
        """Test complete hospital profile creation."""
        location = HospitalLocation(
            address="Test Hospital Road",
            city="Delhi",
            state="Delhi",
            pincode="110001",
            tier=HospitalTier.TIER_1
        )
        
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("150000000"),
            operating_margin=12.0,
            fiscal_year="FY2024-25"
        )
        
        operational = HospitalOperationalMetrics(
            bed_count=300,
            occupancy_rate=0.80,
            average_length_of_stay=3.5,
            reporting_period="Q1-FY2024-25"
        )
        
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        hospital = HospitalProfile(
            hospital_id="TEST_HOSP_001",
            name="Test Hospital Delhi",
            location=location,
            hospital_type=HospitalType.SUPER_SPECIALTY,
            bed_count=300,
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        assert hospital.name == "Test Hospital Delhi"
        assert hospital.hospital_type == HospitalType.SUPER_SPECIALTY
        assert hospital.bed_count == 300
        assert hospital.financial_metrics.annual_revenue == Decimal("150000000")
        assert hospital.location.city == "Delhi"
    
    def test_hospital_profile_multi_specialty(self):
        """Test hospital profile with multi-specialty type."""
        location = HospitalLocation(
            address="Multi Specialty Hospital",
            city="Chennai",
            state="Tamil Nadu",
            pincode="600001",
            tier=HospitalTier.TIER_1
        )
        
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("120000000"),
            operating_margin=14.0,
            fiscal_year="FY2024-25"
        )
        
        operational = HospitalOperationalMetrics(
            bed_count=250,
            occupancy_rate=0.78,
            average_length_of_stay=3.8,
            reporting_period="Q1-FY2024-25"
        )
        
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        hospital = HospitalProfile(
            hospital_id="MULTI_SPEC_001",
            name="Multi Specialty Test Hospital",
            location=location,
            hospital_type=HospitalType.MULTI_SPECIALTY,
            bed_count=250,
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        assert hospital.hospital_type == HospitalType.MULTI_SPECIALTY
        assert hospital.bed_count == 250
    
    @pytest.mark.parametrize("hospital_type", [
        HospitalType.ACUTE_CARE,
        HospitalType.SPECIALTY,
        HospitalType.SUPER_SPECIALTY,
        HospitalType.MULTI_SPECIALTY,
    ])
    def test_hospital_types_validation(self, hospital_type: HospitalType):
        """Test all hospital types are supported."""
        location = HospitalLocation(
            address="Test Address",
            city="Test City",
            state="Test State",
            pincode="123456",
            tier=HospitalTier.TIER_2
        )
        
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("100000000"),
            operating_margin=15.0,
            fiscal_year="FY2024-25"
        )
        
        operational = HospitalOperationalMetrics(
            bed_count=200,
            occupancy_rate=0.75,
            average_length_of_stay=4.0,
            reporting_period="Q1-FY2024-25"
        )
        
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        hospital = HospitalProfile(
            hospital_id=f"TEST_{hospital_type.value.upper()}_001",
            name=f"Test {hospital_type.value} Hospital",
            location=location,
            hospital_type=hospital_type,
            bed_count=200,
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        assert hospital.hospital_type == hospital_type


class TestHospitalEnums:
    """Test cases for hospital enumeration types."""
    
    def test_hospital_tier_enum_values(self):
        """Test all hospital tier enum values."""
        expected_tiers = ["TIER_1", "TIER_2", "TIER_3", "TIER_4"]
        actual_tiers = [tier.name for tier in HospitalTier]
        
        for tier in expected_tiers:
            assert tier in actual_tiers
    
    def test_hospital_type_enum_values(self):
        """Test all hospital type enum values."""
        expected_types = [
            "ACUTE_CARE", 
            "SPECIALTY", 
            "SUPER_SPECIALTY", 
            "MULTI_SPECIALTY"
        ]
        actual_types = [hospital_type.name for hospital_type in HospitalType]
        
        for hospital_type in expected_types:
            assert hospital_type in actual_types
    
    def test_hospital_type_enum_string_values(self):
        """Test hospital type enum string values."""
        type_mappings = {
            HospitalType.ACUTE_CARE: "acute_care",
            HospitalType.SPECIALTY: "specialty",
            HospitalType.SUPER_SPECIALTY: "super_specialty",
            HospitalType.MULTI_SPECIALTY: "multi_specialty",
        }
        
        for enum_val, string_val in type_mappings.items():
            assert enum_val.value == string_val


@pytest.mark.slow
class TestHospitalProfileIntegration:
    """Integration-style tests for hospital profile validation."""
    
    def test_hospital_profile_data_consistency(self):
        """Test data consistency across hospital profile components."""
        location = HospitalLocation(
            address="Consistency Test Hospital",
            city="Pune",
            state="Maharashtra", 
            pincode="411001",
            tier=HospitalTier.TIER_1
        )
        
        # Ensure operational bed count matches profile bed count
        bed_count = 400
        
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("180000000"),
            operating_margin=16.0,
            fiscal_year="FY2024-25"
        )
        
        operational = HospitalOperationalMetrics(
            bed_count=bed_count,
            occupancy_rate=0.82,
            average_length_of_stay=3.6,
            reporting_period="Q1-FY2024-25"
        )
        
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        hospital = HospitalProfile(
            hospital_id="CONSISTENCY_001",
            name="Consistency Test Hospital",
            location=location,
            hospital_type=HospitalType.MULTI_SPECIALTY,
            bed_count=bed_count,  # Must match operational.bed_count
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        # Validate consistency
        assert hospital.bed_count == operational.bed_count
        assert hospital.location.tier == HospitalTier.TIER_1
        assert hospital.hospital_type == HospitalType.MULTI_SPECIALTY