import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import get_storage


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    storage = get_storage()
    storage.clear()
    yield
    storage.clear()