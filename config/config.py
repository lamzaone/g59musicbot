import discord
import os



### CONFIGURATION FILES
#get the full path for the current folder
config_path = os.path.dirname(os.path.abspath(__file__))
serversettings = os.path.join(config_path, 'serversettings.json')
queues = os.path.join(config_path, 'queues.json')
token_file = os.path.join(config_path, 'bot_token.txt')
playlists_folder = os.path.join(os.path.dirname(config_path), 'playlists')
FFMPEG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ffmpeg.exe')
bot_token=''
cogs_dir = os.path.join(os.path.dirname(config_path), 'cogs')
cache_dir = os.path.join(os.path.dirname(config_path), 'cache')
cookies_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookies.txt')


def init():
    global bot_token
    global app_id
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


        

def get_cogs():
    cogs = []
    for file in os.listdir(cogs_dir):
        if file.endswith(".py") and not file.startswith("!"):
            cogs.append(file[:-3])
    return cogs


os.makedirs(cache_dir, exist_ok=True)

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
    'no-download': True,
    'default_search': 'ytsearch1',
    'source_address': '0.0.0.0',  
    'force-ipv4': True,
    'preferredcodec': 'webm',
    'preferredquality': '0',
    'cachedir' : cache_dir,
    "noprogress": True,
    'cookiefile': 'cookies.txt',
    'quality': '0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'webm',
        'preferredquality': '0',
    }],
    'bitdepth': 24,
    
}

YTDL_SOUNDCLOUD_OPTS = {
    'format': 'bestaudio/best',    
    'no-download': True,
    'restrictfilenames': False,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'force-ipv4': True,
    'preferredcodec': 'webm',
    'preferredquality': '0',
    "noprogress": True,
    'quality': '0',
    'default_search': 'soundcloud',
    'source_address': '0.0.0.0'
    }


YTDL_AUTO = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': True,    
    'no-download': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  
    'force-ipv4': True,
    'preferredcodec': 'webm',
    'preferredquality': '0',
    'cachedir' : cache_dir,
    "noprogress": True,
    'cookiefile': 'cookies.txt',
    'quality': '0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'webm',
        'preferredquality': '0',
    }],
    'bitdepth': 24,
    
}
