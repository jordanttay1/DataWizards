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
        rating=stats.get("last").get("rating"),
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
