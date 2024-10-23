## Get all usernames that have been pulled so far
import json
import os

import pandas as pd

users = set()

for file_name in os.listdir("Data"):
    print(f"Working on file: {file_name}")
    file_path = os.path.join("Data", file_name)
    with open(file_path, "r") as file:
        data = json.load(file)

    for i in data:
        temp = pd.json_normalize(i["games"])

        users.update(set(temp["black.username"]))
        users.update(set(temp["white.username"]))

with open("player_search_space.txt", "w") as file:
    file.write("\n".join(map(str, users)) + "\n")
