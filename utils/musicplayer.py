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
    except yt_dlp.DownloadError as e:
        print(f"[-] An error occurred while downloading the video: {e}") 
        return None
    except Exception as e:
        print(f"[-] An error occurred while extracting info: {e}")

    

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
        print("is youtube")
        return extract_music_info(query)
    elif is_soundcloud(query):
        print("is soundcloud")
        return extract_soundcloud_info(query)
    else:
        print("is auto")
        return extract_auto_info(query)
    
def format_duration(duration:int):
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    if seconds < 10:
        seconds = f"0{seconds}"
    if minutes < 10:
        minutes = f"0{minutes}"
    return f"{hours}:{minutes}:{seconds}" if hours > 0 else f"{minutes}:{seconds}"

def format_upload_date(_date:str):
    _date = _date.split('T')[0]
    y = _date[:4]
    m = _date[4:6]
    d = _date[6:8]
    return f"{d}/{m}/{y}"

def get_elapsed(start:int, current:int):
    elapsed = current-start
    elapsed = int(elapsed.total_seconds())
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    if seconds < 10:
        seconds = f"0{seconds}"
    if minutes < 10 & hours > 0:
        minutes = f"0{minutes}"
    elapsed = f"{hours}:{minutes}:{seconds}" if hours > 0 else f"{minutes}:{seconds}"
    return elapsed
