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


BEFORE_RESULTS = [
  {"hotel_name": "Hotel A", "author": "Alice", "review_text": "Great stay!"},
  {"hotel_name": "Hotel B", "author": "Bob", "review_text": "Decent place."},
]

AFTER_RESULTS = [
  {"hotel_name": "Hotel A", "author": "Alice", "review_text": "Great stay!", "sentiment": "positive"},
  {"hotel_name": "Hotel B", "author": "Bob", "review_text": "Decent place.", "sentiment": "neutral"},
]


@pytest.fixture
def mock_execute_query():
  """Mock database.execute_query to return canned before/after results."""
  call_count = {"n": 0}

  def side_effect(cluster, statement, timeout=30):
    call_count["n"] += 1
    if call_count["n"] % 2 == 1:
      return BEFORE_RESULTS
    return AFTER_RESULTS

  with patch("app.routes.execute_query", side_effect=side_effect):
    yield


@pytest.fixture
def mock_execute_query_error():
  """Mock database.execute_query to raise a RuntimeError."""
  with patch("app.routes.execute_query", side_effect=RuntimeError("Query execution failed: CouchbaseException")):
    yield
