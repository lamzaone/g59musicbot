import discord
import os

bot_token = 'MTIzMjE3NTYwNzU2NDIxMDIxNw.GuY4Uq.eVvB7ohe7g9vosl9Gd1onkhAyikqYWjkDwoU_w'

### CONFIGURATION FILES
#get the full path for the current folder
current_folder = os.path.dirname(os.path.abspath(__file__))
serversettings = os.path.join(current_folder, 'serversettings.json')
queues = os.path.join(current_folder, 'queues.json')


def init():
    try:
        with open(serversettings, 'r') as f:
            if f.read() == '':
                with open(serversettings, 'w') as f:
                    f.write('{}')
    except FileNotFoundError:
        print("[-] serversettings.json not found. Creating it now.")
        try:
            with open(serversettings, 'w') as f:
                f.write('{}')
            print("[+] serversettings.json created successfully")
        except Exception as e:
            print("[--] Error creating serversettings.json file. Check permissions on the folder.\n^-- Error: ", e)

    try:
        with open(queues, 'r') as f:
            if f.read() == '':
                with open(queues, 'w') as f:
                    f.write('{}')
    except FileNotFoundError:
        print("[-] queues.json  not found. Creating it now.")
        try:
            with open(queues, 'w') as f:
                f.write('{}')
            print("[+] queues.json created successfully")
        except Exception as e:
            print("[--] Error creating queues.json file. Check permissions on the folder.\n^-- Error: ", e)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

YTDL_OPTS = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  
    'force-ipv4': True,
    'preferredcodec': 'wav',
    'preferredquality': '320',
    'cachedir': True,
    'expiretime': 3600,
    'cookiefile': 'cookies.txt',
    'quality': 'highestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '320',
    }],
    'bitdepth': 24,
    
}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.presences = True