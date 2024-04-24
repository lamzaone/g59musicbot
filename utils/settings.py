from config import config
import json

def get_settings(guild_id: int):
    with open(config.serversettings, "r") as f:
        settings = json.load(f)

