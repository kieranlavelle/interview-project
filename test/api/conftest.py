import pytest
from fastapi.testclient import TestClient

from service_provider_api.app import app


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)
