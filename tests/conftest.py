import pytest
from starlette.testclient import TestClient


@pytest.fixture
def client():
    """Synchronous test client for FastAPI app."""
    from main import app

    with TestClient(app) as c:
        yield c
