import toml
from chessdotcom import Client

Client.request_config["headers"]["User-Agent"] = toml.load("config.toml")["API"][
    "USER_AGENT"
]
