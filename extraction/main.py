from datetime import datetime
from typing import Optional

from chessdotcom import (
    Client,
    get_player_game_archives,
    get_player_games_by_month,
    get_player_profile,
    get_player_stats,
)

from network import PlayerNode

GAME_TYPE = "chess_rapid"


def fetch_archive_games(username: str) -> list[dict]:
    """Fetch the archive games of a player.

    Args:
        username (str): The username of the player.

    Returns:
        list[dict]: A list of games the player has played.
    """

    games = []
    for url in get_player_game_archives(username).json["archives"]:
        year = url.split("/")[-2]
        month = url.split("/")[-1]
        games += get_player_games_by_month(username, year, month).json["games"]

    return games


def get_opponents_by_month(
    username: str, year: Optional[int] = None, month: Optional[int] = None
) -> set[str]:
    """Get the opponents of a player by month.

    Args:
        username (str): The username of the player.
        year (Optional[int], optional): The year to filter by. Defaults to None.
        month (Optional[int], optional): The month to filter by. Defaults to None.

    Returns:
        set[str]: A set of opponents the player has played against.
    """
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    games = get_player_games_by_month(username, year, month).json.get("games", [])
    opponents = set()
    for game in games:
        opponent = (
            game["black"]["username"]
            if game["white"]["username"] == username
            else game["white"]["username"]
        )
        opponents.add(opponent)
    if not opponents:
        print(f"No opponents found for {username} in {year}-{month}")
    return opponents


def get_player_data(username: str) -> PlayerNode:
    """Get the player data for a given username.

    Args:
        username (str): The username of the player.

    Returns:
        PlayerNode: The player node object.
    """
    profile = get_player_profile(username).json.get("player")
    if not profile:
        raise ValueError(f"Player {username} not found.")
    stats = get_player_stats(username).json.get("stats").get(GAME_TYPE)
    return PlayerNode(
        uid=profile.get("player_id"),
        name=profile.get("name"),
        username=profile.get("username"),
        country=profile.get("country").split("/")[-1],
        rating=stats.get("last", {}).get("rating", 0),
    )


def main():
    """Simply usage of the chessdotcom package from API docs."""
    Client.request_config["headers"]["User-Agent"] = (
        "My Python Application. " "Contact me at email@example.com"
    )
    response = get_player_profile("fabianocaruana")
    player_name = response.player.name
    print(player_name)


if __name__ == "__main__":
    main()
