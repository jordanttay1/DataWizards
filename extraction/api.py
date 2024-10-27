import chessdotcom as cdc

from cache import cache


@cache
def get_player_game_archives(username: str):
    """Get the game archives of a player."""
    return cdc.get_player_game_archives(username).json


@cache
def get_player_games_by_month(username: str, year: int, month: int):
    """Get the games of a player by month."""
    return cdc.get_player_games_by_month(username, year, month).json


@cache
def get_player_games_by_month_pgn(username: str, year: int, month: int):
    """Get the games of a player by month."""
    return cdc.get_player_games_by_month_pgn(username, year, month).json


@cache
def get_player_profile(username: str):
    """Get the profile of a player."""
    return cdc.get_player_profile(username).json


@cache
def get_player_stats(username: str):
    """Get the stats of a player."""
    return cdc.get_player_stats(username).json


def main():
    """Simple usage of the chessdotcom package from API docs."""
    cdc.Client.request_config["headers"]["User-Agent"] = (
        "My Python Application. " "Contact me at email@example.com"
    )
    response = get_player_profile("fabianocaruana")
    player_name = response.player.name
    print(player_name)


if __name__ == "__main__":
    main()
