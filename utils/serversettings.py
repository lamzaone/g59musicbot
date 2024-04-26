from config import config
import json


default_settings = {"volume": 0.5,\
                "prefix": "!",}


def get_settings_all():
    with open(config.serversettings, "r") as f:
        settings = json.load(f)
    return settings

def get_settings(guild_id: int):
    settings = get_settings_all()
    if str(guild_id) in settings:
        return settings[str(guild_id)]
    return None

def set_all_settings(settings):
    try:
        with open(config.serversettings, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print('[-] Error updating settings: ', e)


def set_guild_settings(guild_id: int, settings):
    all_settings = get_settings_all()
    all_settings[str(guild_id)] = settings
    set_all_settings(all_settings)
