from config import config
import json



default_settings = {
    "volume": 0.5,
    "prefix": "!",
    "dj_role": None}


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


def check_integrity(guild_settings):
    for setting in default_settings:
        if setting not in guild_settings:
            guild_settings[setting] = default_settings[setting]
    return guild_settings

async def check_guilds(guilds):
    all_settings = get_settings_all()
    try:
        for guild in guilds:
            guild_settings = get_settings(guild.id)
            if guild_settings is None:
                guild_settings = default_settings
            guild_settings = check_integrity(guild_settings)
            all_settings[str(guild.id)] = guild_settings
        set_all_settings(all_settings)
    except Exception as e:
        print('[!] Error checking guild settings: ', e)


def get_dj_role(guild_id):
    settings = get_settings(guild_id)
    return settings['dj_role']