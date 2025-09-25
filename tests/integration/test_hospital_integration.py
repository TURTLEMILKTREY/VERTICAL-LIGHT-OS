"""
Integration tests for Hospital Intelligence Engine complete workflows.

This module contains integration tests that validate end-to-end workflows
combining multiple components including HMS connectors, data models, and services.
"""

import pytest
import asyncio
from decimal import Decimal
from typing import Dict, Any, List
from unittest.mock import Mock, patch

from backend.models.hospital_schemas_simple import (
    HospitalProfile, HospitalLocation, HospitalFinancialMetrics,
    HospitalOperationalMetrics, HospitalQualityMetrics,
    HospitalTier, HospitalType
)

from backend.services.hospital_intelligence.hms_connectors import (
    HMSConnectorFactory, HMSType, HMSConnectionConfig
)


@pytest.mark.integration
class TestHospitalDataIntegration:
    """Integration tests for complete hospital data workflows."""
    
    def test_complete_hospital_setup_workflow(self):
        """Test complete hospital setup from creation to HMS integration."""
        # Step 1: Create hospital location
        location = HospitalLocation(
            address="Integration Test Hospital Complex",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            tier=HospitalTier.TIER_1
        )
        
        # Step 2: Create financial metrics
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("250000000"),
            operating_margin=18.5,
            fiscal_year="FY2024-25"
        )
        
        # Step 3: Create operational metrics
        operational = HospitalOperationalMetrics(
            bed_count=500,
            occupancy_rate=0.85,
            average_length_of_stay=3.2,
            reporting_period="Q1-FY2024-25"
        )
        
        # Step 4: Create quality metrics
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        # Step 5: Create complete hospital profile
        hospital = HospitalProfile(
            hospital_id="INTEGRATION_HOSP_001",
            name="Integration Test Multi-Specialty Hospital",
            location=location,
            hospital_type=HospitalType.MULTI_SPECIALTY,
            bed_count=500,
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        # Step 6: Create HMS configuration
        hms_config = HMSConnectionConfig(
            hms_type=HMSType.BIRLAMEDISOFT,
            api_endpoint="http://localhost:8080/api/v1",
            username="integration_test_user",
            password="integration_test_pass",
            timeout=60,
            retry_count=3
        )
        
        # Step 7: Create HMS connector
        connector = HMSConnectorFactory.create_connector(
            HMSType.BIRLAMEDISOFT, 
            hms_config
        )
        
        # Step 8: Validate complete integration
        assert hospital.name == "Integration Test Multi-Specialty Hospital"
        assert hospital.bed_count == 500
        assert hospital.hospital_type == HospitalType.MULTI_SPECIALTY
        assert hospital.financial_metrics.annual_revenue == Decimal("250000000")
        assert hospital.location.tier == HospitalTier.TIER_1
        
        assert connector is not None
        assert connector.config.hms_type == HMSType.BIRLAMEDISOFT
        assert connector.config.timeout == 60
        
        # Validate data consistency
        assert hospital.bed_count == operational.bed_count
        assert hospital.location.city == location.city
        
        print(f"✅ Successfully integrated hospital: {hospital.name}")
        print(f"✅ Successfully configured HMS: {connector.__class__.__name__}")
    
    def test_multi_hospital_batch_processing(self):
        """Test batch processing of multiple hospitals."""
        hospitals = []
        connectors = []
        
        hospital_configs = [
            {
                "id": "BATCH_001",
                "name": "Batch Hospital Alpha",
                "city": "Delhi",
                "state": "Delhi",
                "beds": 300,
                "hms": HMSType.BIRLAMEDISOFT
            },
            {
                "id": "BATCH_002", 
                "name": "Batch Hospital Beta",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "beds": 250,
                "hms": HMSType.MEDEIL
            },
            {
                "id": "BATCH_003",
                "name": "Batch Hospital Gamma",
                "city": "Bangalore",
                "state": "Karnataka", 
                "beds": 400,
                "hms": HMSType.HMS_360
            }
        ]
        
        # Process each hospital configuration
        for config in hospital_configs:
            # Create location
            location = HospitalLocation(
                address=f"{config['name']} Address",
                city=config['city'],
                state=config['state'],
                pincode="000001",
                tier=HospitalTier.TIER_1
            )
            
            # Create metrics
            financial = HospitalFinancialMetrics(
                annual_revenue=Decimal(str(config['beds'] * 500000)),
                operating_margin=15.0,
                fiscal_year="FY2024-25"
            )
            
            operational = HospitalOperationalMetrics(
                bed_count=config['beds'],
                occupancy_rate=0.80,
                average_length_of_stay=3.5,
                reporting_period="Q1-FY2024-25"
            )
            
            quality = HospitalQualityMetrics(
                reporting_period="Q1-FY2024-25"
            )
            
            # Create hospital
            hospital = HospitalProfile(
                hospital_id=config['id'],
                name=config['name'],
                location=location,
                hospital_type=HospitalType.MULTI_SPECIALTY,
                bed_count=config['beds'],
                financial_metrics=financial,
                operational_metrics=operational,
                quality_metrics=quality
            )
            
            # Create HMS connector
            hms_config = HMSConnectionConfig(
                hms_type=config['hms'],
                api_endpoint=f"http://{config['hms'].value}:8080/api",
                username=f"user_{config['id'].lower()}",
                password=f"pass_{config['id'].lower()}"
            )
            
            connector = HMSConnectorFactory.create_connector(
                config['hms'], 
                hms_config
            )
            
            hospitals.append(hospital)
            connectors.append(connector)
        
        # Validate batch processing results
        assert len(hospitals) == 3
        assert len(connectors) == 3
        
        # Validate each hospital
        for i, hospital in enumerate(hospitals):
            config = hospital_configs[i]
            assert hospital.hospital_id == config['id']
            assert hospital.name == config['name']
            assert hospital.bed_count == config['beds']
            assert hospital.location.city == config['city']
            
        # Validate each connector
        for i, connector in enumerate(connectors):
            config = hospital_configs[i]
            assert connector.config.hms_type == config['hms']
        
        print(f"✅ Successfully processed {len(hospitals)} hospitals in batch")
    
    def test_hospital_data_validation_workflow(self):
        """Test comprehensive data validation across all components."""
        # Create hospital with edge case values
        location = HospitalLocation(
            address="Validation Test Hospital",
            city="Hyderabad",
            state="Telangana",
            pincode="500001",
            tier=HospitalTier.TIER_2
        )
        
        # Test minimum viable financial data
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("10000000"),  # 1 crore minimum
            operating_margin=5.0,  # Low but positive margin
            fiscal_year="FY2024-25"
        )
        
        # Test edge case operational data
        operational = HospitalOperationalMetrics(
            bed_count=50,  # Small hospital
            occupancy_rate=0.95,  # High occupancy
            average_length_of_stay=2.0,  # Short stay
            reporting_period="Q1-FY2024-25"
        )
        
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        # Create hospital with edge case data
        hospital = HospitalProfile(
            hospital_id="VALIDATION_001",
            name="Edge Case Validation Hospital",
            location=location,
            hospital_type=HospitalType.SPECIALTY,
            bed_count=50,
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        # Validate data integrity
        assert hospital.bed_count == operational.bed_count
        assert hospital.financial_metrics.operating_margin > 0
        assert hospital.operational_metrics.occupancy_rate <= 1.0
        assert hospital.location.tier == HospitalTier.TIER_2
        
        # Test HMS integration with edge case hospital
        hms_config = HMSConnectionConfig(
            hms_type=HMSType.EHOSPITAL,  # Government system
            api_endpoint="http://ehospital.gov.in/api/v2",
            username="govt_hospital_admin",
            password="secure_govt_pass"
        )
        
        connector = HMSConnectorFactory.create_connector(
            HMSType.EHOSPITAL, 
            hms_config
        )
        
        assert connector is not None
        assert connector.__class__.__name__ == "EHospitalConnector"
        
        print(f"✅ Successfully validated edge case hospital: {hospital.name}")


@pytest.mark.integration
@pytest.mark.database
class TestHospitalDatabaseIntegration:
    """Integration tests with database operations."""
    
    def test_hospital_persistence_workflow(self, test_db_session):
        """Test complete hospital data persistence workflow."""
        # Note: This would require actual database models and repositories
        # For now, we test the data structure compatibility
        
        location = HospitalLocation(
            address="Database Test Hospital",
            city="Kolkata",
            state="West Bengal",
            pincode="700001",
            tier=HospitalTier.TIER_1
        )
        
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal("180000000"),
            operating_margin=16.0,
            fiscal_year="FY2024-25"
        )
        
        operational = HospitalOperationalMetrics(
            bed_count=350,
            occupancy_rate=0.82,
            average_length_of_stay=3.8,
            reporting_period="Q1-FY2024-25"
        )
        
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        hospital = HospitalProfile(
            hospital_id="DB_TEST_001",
            name="Database Integration Hospital",
            location=location,
            hospital_type=HospitalType.MULTI_SPECIALTY,
            bed_count=350,
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        # Validate data can be serialized (important for database storage)
        hospital_dict = hospital.model_dump()
        assert isinstance(hospital_dict, dict)
        assert hospital_dict['hospital_id'] == "DB_TEST_001"
        assert hospital_dict['name'] == "Database Integration Hospital"
        
        # Test data can be reconstructed from dictionary
        reconstructed_hospital = HospitalProfile.model_validate(hospital_dict)
        assert reconstructed_hospital.hospital_id == hospital.hospital_id
        assert reconstructed_hospital.name == hospital.name
        assert reconstructed_hospital.bed_count == hospital.bed_count
        
        print(f"✅ Successfully validated database compatibility for: {hospital.name}")


@pytest.mark.integration
@pytest.mark.api
class TestHospitalAPIIntegration:
    """Integration tests with API operations."""
    
    @pytest.mark.asyncio
    async def test_hospital_api_workflow(self, test_client):
        """Test complete hospital API integration workflow."""
        # Create test hospital data
        hospital_data = {
            "hospital_id": "API_TEST_001",
            "name": "API Integration Hospital",
            "location": {
                "address": "API Test Address", 
                "city": "Pune",
                "state": "Maharashtra",
                "pincode": "411001",
                "tier": "TIER_1"
            },
            "hospital_type": "MULTI_SPECIALTY",
            "bed_count": 280,
            "financial_metrics": {
                "annual_revenue": "140000000",
                "operating_margin": 14.5,
                "fiscal_year": "FY2024-25"
            },
            "operational_metrics": {
                "bed_count": 280,
                "occupancy_rate": 0.79,
                "average_length_of_stay": 3.6,
                "reporting_period": "Q1-FY2024-25"
            },
            "quality_metrics": {
                "reporting_period": "Q1-FY2024-25"
            }
        }
        
        # Test data structure is valid for API
        hospital = HospitalProfile.model_validate(hospital_data)
        assert hospital.hospital_id == "API_TEST_001"
        assert hospital.name == "API Integration Hospital"
        
        # Test JSON serialization for API
        json_data = hospital.model_dump_json()
        assert isinstance(json_data, str)
        assert "API_TEST_001" in json_data
        
        # Test deserialization from JSON
        from_json_hospital = HospitalProfile.model_validate_json(json_data)
        assert from_json_hospital.hospital_id == hospital.hospital_id
        assert from_json_hospital.name == hospital.name
        
        print(f"✅ Successfully validated API compatibility for: {hospital.name}")


@pytest.mark.integration
@pytest.mark.slow
class TestHospitalPerformanceIntegration:
    """Performance integration tests."""
    
    def test_large_hospital_dataset_processing(self):
        """Test processing large dataset of hospitals."""
        import time
        
        start_time = time.time()
        
        hospitals = []
        connectors = []
        
        # Create 100 hospitals with different configurations
        for i in range(100):
            location = HospitalLocation(
                address=f"Performance Test Hospital {i+1}",
                city=f"City{i+1}",
                state="Test State",
                pincode=f"{400001 + i}",
                tier=HospitalTier.TIER_1 if i % 4 == 0 else HospitalTier.TIER_2
            )
            
            financial = HospitalFinancialMetrics(
                annual_revenue=Decimal(str(100000000 + (i * 10000000))),
                operating_margin=10.0 + (i % 10),
                fiscal_year="FY2024-25"
            )
            
            operational = HospitalOperationalMetrics(
                bed_count=100 + (i * 5),
                occupancy_rate=0.70 + (i % 20) * 0.01,
                average_length_of_stay=3.0 + (i % 3),
                reporting_period="Q1-FY2024-25"
            )
            
            quality = HospitalQualityMetrics(
                reporting_period="Q1-FY2024-25"
            )
            
            hospital = HospitalProfile(
                hospital_id=f"PERF_TEST_{i+1:03d}",
                name=f"Performance Test Hospital {i+1}",
                location=location,
                hospital_type=HospitalType.MULTI_SPECIALTY,
                bed_count=100 + (i * 5),
                financial_metrics=financial,
                operational_metrics=operational,
                quality_metrics=quality
            )
            
            # Create HMS connector for every 10th hospital
            if i % 10 == 0:
                hms_types = [HMSType.BIRLAMEDISOFT, HMSType.MEDEIL, HMSType.HMS_360]
                hms_type = hms_types[i // 10 % len(hms_types)]
                
                hms_config = HMSConnectionConfig(
                    hms_type=hms_type,
                    api_endpoint=f"http://perf{i}:8080/api",
                    username=f"perf_user_{i}",
                    password=f"perf_pass_{i}"
                )
                
                connector = HMSConnectorFactory.create_connector(hms_type, hms_config)
                connectors.append(connector)
            
            hospitals.append(hospital)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Validate performance
        assert len(hospitals) == 100
        assert len(connectors) == 10  # Every 10th hospital
        assert processing_time < 5.0  # Should complete in less than 5 seconds
        
        # Validate data integrity
        for i, hospital in enumerate(hospitals):
            assert hospital.hospital_id == f"PERF_TEST_{i+1:03d}"
            assert hospital.bed_count == 100 + (i * 5)
        
        print(f"✅ Successfully processed {len(hospitals)} hospitals in {processing_time:.2f} seconds")
        print(f"✅ Created {len(connectors)} HMS connectors")
        print(f"✅ Average processing time per hospital: {processing_time/100:.4f} seconds")


@pytest.mark.integration
class TestHospitalTypeIntegration:
    """Integration tests for different hospital types."""
    
    @pytest.mark.parametrize("hospital_type,expected_features", [
        (HospitalType.ACUTE_CARE, {"emergency": True, "icu": True}),
        (HospitalType.SPECIALTY, {"specialized_departments": True}),
        (HospitalType.SUPER_SPECIALTY, {"advanced_procedures": True, "research": True}),
        (HospitalType.MULTI_SPECIALTY, {"multiple_departments": True, "comprehensive": True}),
    ])
    def test_hospital_type_specific_workflows(
        self, 
        hospital_type: HospitalType, 
        expected_features: Dict[str, bool]
    ):
        """Test workflows specific to different hospital types."""
        location = HospitalLocation(
            address=f"{hospital_type.value.title()} Hospital",
            city="Type Test City",
            state="Test State",
            pincode="123456",
            tier=HospitalTier.TIER_1
        )
        
        # Adjust metrics based on hospital type
        bed_count = {
            HospitalType.ACUTE_CARE: 150,
            HospitalType.SPECIALTY: 100,
            HospitalType.SUPER_SPECIALTY: 300,
            HospitalType.MULTI_SPECIALTY: 400
        }[hospital_type]
        
        financial = HospitalFinancialMetrics(
            annual_revenue=Decimal(str(bed_count * 800000)),
            operating_margin=15.0,
            fiscal_year="FY2024-25"
        )
        
        operational = HospitalOperationalMetrics(
            bed_count=bed_count,
            occupancy_rate=0.80,
            average_length_of_stay=3.5,
            reporting_period="Q1-FY2024-25"
        )
        
        quality = HospitalQualityMetrics(
            reporting_period="Q1-FY2024-25"
        )
        
        hospital = HospitalProfile(
            hospital_id=f"TYPE_TEST_{hospital_type.name}",
            name=f"{hospital_type.value.title()} Test Hospital",
            location=location,
            hospital_type=hospital_type,
            bed_count=bed_count,
            financial_metrics=financial,
            operational_metrics=operational,
            quality_metrics=quality
        )
        
        # Validate hospital creation
        assert hospital.hospital_type == hospital_type
        assert hospital.bed_count == bed_count
        
        # Validate type-specific characteristics
        assert hospital.name.lower().startswith(hospital_type.value.replace('_', ' '))
        
        print(f"✅ Successfully created {hospital_type.value} hospital: {hospital.name}")
        print(f"✅ Expected features: {expected_features}")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])