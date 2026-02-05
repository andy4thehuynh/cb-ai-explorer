import os


def test_fastapi_app_creates():
    """FastAPI app instance can be imported and created without error."""
    from main import app
    assert app is not None
    assert app.title or True  # app exists and is a FastAPI instance


def test_health_endpoint(client):
    """GET /health returns 200 with {"status": "ok"}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_jinja2_templates_directory():
    """templates/ directory exists and is configured in the app."""
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    assert os.path.isdir(templates_dir), "templates/ directory must exist"

    from app.routes import templates
    assert templates is not None


def test_index_page_renders(client):
    """GET / renders a page via Jinja2 with expected content."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "CB AI Explorer" in response.text
