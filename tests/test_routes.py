"""
Task 2.5: Route tests — verify HTTP endpoints behave correctly.

Tests:
  (a) GET /health returns 200 with {"status": "ok"}
"""


def test_health_endpoint(client):
    """GET /health returns 200 with {"status": "ok"}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
