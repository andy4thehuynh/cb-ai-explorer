import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes import router

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
app.include_router(router)
