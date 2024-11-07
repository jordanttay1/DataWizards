from network import PlayerNode

MIN_RATING = 1500
COUNTRY = "US"


def is_within_rated_range(player: PlayerNode) -> bool:
    """Check if the player is within the rated range."""
    if player.rating < MIN_RATING:
        print(
            f"Skip adding opponents for player with rating < {MIN_RATING}. They are rated at {player.rating}."
        )
        return False
    return True


def is_within_country(player: PlayerNode) -> bool:
    """Check if the player is within the country."""
    if player.country != COUNTRY:
        print(
            f"Skip adding opponents for player not from {COUNTRY}. They are from {player.country}."
        )
        return False
    return True
