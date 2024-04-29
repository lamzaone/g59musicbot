import discord
import json
import os
import yt_dlp
from config import config
from utils import serversettings as Settings
on_windows = os.name == 'nt'

def is_link(url:str):
    return 'http' in url

def is_youtube(url):
    return 'youtube.com' in url or 'youtu.be' in url

def is_soundcloud(url):
    return 'soundcloud.com' in url

def extract_music_info(query:str):
    try:
        with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
            if is_link(query):
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


def extract_auto_info(query:str):
    try:
        with yt_dlp.YoutubeDL(config.YTDL_AUTO) as ydl:
            info = ydl.extract_info(query, download=False)
            return info
    except Exception as e:
        print(f"[-] An error occurred while extracting info: {e}")
        return None


def get_info(query:str):
    if is_youtube(query) or not is_link(query):
        return extract_music_info(query)
    elif is_soundcloud(query):
        return extract_soundcloud_info(query)
    else:
        return extract_auto_info(query)
    