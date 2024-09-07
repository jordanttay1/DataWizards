from chessdotcom import get_player_profile, Client


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
