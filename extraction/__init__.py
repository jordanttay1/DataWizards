import os

from chessdotcom import Client
from dotenv import load_dotenv

from extraction.main import (
    fetch_archive_games,
    fetch_player_data,
    get_opponents_and_games_by_month,
    get_player_data,
)

load_dotenv()
Client.request_config["headers"]["User-Agent"] = os.getenv("USER_AGENT")

__all__ = [
    "get_player_data",
    "fetch_player_data",
    "fetch_archive_games",
    "get_opponents_and_games_by_month",
]
