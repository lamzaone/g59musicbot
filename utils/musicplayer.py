import discord
import json
import os
import yt_dlp
from config import config

on_windows = os.name == 'nt'



def extract_yt_info(query:str):
    try:
        with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
            if 'youtube.com' in query or 'youtu.be' in query:
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(query, download=False)['entries'][0]
            return info
    except Exception as e:
        print(f"[-] An error occurred while extracting info: {e}")
        return None
    

# def get_audio_source