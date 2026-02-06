import os
from unittest.mock import patch


def _env_vars(**overrides):
  """Build a complete set of valid env vars, with optional overrides."""
  base = {
    "CB_CONNECTION_STRING": "couchbases://cb.test.cloud.couchbase.com",
    "CB_USERNAME": "testuser",
    "CB_PASSWORD": "testpass",
    "CB_BUCKET": "travel-sample",
  }
  base.update(overrides)
  return base


class TestGetSettings:
  """Tests for get_settings() loading and validation."""

  @patch.dict(os.environ, _env_vars(), clear=False)
  def test_loads_all_env_vars(self):
    """get_settings() loads all 4 env vars correctly from environment."""
    from app.config import get_settings

    settings = get_settings()
    assert settings.cb_connection_string == "couchbases://cb.test.cloud.couchbase.com"
    assert settings.cb_username == "testuser"
    assert settings.cb_password == "testpass"
    assert settings.cb_bucket == "travel-sample"

  @patch.dict(os.environ, {
    "CB_CONNECTION_STRING": "couchbases://cb.test.cloud.couchbase.com",
    "CB_USERNAME": "testuser",
    "CB_PASSWORD": "testpass",
  }, clear=True)
  def test_bucket_defaults_to_travel_sample(self):
    """CB_BUCKET defaults to 'travel-sample' when not set."""
    from app.config import get_settings

    settings = get_settings()
    assert settings.cb_bucket == "travel-sample"

  @patch.dict(os.environ, {
    "CB_USERNAME": "testuser",
    "CB_PASSWORD": "testpass",
  }, clear=True)
  def test_raises_when_connection_string_missing(self):
    """Raises ValueError naming CB_CONNECTION_STRING when it is absent."""
    import pytest
    from app.config import get_settings

    with pytest.raises(ValueError, match="CB_CONNECTION_STRING"):
      get_settings()

  @patch.dict(os.environ, {
    "CB_CONNECTION_STRING": "couchbases://cb.test.cloud.couchbase.com",
    "CB_PASSWORD": "testpass",
  }, clear=True)
  def test_raises_when_username_missing(self):
    """Raises ValueError naming CB_USERNAME when it is absent."""
    import pytest
    from app.config import get_settings

    with pytest.raises(ValueError, match="CB_USERNAME"):
      get_settings()

  @patch.dict(os.environ, {
    "CB_CONNECTION_STRING": "couchbases://cb.test.cloud.couchbase.com",
    "CB_USERNAME": "testuser",
  }, clear=True)
  def test_raises_when_password_missing(self):
    """Raises ValueError naming CB_PASSWORD when it is absent."""
    import pytest
    from app.config import get_settings

    with pytest.raises(ValueError, match="CB_PASSWORD"):
      get_settings()

  @patch.dict(os.environ, _env_vars(), clear=False)
  def test_settings_are_immutable(self):
    """Settings object is read-only after creation."""
    import pytest
    from app.config import get_settings

    settings = get_settings()
    with pytest.raises((AttributeError, TypeError)):
      settings.cb_username = "hacker"
