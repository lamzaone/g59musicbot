import discord

bot_token = 'MTIzMjE3NTYwNzU2NDIxMDIxNw.GEp7Ge.HPvDBvgPN97jVMKl-jTm9YgM3W4OkkEBP5Efgc'

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.5"',
}

YTDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch1',  # ytsearch1 returns the top result
}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.presences = True