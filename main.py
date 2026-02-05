import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load config and connect to Couchbase. Shutdown: cleanup."""
    from app.config import get_settings
    from app.database import get_cluster

    try:
        settings = get_settings()
    except ValueError:
        logger.exception("Configuration error — app will start without database")
        app.state.cluster = None
        yield
        app.state.cluster = None
        return

    logger.info("Settings loaded — connecting to %s", settings.cb_connection_string)

    try:
        cluster = get_cluster()
        app.state.cluster = cluster
        logger.info("Couchbase connection established")
    except RuntimeError:
        logger.exception("Couchbase connection failed — app will start without database")
        app.state.cluster = None

    yield

    app.state.cluster = None


app = FastAPI(title="CB AI Explorer", lifespan=lifespan)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


# Temporary scaffolding route to verify HTMX fragment delivery (task 1.12)
# Remove after infrastructure setup is complete
@app.get("/test-fragment", response_class=HTMLResponse)
def test_fragment(request: Request):
    return templates.TemplateResponse(request, "partials/test_fragment.html")
