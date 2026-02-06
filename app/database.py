from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import CouchbaseException
from couchbase.options import ClusterOptions, QueryOptions

from app.config import get_settings


def _exc_detail(exc):
  """Extract the most useful error detail from a CouchbaseException."""
  try:
    ctx = exc.error_context
    msg = getattr(ctx, "first_error_message", None)
    if msg:
      return msg
  except Exception:
    pass
  try:
    if exc.message:
      return exc.message
  except Exception:
    pass
  return type(exc).__name__


def get_cluster() -> Cluster:
  """Connect to Couchbase using settings from app.config.

  Raises RuntimeError with a descriptive message on connection failure.
  """
  settings = get_settings()
  try:
    cluster = Cluster.connect(
      settings.cb_connection_string,
      ClusterOptions(
        PasswordAuthenticator(settings.cb_username, settings.cb_password)
      ),
    )
    cluster.wait_until_ready(timedelta(seconds=10))
    return cluster
  except CouchbaseException as exc:
    raise RuntimeError(
      f"Failed to connect to Couchbase at {settings.cb_connection_string}: "
      f"{_exc_detail(exc)}"
    ) from exc


def execute_query(cluster: Cluster, statement: str, timeout: int = 30) -> list[dict]:
  """Execute a SQL++ statement and return results as a list of dicts.

  Raises RuntimeError with a descriptive message on query failure.
  """
  try:
    result = cluster.query(
      statement,
      QueryOptions(timeout=timedelta(seconds=timeout)),
    )
    return [row for row in result]
  except CouchbaseException as exc:
    raise RuntimeError(
      f"Query execution failed: {type(exc).__name__}: {_exc_detail(exc)}"
    ) from exc


def _parse_ai_response(value):
  """Extract clean string from AI Function response format [{"response": "..."}]."""
  if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict) and "response" in value[0]:
    return value[0]["response"]
  return value


def parse_ai_fields_in_results(results, ai_fields):
  """Parse AI Function responses in result rows for specified fields."""
  parsed = []
  for row in results:
    parsed_row = {}
    for key, value in row.items():
      if key in ai_fields:
        parsed_row[key] = _parse_ai_response(value)
      else:
        parsed_row[key] = value
    parsed.append(parsed_row)
  return parsed
