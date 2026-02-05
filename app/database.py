from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import CouchbaseException
from couchbase.options import ClusterOptions, QueryOptions

from app.config import get_settings


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
            f"{type(exc).__name__}"
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
            f"Query execution failed: {type(exc).__name__}"
        ) from exc
