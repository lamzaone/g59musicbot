import discord
import json
import os
import yt_dlp
from config import config
from utils import serversettings as Settings
on_windows = os.name == 'nt'

def is_soundcloud(url):
    return 'soundcloud.com' in url or 'sndcdn.com' in url

def is_youtube(url):
    return 'youtube.com' in url or 'youtu.be' in url

def extract_yt_info(query:str):
    try:
        with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
            if is_youtube(query):
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(query, download=False)['entries'][0]
            return info
    except Exception as e:
        print(f"[-] An error occurred while extracting info: {e}")
        return None
    

def extract_soundcloud_info(query:str):
    try:
        with yt_dlp.YoutubeDL(config.YTDL_SOUNDCLOUD_OPTS) as ydl:
            info = ydl.extract_info(query, download=False)
            return info
    except Exception as e:
        print(f"[-] An error occurred while extracting info: {e}")
        return None



def get_info(query:str):
    if is_soundcloud(query):
        return extract_soundcloud_info(query)
    else:
        return extract_yt_info(query)
    

    
# def get_audio_source(url:str, guild_id:int):
#     try:
#         if on_windows:
#             audio_source = discord.FFmpegPCMAudio(url, executable=config.FFMPEG_PATH, options=config.ffmpeg_options)
#             return discord.PCMVolumeTransformer(audio_source, Settings.get_settings(guild_id)['volume'])
#         else:
#             audio_source = discord.FFmpegPCMAudio(url, options=config.ffmpeg_options)
#             return discord.PCMVolumeTransformer(audio_source, Settings.get_settings(guild_id)['volume'])
#     except Exception as e:
#         print(f"[-] An error occurred while getting audio source: {e}")
#         return None