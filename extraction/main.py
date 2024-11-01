import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from chessdotcom import ChessDotComError

from extraction.api import (
    get_player_game_archives,
    get_player_games_by_month,
    get_player_profile,
    get_player_stats,
)
from network import GameEdge, PlayerDetails, PlayerNode

GAME_TYPE = "chess_rapid"


def fetch_archive_games(username: str) -> list[dict]:
    """Fetch the archive games of a player.

    Args:
        username (str): The username of the player.

    Returns:
        list[dict]: A list of games the player has played.
    """

    games = []
    for url in get_player_game_archives(username)["archives"]:
        year = url.split("/")[-2]
        month = url.split("/")[-1]
        games += get_player_games_by_month(username, year, month)["games"]

    return games


def get_opponents_and_games_by_month(
    username: str, year: Optional[int] = None, month: Optional[int] = None
) -> Dict[str, List[GameEdge]]:
    """Get opponents and game details for a player by month.

    Args:
        username (str): The username of the player.
        year (Optional[int], optional): The year to filter by. Defaults to None.
        month (Optional[int], optional): The month to filter by. Defaults to None.

    Returns:
        Dict[str, List[GameEdge]]: A dictionary with opponent usernames as keys and lists of GameEdge objects as values.
    """
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    try:
        games_data = get_player_games_by_month(username, year, month).get("games", [])
    except ChessDotComError as exc:
        if exc.status_code == 0:
            print(
                f"No games found for {username} in {year}-{month}. {year}-{month} is in the future."
            )
            return {}
        else:
            raise
    opponents_games: Dict[str, List[GameEdge]] = {}

    for game in games_data:
        is_white = game["white"]["username"] == username
        opponent_username = (
            game["black"]["username"] if is_white else game["white"]["username"]
        )

        game_edge = GameEdge(
            pgn=game.get("pgn", ""),
            time_control=game.get("time_control", ""),
            time_class=game.get("time_class", ""),
            rules=game.get("rules", ""),
            accuracies=game.get("accuracies", {}),
            eco_code=game.get("eco", ""),
            white=PlayerDetails(
                username=game["white"]["username"],
                rating=game["white"].get("rating", 0),
                result=game["white"]["result"],
                uid=game["white"]["uuid"],
            ),
            black=PlayerDetails(
                username=game["black"]["username"],
                rating=game["black"].get("rating", 0),
                result=game["black"]["result"],
                uid=game["black"]["uuid"],
            ),
            start_time=game.get("start_time", 0),
            end_time=game.get("end_time", 0),
        )

        if opponent_username not in opponents_games:
            opponents_games[opponent_username] = []
        opponents_games[opponent_username].append(game_edge)

    if not opponents_games:
        print(f"No opponents found for {username} in {year}-{month}")

    return opponents_games


async def fetch_player_data(username: str) -> Optional[PlayerNode]:
    """Fetch the player data for a given username asynchronously."""
    return await asyncio.to_thread(get_player_data, username)


def get_player_data(username: str) -> Optional[PlayerNode]:
    """Get the player data for a given username.

    Args:
        username (str): The username of the player.

    Returns:
        PlayerNode: The player node object.
    """
    try:
        profile = get_player_profile(username).get("player")
    except ChessDotComError as exc:
        print(f"Error fetching profile for {username}: {exc}")
        return None
    if not profile:
        print(f"Profile not found for {username}")
        return None

    stats = get_player_stats(username).get("stats").get(GAME_TYPE)
    if stats is None:
        return None
    return PlayerNode(
        uid=profile.get("player_id"),
        name=profile.get("name"),
        username=profile.get("username"),
        country=profile.get("country").split("/")[-1],
        rating=stats.get("last", {}).get("rating", 0),
    )
