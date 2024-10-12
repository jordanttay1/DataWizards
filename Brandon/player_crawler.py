import concurrent.futures
import json
import os
import threading
from urllib.request import urlopen

import pandas as pd
from chessdotcom import Client, get_player_game_archives

# Global set to store all users to search
users_to_search = set()
users_to_search_lock = threading.Lock()  # Lock to ensure thread-safe updates


def fetch_archive(url):
    """Fetch game data from a single archive URL."""
    try:
        response = urlopen(url)
        return json.loads(response.read())
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def save_user_data(u_name, raw_json):
    """Save game data for a user to a file."""
    os.makedirs("Data", exist_ok=True)  # Create the folder if it doesn't exist
    with open(f"Data/{u_name}.json", "w") as file:
        json.dump(raw_json, file, indent=4)


def fetch_and_save_user_games(u_name):
    """Fetch and save games for a single user."""
    try:
        g_history = get_player_game_archives(u_name).json
        archives = g_history["archives"]
    except Exception as e:
        print(f"Failed to fetch archives for {u_name}: {e}")
        return []

    raw_json = []
    # Fetch game data sequentially
    for url in archives:
        print(url)
        data = fetch_archive(url)
        if data:
            raw_json.append(data)

    # Save user data
    save_user_data(u_name, raw_json)

    # Extract unique opponents from the game data
    new_users = set()
    for games_data in raw_json:
        if "games" in games_data:
            get_raw_users = pd.json_normalize(games_data["games"])[
                ["black.username", "white.username"]
            ]
            new_users.update(
                set(get_raw_users["black.username"]).union(
                    set(get_raw_users["white.username"])
                )
            )

    # Thread-safe update of global `users_to_search`
    with users_to_search_lock:
        users_to_search.update(new_users)
        with open("player_search_space.txt", "w") as file:
            file.write("\n".join(map(str, users_to_search)) + "\n")

    print(f"Search space size: {len(users_to_search)}")

    return new_users


def get_users_played_recursively(
    u_name, searched_users, executor, depth=0, max_depth=10
):
    """Recursively get users played by starting user, using a global thread pool."""
    if u_name in searched_users or depth > max_depth:
        return
    searched_users.add(u_name)

    print(f"Fetching data for {u_name} at depth {depth}...")

    # Fetch and save current user's games, and get their opponents
    fetch_and_save_user_games(u_name)

    print(f"{u_name} data fetched")

    # Check if depth allows more recursion
    if depth < max_depth:
        # Thread-safe access to `users_to_search`
        with users_to_search_lock:
            users_to_search_copy = (
                users_to_search.copy()
            )  # Avoid modifying the set while iterating

        # Submit new tasks for each opponent recursively, but within the global thread pool
        futures = {
            executor.submit(
                get_users_played_recursively,
                user,
                searched_users,
                executor,
                depth + 1,
                max_depth,
            ): user
            for user in users_to_search_copy
        }
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Wait for each future to complete


Client.request_config["headers"]["User-Agent"] = (
    "My Python Application. " "Contact me at"
)

# Start with the initial user
start_user = "bkdog99"
searched_users = set()

# Use a global thread pool for all recursive tasks
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
    get_users_played_recursively(start_user, searched_users, executor, max_depth=10)

# After the recursion completes, `users_to_search` will contain all unique users encountered
with users_to_search_lock:
    print(f"Total unique users found: {len(users_to_search)}")
