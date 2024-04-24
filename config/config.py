import discord
import os

bot_token = 'MTIzMjE3NTYwNzU2NDIxMDIxNw.GuY4Uq.eVvB7ohe7g9vosl9Gd1onkhAyikqYWjkDwoU_w'

serversettings = os.path.join(os.getcwd(), 'config/serversettings.json')
# check if server settings file exists, if not create it
if not os.path.exists(serversettings):
    with open(serversettings, 'w') as f:
        f.write('{}')
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

YTDL_OPTS = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  
    'force-ipv4': True,
    'preferredcodec': 'mp3',
    'cachedir': True,
    'cookiefile': 'cookies.txt',
    'quality': 'highestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'bitdepth': 24,
    
}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.presences = True