"""
Unit tests for HMS (Hospital Management System) connectors.

This module contains comprehensive unit tests for HMS connector factory,
connection management, and individual connector implementations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from backend.services.hospital_intelligence.hms_connectors import (
 HMSConnectorFactory, HMSType, HMSConnectionConfig,
 BaseHMSConnector
)


class TestHMSConnectionConfig:
 """Test cases for HMS connection configuration."""

 def test_hms_connection_config_creation(self):
 """Test HMS connection config creation with required fields."""
 config = HMSConnectionConfig(
 hms_type=HMSType.BIRLAMEDISOFT,
 api_endpoint="http://localhost:8080/api",
 username="test_user",
 password="test_pass"
 )

 assert config.hms_type == HMSType.BIRLAMEDISOFT
 assert config.api_endpoint == "http://localhost:8080/api"
 assert config.username == "test_user"
 assert config.password == "test_pass"

 def test_hms_connection_config_optional_fields(self):
 """Test HMS connection config with optional fields."""
 config = HMSConnectionConfig(
 hms_type=HMSType.MEDEIL,
 api_endpoint="http://localhost:3000/api",
 username="medeil_user",
 password="medeil_pass",
 timeout=60,
 retry_count=3,
 ssl_verify=False
 )

 assert config.timeout == 60
 assert config.retry_count == 3
 assert config.ssl_verify is False

 @pytest.mark.parametrize("hms_type,endpoint", [
 (HMSType.BIRLAMEDISOFT, "http://birla:8080/api"),
 (HMSType.MEDEIL, "http://medeil:3000/api"),
 (HMSType.EHOSPITAL, "http://ehospital.gov.in/api"),
 (HMSType.HMS_360, "http://hms360:9000/api"),
 ])
 def test_hms_types_configuration(self, hms_type: HMSType, endpoint: str):
 """Test configuration for different HMS types."""
 config = HMSConnectionConfig(
 hms_type=hms_type,
 api_endpoint=endpoint,
 username="test_user",
 password="test_pass"
 )

 assert config.hms_type == hms_type
 assert config.api_endpoint == endpoint


class TestHMSConnectorFactory:
 """Test cases for HMS connector factory."""

 def test_birlamedisoft_connector_creation(self):
 """Test Birlamedisoft connector creation."""
 config = HMSConnectionConfig(
 hms_type=HMSType.BIRLAMEDISOFT,
 api_endpoint="http://localhost:8080/api",
 username="test_user",
 password="test_pass"
 )

 connector = HMSConnectorFactory.create_connector(
 HMSType.BIRLAMEDISOFT, 
 config
 )

 assert connector is not None
 assert connector.__class__.__name__ == "BirlamedisoftConnector"
 assert hasattr(connector, 'connect')
 assert hasattr(connector, 'disconnect')
 assert hasattr(connector, 'get_patient_data')

 def test_medeil_connector_creation(self):
 """Test Medeil connector creation."""
 config = HMSConnectionConfig(
 hms_type=HMSType.MEDEIL,
 api_endpoint="http://localhost:3000/api",
 username="medeil_user",
 password="medeil_pass"
 )

 connector = HMSConnectorFactory.create_connector(
 HMSType.MEDEIL, 
 config
 )

 assert connector is not None
 assert connector.__class__.__name__ == "MedeilConnector"
 assert hasattr(connector, 'connect')
 assert hasattr(connector, 'get_billing_data')

 def test_ehospital_connector_creation(self):
 """Test eHospital connector creation."""
 config = HMSConnectionConfig(
 hms_type=HMSType.EHOSPITAL,
 api_endpoint="http://ehospital.gov.in/api",
 username="hospital_admin",
 password="govt_pass"
 )

 connector = HMSConnectorFactory.create_connector(
 HMSType.EHOSPITAL, 
 config
 )

 assert connector is not None
 assert connector.__class__.__name__ == "EHospitalConnector"
 assert hasattr(connector, 'connect')
 assert hasattr(connector, 'get_government_schemes_data')

 def test_hms360_connector_creation(self):
 """Test HMS 360 connector creation."""
 config = HMSConnectionConfig(
 hms_type=HMSType.HMS_360,
 api_endpoint="http://localhost:9000/api",
 username="hms360_user",
 password="hms360_pass"
 )

 connector = HMSConnectorFactory.create_connector(
 HMSType.HMS_360, 
 config
 )

 assert connector is not None
 assert connector.__class__.__name__ == "HMS360Connector"

 def test_unsupported_hms_type_raises_error(self):
 """Test that unsupported HMS type raises ValueError."""
 config = HMSConnectionConfig(
 hms_type=HMSType.EPIC, # Unsupported type
 api_endpoint="http://localhost:9000/api",
 username="epic_user",
 password="epic_pass"
 )

 with pytest.raises(ValueError, match="Unsupported HMS type"):
 HMSConnectorFactory.create_connector(HMSType.EPIC, config)

 def test_factory_creates_different_instances(self):
 """Test that factory creates different instances for each call."""
 config = HMSConnectionConfig(
 hms_type=HMSType.BIRLAMEDISOFT,
 api_endpoint="http://localhost:8080/api",
 username="test_user",
 password="test_pass"
 )

 connector1 = HMSConnectorFactory.create_connector(
 HMSType.BIRLAMEDISOFT, 
 config
 )
 connector2 = HMSConnectorFactory.create_connector(
 HMSType.BIRLAMEDISOFT, 
 config
 )

 assert connector1 is not connector2
 assert type(connector1) == type(connector2)


class TestBaseHMSConnector:
 """Test cases for base HMS connector functionality."""

 @pytest.fixture
 def mock_connector(self) -> BaseHMSConnector:
 """Create mock HMS connector for testing."""
 config = HMSConnectionConfig(
 hms_type=HMSType.BIRLAMEDISOFT,
 api_endpoint="http://test:8080/api",
 username="test",
 password="test"
 )

 # Create a concrete implementation for testing
 class TestConnector(BaseHMSConnector):
 def connect(self) -> bool:
 return True

 def disconnect(self) -> bool:
 return True

 def get_patient_data(self) -> Dict[str, Any]:
 return {"patients": []}

 def get_billing_data(self) -> Dict[str, Any]:
 return {"bills": []}

 return TestConnector(config)

 def test_connector_initialization(self, mock_connector: BaseHMSConnector):
 """Test connector initialization with config."""
 assert mock_connector.config is not None
 assert mock_connector.config.hms_type == HMSType.BIRLAMEDISOFT
 assert not mock_connector.is_connected

 def test_connector_connection_lifecycle(self, mock_connector: BaseHMSConnector):
 """Test connector connection and disconnection."""
 # Initially not connected
 assert not mock_connector.is_connected

 # Connect should return True
 result = mock_connector.connect()
 assert result is True

 # Should now be connected
 assert mock_connector.is_connected

 # Disconnect should return True
 result = mock_connector.disconnect()
 assert result is True

 # Should no longer be connected
 assert not mock_connector.is_connected

 def test_connector_data_retrieval_methods(self, mock_connector: BaseHMSConnector):
 """Test data retrieval methods exist and return expected format."""
 # Test patient data retrieval
 patient_data = mock_connector.get_patient_data()
 assert isinstance(patient_data, dict)
 assert "patients" in patient_data

 # Test billing data retrieval
 billing_data = mock_connector.get_billing_data()
 assert isinstance(billing_data, dict)
 assert "bills" in billing_data


class TestHMSConnectorIntegration:
 """Integration tests for HMS connector workflows."""

 def test_complete_connector_workflow(self):
 """Test complete HMS connector usage workflow."""
 # Step 1: Create configuration
 config = HMSConnectionConfig(
 hms_type=HMSType.BIRLAMEDISOFT,
 api_endpoint="http://integration-test:8080/api",
 username="integration_user",
 password="integration_pass",
 timeout=30,
 retry_count=2
 )

 # Step 2: Create connector
 connector = HMSConnectorFactory.create_connector(
 HMSType.BIRLAMEDISOFT, 
 config
 )

 # Step 3: Verify connector properties
 assert connector is not None
 assert connector.config.hms_type == HMSType.BIRLAMEDISOFT
 assert connector.config.timeout == 30
 assert connector.config.retry_count == 2

 # Step 4: Test connection lifecycle
 assert not connector.is_connected

 # Note: In real integration test, we would test actual connection
 # For unit test, we verify the connector has the required methods
 assert hasattr(connector, 'connect')
 assert hasattr(connector, 'disconnect')
 assert hasattr(connector, 'get_patient_data')
 assert hasattr(connector, 'get_billing_data')

 print(f"Successfully created and validated connector: {connector.__class__.__name__}")

 @pytest.mark.parametrize("hms_type,expected_connector", [
 (HMSType.BIRLAMEDISOFT, "BirlamedisoftConnector"),
 (HMSType.MEDEIL, "MedeilConnector"),
 (HMSType.EHOSPITAL, "EHospitalConnector"),
 (HMSType.HMS_360, "HMS360Connector"),
 ])
 def test_all_supported_connector_types(
 self, 
 hms_type: HMSType, 
 expected_connector: str
 ):
 """Test all supported HMS connector types can be created."""
 config = HMSConnectionConfig(
 hms_type=hms_type,
 api_endpoint=f"http://{hms_type.value}:8080/api",
 username="test_user",
 password="test_pass"
 )

 connector = HMSConnectorFactory.create_connector(hms_type, config)

 assert connector is not None
 assert connector.__class__.__name__ == expected_connector
 assert connector.config.hms_type == hms_type


class TestHMSConnectorErrorHandling:
 """Test error handling in HMS connectors."""

 def test_invalid_config_handling(self):
 """Test handling of invalid configuration."""
 # Test with None config
 with pytest.raises(TypeError):
 HMSConnectorFactory.create_connector(HMSType.BIRLAMEDISOFT, None)

 def test_connection_failure_simulation(self):
 """Test connection failure scenarios."""
 config = HMSConnectionConfig(
 hms_type=HMSType.BIRLAMEDISOFT,
 api_endpoint="http://invalid-host:8080/api",
 username="test_user",
 password="test_pass",
 timeout=1 # Very short timeout to simulate failure
 )

 connector = HMSConnectorFactory.create_connector(
 HMSType.BIRLAMEDISOFT, 
 config
 )

 assert connector is not None
 # In actual implementation, connection would fail
 # For unit test, we verify the connector is created properly
 assert connector.config.timeout == 1

 def test_data_retrieval_error_handling(self):
 """Test error handling during data retrieval."""
 config = HMSConnectionConfig(
 hms_type=HMSType.BIRLAMEDISOFT,
 api_endpoint="http://test:8080/api",
 username="test",
 password="test"
 )

 connector = HMSConnectorFactory.create_connector(
 HMSType.BIRLAMEDISOFT, 
 config
 )

 # Test that methods exist and can be called
 # In actual implementation, these would handle API errors
 assert hasattr(connector, 'get_patient_data')
 assert hasattr(connector, 'get_billing_data')
 assert callable(connector.get_patient_data)
 assert callable(connector.get_billing_data)


@pytest.mark.slow
class TestHMSConnectorPerformance:
 """Performance tests for HMS connectors."""

 def test_connector_creation_performance(self):
 """Test performance of connector creation."""
 import time

 config = HMSConnectionConfig(
 hms_type=HMSType.BIRLAMEDISOFT,
 api_endpoint="http://localhost:8080/api",
 username="perf_test",
 password="perf_pass"
 )

 start_time = time.time()

 # Create multiple connectors to test performance
 connectors = []
 for _ in range(10):
 connector = HMSConnectorFactory.create_connector(
 HMSType.BIRLAMEDISOFT, 
 config
 )
 connectors.append(connector)

 end_time = time.time()
 creation_time = end_time - start_time

 # Should be able to create 10 connectors quickly
 assert creation_time < 1.0 # Less than 1 second
 assert len(connectors) == 10

 # All connectors should be different instances
 for i, connector in enumerate(connectors):
 for j, other_connector in enumerate(connectors):
 if i != j:
 assert connector is not other_connector