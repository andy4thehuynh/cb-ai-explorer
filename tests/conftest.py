import os
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient


@pytest.fixture
def client():
    """Synchronous test client for FastAPI app.

    Mocks Couchbase connection during lifespan so tests don't need a real cluster.
    Sets dummy env vars so config loading succeeds.
    """
    env = {
        "CB_CONNECTION_STRING": "couchbases://cb.test.cloud.couchbase.com",
        "CB_USERNAME": "testuser",
        "CB_PASSWORD": "testpass",
        "CB_BUCKET": "travel-sample",
    }
    with patch.dict(os.environ, env, clear=False), \
         patch("app.database.Cluster") as mock_cluster_cls:
        mock_cluster_cls.connect.return_value = MagicMock()
        from main import app
        with TestClient(app) as c:
            yield c
