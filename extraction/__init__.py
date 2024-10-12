import toml
from chessdotcom import Client

from extraction.main import get_player_data

Client.request_config["headers"]["User-Agent"] = toml.load("config.toml")["API"][
    "USER_AGENT"
]

__all__ = ["get_player_data"]
