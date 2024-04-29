import discord
import os



### CONFIGURATION FILES
#get the full path for the current folder
current_folder = os.path.dirname(os.path.abspath(__file__))
serversettings = os.path.join(current_folder, 'serversettings.json')
queues = os.path.join(current_folder, 'queues.json')
token_file = os.path.join(current_folder, 'bot_token.txt')
FFMPEG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ffmpeg.exe')
bot_token=''


def init():
    global bot_token

    # Check if serversettings.json exists
    try:
        with open(serversettings, 'r') as f:
            if f.read() == '':
                with open(serversettings, 'w') as f:
                    f.write('{}')
    except FileNotFoundError:
        # If the file does not exist, create it
        print("[!] serversettings.json not found. Attempting to create it now.")
        try:
            with open(serversettings, 'w') as f:
                f.write('{}')
            print("[+] serversettings.json created successfully")
        except Exception as e:
            print("[!!] Error creating serversettings.json file. Check permissions on the folder.\n^-- Error: ", e)


    # Check if queues.json exists
    try:
        with open(queues, 'r') as f:
            if f.read() == '':
                with open(queues, 'w') as f:
                    f.write('{}')
    except FileNotFoundError:
        # If the file does not exist, create it
        print("[!] queues.json  not found. Attempting to create it now.")
        try:
            with open(queues, 'w') as f:
                f.write('{}')
            print("[+] queues.json created successfully")
        except Exception as e:
            print("[!!] Error creating queues.json file. Check permissions on the folder.\n^-- Error: ", e)
    

    # Check if bot_token.txt exists
    try:
        with open(token_file, 'r') as f:
            bot_token = f.read()
    except FileNotFoundError:
        # If the file does not exist, create it and ask the user for the bot token
        print("[!] bot_token.txt not found. Attempting to create it now.")
        try:
            with open(token_file, 'w') as f:
                bot_token = input("[-] Please enter your bot token: ")
                f.write(bot_token)
            print("[+] bot_token.txt created successfully")
        except Exception as e:
            print("[!!] Error creating bot_token.txt file. Check permissions on the folder.\n^-- Error: ", e)
    
    # Check if the bot token is valid and ask for the token again if it's not valid.
    if len(bot_token) < 10:
        print("[!] Bot token is invalid. Please enter a valid bot token")
        try:
            with open(token_file, 'w') as f:
                bot_token = input("[-] Please enter your bot token: ")
                f.write(bot_token)
            print("[+] bot_token.txt updated successfully")
        except Exception as e:
            print("[!!] Error updating bot_token.txt file. Check permissions on the folder.\n^-- Error: ", e)


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
    'default_search': 'ytsearch1',
    'source_address': '0.0.0.0',  
    'force-ipv4': True,
    'preferredcodec': 'mp3',
    'preferredquality': '256',
    'cachedir' : True,
    'timeout': 60,
    'expiretime': 3600,
    "noprogress": True,
    "socket_timeout": 5,
    "socket_io_timeout": 10,
    "sleep_interval": 1,
    "max_sleep_interval": 5,
    "retries": 10,
    "fragment_retries": 10,
    "threads": 6,
    "geo_bypass": True,
    'cookiefile': 'cookies.txt',
    'quality': 'highestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256',
    }],
    'bitdepth': 24,
    
}

YTDL_SOUNDCLOUD_OPTS = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'force-ipv4': True,
    'preferredcodec': 'mp3',
    'preferredquality': '256',
    "noprogress": True,
    "socket_timeout": 5,
    "socket_io_timeout": 10,
    "sleep_interval": 1,
    "max_sleep_interval": 5,
    "retries": 10,
    "fragment_retries": 10,
    "threads": 6,
    "geo_bypass": True,
    'timeout': 60,
    'default_search': 'soundcloud',
    'source_address': '0.0.0.0'
    }


YTDL_AUTO = {
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
    'preferredcodec': 'mp3',
    'preferredquality': '256',
    'timeout': 60,
    'expiretime': 3600,
    "noprogress": True,
    "socket_timeout": 5,
    "socket_io_timeout": 10,
    "sleep_interval": 1,
    "max_sleep_interval": 5,
    "retries": 10,
    "fragment_retries": 10,
    "threads": 6,
    "geo_bypass": True,
    'cookiefile': 'cookies.txt',
    'quality': 'highestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256',
    }],
    'bitdepth': 24,
    
}


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.presences = True