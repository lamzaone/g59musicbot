import discord

bot_token = 'MTIzMjE3NTYwNzU2NDIxMDIxNw.GEp7Ge.HPvDBvgPN97jVMKl-jTm9YgM3W4OkkEBP5Efgc'
serversettings = 'serversettings.json'
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    # 'options': '-vn -filter:a "volume=0.5"',
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
    'cachedir': False,
    
}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.presences = True