"""
Test Suite for Hospital Intelligence Engine
Production-level testing framework
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime

# Test imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.hospital_schemas_simple import (
    HospitalProfile, HospitalLocation, HospitalFinancialMetrics,
    HospitalOperationalMetrics, HospitalQualityMetrics,
    HospitalTier, HospitalType
)

from services.hospital_intelligence.hms_connectors import (
    HMSConnectorFactory, HMSType, HMSConnectionConfig
)

class TestHospitalSchemas:
    """Test hospital data models"""
    
    def test_hospital_location_creation(self):
        """Test hospital location model"""
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
    
    def test_financial_metrics_creation(self):
        """Test financial metrics model"""
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("100000000"),
            operating_margin=15.0,
            fiscal_year="FY2024-25"
        )
        
        assert financial.annual_revenue == Decimal("100000000")
        assert financial.operating_margin == 15.0
        assert financial.fiscal_year == "FY2024-25"
    
    def test_operational_metrics_creation(self):
        """Test operational metrics model"""
        operational = HospitalOperationalMetrics(
            bed_count=200,
            occupancy_rate=0.75,
            average_length_of_stay=4.0,
            reporting_period="Q1-FY2024-25"
        )
        
        assert operational.bed_count == 200
        assert operational.occupancy_rate == 0.75
        assert operational.reporting_period == "Q1-FY2024-25"
    
    def test_quality_metrics_creation(self):
        """Test quality metrics model"""
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        assert quality.reporting_period == "Q1-FY2024-25"
    
    def test_complete_hospital_profile(self):
        """Test complete hospital profile creation"""
        # Create location
        location = HospitalLocation(
            address="Test Hospital Road",
            city="Delhi",
            state="Delhi",
            pincode="110001",
            tier=HospitalTier.TIER_1
        )
        
        # Create metrics
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
        
        # Create hospital profile
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

class TestHMSConnectors:
    """Test HMS connector functionality"""
    
    def test_birlamedisoft_connector_creation(self):
        """Test Birlamedisoft connector creation"""
        config = HMSConnectionConfig(
            hms_type=HMSType.BIRLAMEDISOFT,
            api_endpoint="http://localhost:8080/api",
            username="test_user",
            password="test_pass"
        )
        
        connector = HMSConnectorFactory.create_connector(HMSType.BIRLAMEDISOFT, config)
        assert connector is not None
        assert connector.__class__.__name__ == "BirlamedisoftConnector"
    
    def test_medeil_connector_creation(self):
        """Test Medeil connector creation"""
        config = HMSConnectionConfig(
            hms_type=HMSType.MEDEIL,
            api_endpoint="http://localhost:3000/api",
            username="medeil_user",
            password="medeil_pass"
        )
        
        connector = HMSConnectorFactory.create_connector(HMSType.MEDEIL, config)
        assert connector is not None
        assert connector.__class__.__name__ == "MedeilConnector"
    
    def test_ehospital_connector_creation(self):
        """Test eHospital connector creation"""
        config = HMSConnectionConfig(
            hms_type=HMSType.EHOSPITAL,
            api_endpoint="http://ehospital.gov.in/api",
            username="hospital_admin",
            password="govt_pass"
        )
        
        connector = HMSConnectorFactory.create_connector(HMSType.EHOSPITAL, config)
        assert connector is not None
        assert connector.__class__.__name__ == "EHospitalConnector"
    
    def test_unsupported_hms_type(self):
        """Test unsupported HMS type handling"""
        config = HMSConnectionConfig(
            hms_type=HMSType.EPIC,
            api_endpoint="http://localhost:9000/api",
            username="epic_user",
            password="epic_pass"
        )
        
        with pytest.raises(ValueError, match="Unsupported HMS type"):
            HMSConnectorFactory.create_connector(HMSType.EPIC, config)

class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_end_to_end_hospital_creation(self):
        """Test complete hospital setup workflow"""
        # Step 1: Create hospital profile
        location = HospitalLocation(
            address="Integration Test Hospital",
            city="Bangalore",
            state="Karnataka",
            pincode="560001",
            tier=HospitalTier.TIER_1
        )
        
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("200000000"),
            operating_margin=18.0,
            fiscal_year="FY2024-25"
        )
        
        operational = HospitalOperationalMetrics(
            bed_count=400,
            occupancy_rate=0.85,
            average_length_of_stay=3.2,
            reporting_period="Q1-FY2024-25"
        )
        
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        hospital = HospitalProfile(
            hospital_id="INTEGRATION_TEST_001",
            name="Integration Test Hospital",
            location=location,
            hospital_type=HospitalType.MULTI_SPECIALTY,
            bed_count=400,
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        # Step 2: Create HMS connector
        hms_config = HMSConnectionConfig(
            hms_type=HMSType.BIRLAMEDISOFT,
            api_endpoint="http://localhost:8080/api",
            username="integration_user",
            password="integration_pass"
        )
        
        connector = HMSConnectorFactory.create_connector(HMSType.BIRLAMEDISOFT, hms_config)
        
        # Step 3: Verify integration
        assert hospital.name == "Integration Test Hospital"
        assert hospital.bed_count == 400
        assert connector is not None
        
        # This demonstrates the complete setup workflow
        print(f"✅ Successfully created hospital: {hospital.name}")
        print(f"✅ Successfully created HMS connector: {connector.__class__.__name__}")

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])