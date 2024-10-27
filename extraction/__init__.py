import toml
from chessdotcom import Client

from extraction.main import (
    fetch_archive_games,
    get_opponents_and_games_by_month,
    get_player_data,
)

Client.request_config["headers"]["User-Agent"] = toml.load("config.toml")["API"][
    "USER_AGENT"
]

__all__ = [
    "get_player_data",
    "fetch_archive_games",
    "get_opponents_and_games_by_month",
]
