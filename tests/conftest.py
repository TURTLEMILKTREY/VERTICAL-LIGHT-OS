"""
Test configuration and fixtures for Hospital AI Consulting OS.

This module provides comprehensive test configuration, fixtures, and utilities
for all test types including unit, integration, end-to-end, and performance tests.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Dict, Generator, Any
import warnings

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from backend.main import create_app
from backend.models.schemas import Base
from backend.config.config_manager import ConfigManager
from shared.types import HospitalData

# Suppress specific warnings during testing
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Test Configuration Constants
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_REDIS_URL = "redis://localhost:6379/1"
TEST_CONFIG_PATH = Path(__file__).parent / "fixtures" / "test_config.json"

# Test markers configuration
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
 """
 Create event loop for async tests.

 Yields:
 Event loop for async operations
 """
 loop = asyncio.get_event_loop_policy().new_event_loop()
 yield loop
 loop.close()


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
 """
 Provide test configuration.

 Returns:
 Test configuration dictionary
 """
 return {
 "database": {
 "url": TEST_DATABASE_URL,
 "echo": False,
 "pool_size": 5,
 "max_overflow": 10
 },
 "redis": {
 "url": TEST_REDIS_URL,
 "decode_responses": True,
 "socket_timeout": 30
 },
 "api": {
 "host": "127.0.0.1",
 "port": 8000,
 "debug": True
 },
 "logging": {
 "level": "INFO",
 "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
 },
 "security": {
 "secret_key": "test-secret-key-for-testing-only",
 "algorithm": "HS256",
 "access_token_expire_minutes": 30
 }
 }


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
 """
 Create temporary directory for test files.

 Yields:
 Temporary directory path
 """
 with tempfile.TemporaryDirectory() as tmp_dir:
 yield Path(tmp_dir)


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
 """
 PostgreSQL test container for integration tests.

 Yields:
 PostgreSQL container instance
 """
 with PostgresContainer("postgres:15") as postgres:
 yield postgres


@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, None, None]:
 """
 Redis test container for integration tests.

 Yields:
 Redis container instance
 """
 with RedisContainer("redis:7") as redis:
 yield redis


@pytest.fixture(scope="function")
def test_db_engine(test_config: Dict[str, Any]):
 """
 Create test database engine.

 Args:
 test_config: Test configuration

 Returns:
 SQLAlchemy engine for testing
 """
 engine = create_engine(
 test_config["database"]["url"],
 echo=test_config["database"]["echo"]
 )

 # Create all tables
 Base.metadata.create_all(bind=engine)

 yield engine

 # Cleanup
 Base.metadata.drop_all(bind=engine)
 engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
 """
 Create test database session.

 Args:
 test_db_engine: Test database engine

 Returns:
 Database session for testing
 """
 TestingSessionLocal = sessionmaker(
 autocommit=False, 
 autoflush=False, 
 bind=test_db_engine
 )

 session = TestingSessionLocal()
 try:
 yield session
 finally:
 session.close()


@pytest.fixture(scope="function")
async def test_app(test_config: Dict[str, Any]):
 """
 Create test FastAPI application.

 Args:
 test_config: Test configuration

 Returns:
 FastAPI application instance for testing
 """
 # Override configuration for testing
 os.environ.update({
 "DATABASE_URL": test_config["database"]["url"],
 "REDIS_URL": test_config["redis"]["url"],
 "SECRET_KEY": test_config["security"]["secret_key"],
 "DEBUG": "true"
 })

 app = create_app()
 return app


@pytest.fixture(scope="function")
async def test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
 """
 Create test HTTP client.

 Args:
 test_app: FastAPI test application

 Yields:
 HTTP client for API testing
 """
 async with AsyncClient(
 app=test_app, 
 base_url="http://testserver"
 ) as client:
 yield client


@pytest.fixture(scope="function")
def sample_hospital_data() -> HospitalData:
 """
 Provide sample hospital data for testing.

 Returns:
 Sample hospital data instance
 """
 return HospitalData(
 hospital_id="H001",
 name="Test General Hospital",
 location="Mumbai, Maharashtra",
 type="MULTI_SPECIALTY",
 capacity=200,
 departments=["Cardiology", "Neurology", "Orthopedics"],
 contact_info={
 "phone": "+91-22-12345678",
 "email": "info@testhosp.com",
 "website": "www.testhosp.com"
 }
 )


@pytest.fixture(scope="function")
def mock_hms_data() -> Dict[str, Any]:
 """
 Provide mock HMS (Hospital Management System) data.

 Returns:
 Mock HMS data dictionary
 """
 return {
 "patients": {
 "active": 150,
 "admissions_today": 25,
 "discharges_today": 20,
 "occupancy_rate": 0.75
 },
 "departments": {
 "emergency": {"patients": 15, "wait_time": 45},
 "icu": {"patients": 12, "capacity": 20},
 "surgery": {"operations": 8, "scheduled": 12}
 },
 "staff": {
 "doctors": 45,
 "nurses": 120,
 "support": 80,
 "on_duty": 165
 },
 "finances": {
 "revenue_today": 125000,
 "pending_bills": 85000,
 "collections": 95000
 }
 }


@pytest.fixture(scope="function")
def performance_test_data() -> Dict[str, Any]:
 """
 Provide performance test data sets.

 Returns:
 Performance test data dictionary
 """
 return {
 "small_dataset": list(range(100)),
 "medium_dataset": list(range(1000)),
 "large_dataset": list(range(10000)),
 "concurrent_users": 50,
 "test_duration": 60,
 "response_time_threshold": 2.0
 }


class TestDataFactory:
 """Factory for creating test data objects."""

 @staticmethod
 def create_hospital_batch(count: int = 10) -> list[HospitalData]:
 """
 Create batch of hospital data for testing.

 Args:
 count: Number of hospital records to create

 Returns:
 List of hospital data instances
 """
 hospitals = []
 for i in range(count):
 hospital = HospitalData(
 hospital_id=f"H{i+1:03d}",
 name=f"Test Hospital {i+1}",
 location=f"Test City {i+1}",
 type="MULTI_SPECIALTY",
 capacity=100 + (i * 50),
 departments=["General", "Emergency", "Surgery"],
 contact_info={
 "phone": f"+91-11-1234567{i}",
 "email": f"hospital{i+1}@test.com"
 }
 )
 hospitals.append(hospital)
 return hospitals

 @staticmethod
 def create_performance_metrics() -> Dict[str, float]:
 """
 Create performance metrics for testing.

 Returns:
 Performance metrics dictionary
 """
 return {
 "bed_occupancy_rate": 0.85,
 "average_length_of_stay": 4.2,
 "revenue_per_bed": 15000.0,
 "staff_efficiency": 0.78,
 "patient_satisfaction": 4.1,
 "cost_per_patient": 8500.0
 }


# Pytest plugins and configurations
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
 """Configure pytest with custom markers and settings."""
 config.addinivalue_line(
 "markers", "unit: Unit tests focusing on individual components"
 )
 config.addinivalue_line(
 "markers", "integration: Integration tests with external dependencies"
 )
 config.addinivalue_line(
 "markers", "e2e: End-to-end tests simulating user workflows"
 )
 config.addinivalue_line(
 "markers", "performance: Performance and load tests"
 )
 config.addinivalue_line(
 "markers", "security: Security and vulnerability tests"
 )
 config.addinivalue_line(
 "markers", "slow: Tests that take longer than 5 seconds"
 )
 config.addinivalue_line(
 "markers", "database: Tests that require database connectivity"
 )
 config.addinivalue_line(
 "markers", "api: API endpoint tests"
 )
 config.addinivalue_line(
 "markers", "regression: Regression tests for bug fixes"
 )


def pytest_collection_modifyitems(config, items):
 """Modify test collection to add markers based on test location."""
 for item in items:
 # Add markers based on test file location
 if "unit" in str(item.fspath):
 item.add_marker(pytest.mark.unit)
 elif "integration" in str(item.fspath):
 item.add_marker(pytest.mark.integration)
 elif "e2e" in str(item.fspath):
 item.add_marker(pytest.mark.e2e)
 elif "performance" in str(item.fspath):
 item.add_marker(pytest.mark.performance)
 item.add_marker(pytest.mark.slow)

 # Mark database tests
 if hasattr(item, 'fixturenames') and 'test_db_session' in item.fixturenames:
 item.add_marker(pytest.mark.database)

 # Mark API tests
 if hasattr(item, 'fixturenames') and 'test_client' in item.fixturenames:
 item.add_marker(pytest.mark.api)


@pytest.fixture(autouse=True)
def cleanup_test_files():
 """Auto cleanup test files after each test."""
 yield
 # Cleanup logic here if needed
 pass


# Custom assertion helpers
def assert_hospital_data_valid(hospital: HospitalData) -> None:
 """Assert that hospital data is valid."""
 assert hospital.hospital_id is not None
 assert len(hospital.hospital_id) > 0
 assert hospital.name is not None
 assert len(hospital.name) > 0
 assert hospital.capacity > 0
 assert len(hospital.departments) > 0


def assert_performance_within_threshold(
 actual_time: float, 
 threshold: float = 2.0
) -> None:
 """Assert that performance is within acceptable threshold."""
 assert actual_time <= threshold, (
 f"Performance test failed: {actual_time}s > {threshold}s threshold"
 )