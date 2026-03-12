import pytest
from fastapi.testclient import TestClient

from projeto1.app import app


@pytest.fixture
def client():
    return TestClient(app)
