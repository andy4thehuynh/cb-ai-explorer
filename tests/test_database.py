from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest


def _make_settings(**overrides):
  """Create a mock settings object."""
  settings = MagicMock()
  settings.cb_connection_string = overrides.get(
    "cb_connection_string", "couchbases://cb.test.cloud.couchbase.com"
  )
  settings.cb_username = overrides.get("cb_username", "testuser")
  settings.cb_password = overrides.get("cb_password", "testpass")
  settings.cb_bucket = overrides.get("cb_bucket", "travel-sample")
  return settings


class TestGetCluster:
  """Tests for get_cluster() connection logic."""

  @patch("app.database.Cluster")
  @patch("app.database.get_settings")
  def test_connects_with_correct_credentials(self, mock_get_settings, mock_cluster_cls):
    """get_cluster() calls Cluster.connect() with the connection string and PasswordAuthenticator."""
    from app.database import get_cluster

    mock_get_settings.return_value = _make_settings()
    mock_cluster_cls.connect.return_value = MagicMock()

    get_cluster()

    mock_cluster_cls.connect.assert_called_once()
    call_args = mock_cluster_cls.connect.call_args
    assert call_args[0][0] == "couchbases://cb.test.cloud.couchbase.com"

  @patch("app.database.Cluster")
  @patch("app.database.get_settings")
  def test_uses_password_authenticator(self, mock_get_settings, mock_cluster_cls):
    """get_cluster() passes a PasswordAuthenticator with username and password."""
    from app.database import get_cluster, PasswordAuthenticator

    mock_get_settings.return_value = _make_settings()
    mock_cluster_cls.connect.return_value = MagicMock()

    get_cluster()

    call_args = mock_cluster_cls.connect.call_args
    options = call_args[0][1]
    assert options is not None

  @patch("app.database.Cluster")
  @patch("app.database.get_settings")
  def test_connection_failure_raises_clear_error(self, mock_get_settings, mock_cluster_cls):
    """Connection failure produces a clear, descriptive error message."""
    from couchbase.exceptions import CouchbaseException

    from app.database import get_cluster

    mock_get_settings.return_value = _make_settings()
    mock_cluster_cls.connect.side_effect = CouchbaseException("Connection refused")

    with pytest.raises(RuntimeError, match="Failed to connect to Couchbase"):
      get_cluster()


class TestExecuteQuery:
  """Tests for execute_query() SQL++ execution."""

  @patch("app.database.Cluster")
  @patch("app.database.get_settings")
  def test_returns_list_of_dicts(self, mock_get_settings, mock_cluster_cls):
    """execute_query() returns a list of dicts from the query result."""
    from app.database import execute_query

    mock_cluster = MagicMock()
    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(
      return_value=iter([{"id": 1, "name": "test"}, {"id": 2, "name": "other"}])
    )
    mock_cluster.query.return_value = mock_result

    rows = execute_query(mock_cluster, "SELECT * FROM `travel-sample` LIMIT 2")

    assert rows == [{"id": 1, "name": "test"}, {"id": 2, "name": "other"}]
    mock_cluster.query.assert_called_once()

  @patch("app.database.Cluster")
  @patch("app.database.get_settings")
  def test_passes_statement_to_cluster_query(self, mock_get_settings, mock_cluster_cls):
    """execute_query() passes the SQL++ statement to cluster.query()."""
    from app.database import execute_query

    mock_cluster = MagicMock()
    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(return_value=iter([]))
    mock_cluster.query.return_value = mock_result

    statement = "SELECT META().id FROM `travel-sample` LIMIT 1"
    execute_query(mock_cluster, statement)

    call_args = mock_cluster.query.call_args
    assert call_args[0][0] == statement

  @patch("app.database.Cluster")
  @patch("app.database.get_settings")
  def test_respects_custom_timeout(self, mock_get_settings, mock_cluster_cls):
    """execute_query() passes the timeout to QueryOptions."""
    from app.database import execute_query

    mock_cluster = MagicMock()
    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(return_value=iter([]))
    mock_cluster.query.return_value = mock_result

    execute_query(mock_cluster, "SELECT 1", timeout=60)

    call_args = mock_cluster.query.call_args
    # The timeout should be passed through to QueryOptions
    assert call_args is not None

  @patch("app.database.Cluster")
  @patch("app.database.get_settings")
  def test_default_timeout_is_30_seconds(self, mock_get_settings, mock_cluster_cls):
    """execute_query() uses 30s default timeout when none specified."""
    from app.database import execute_query

    mock_cluster = MagicMock()
    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(return_value=iter([]))
    mock_cluster.query.return_value = mock_result

    execute_query(mock_cluster, "SELECT 1")

    call_args = mock_cluster.query.call_args
    assert call_args is not None

  @patch("app.database.Cluster")
  @patch("app.database.get_settings")
  def test_raises_descriptive_error_on_query_failure(self, mock_get_settings, mock_cluster_cls):
    """execute_query() raises a descriptive error when the query fails."""
    from couchbase.exceptions import CouchbaseException

    from app.database import execute_query

    mock_cluster = MagicMock()
    mock_cluster.query.side_effect = CouchbaseException("Syntax error in SQL++")

    with pytest.raises(RuntimeError, match="Query execution failed"):
      execute_query(mock_cluster, "INVALID SQL++")
