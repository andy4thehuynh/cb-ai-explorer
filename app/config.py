import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

_REQUIRED_VARS = ("CB_CONNECTION_STRING", "CB_USERNAME", "CB_PASSWORD")


@dataclass(frozen=True)
class Settings:
    cb_connection_string: str
    cb_username: str
    cb_password: str
    cb_bucket: str


def get_settings() -> Settings:
    """Load settings from environment variables.

    Raises ValueError if any required variable is missing.
    """
    for var in _REQUIRED_VARS:
        if not os.environ.get(var):
            raise ValueError(f"Required environment variable {var} is not set")

    return Settings(
        cb_connection_string=os.environ["CB_CONNECTION_STRING"],
        cb_username=os.environ["CB_USERNAME"],
        cb_password=os.environ["CB_PASSWORD"],
        cb_bucket=os.environ.get("CB_BUCKET", "travel-sample"),
    )
