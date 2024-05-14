import socket
import subprocess
import psutil
from video_streaming import stream
import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import os
from requests import get
import requests
import json

is_windows = os.name == 'nt'

#TODO: MAKE THIS WORK WITH DIRECT LINKS INSTEAD OF DOWNLOADING THE WHOLE SHIT

# port = int(str(ctx.guild.id)[-4:])
port = 5000
ip = get('https://api.ipify.org').content.decode('utf8')


class VideoPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def playvideo(self, ctx, url):
        if os.path.exists('video_streaming/static/video.mp4'):
            os.remove('video_streaming/static/video.mp4')            

        if hasattr(ctx.bot, 'process'):
            if ctx.bot.process is not None:
                ctx.bot.process.kill()
                ctx.bot.process = None


        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'video_streaming/static/video.mp4',
            'default_search': 'auto',
            'forceurl': True,
        }

        async with ctx.typing():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                
                print(info)
                print(video)

        await ctx.send(f'http://{ip}:{port}')

        ctx.bot.process = subprocess.Popen(['python' if is_windows else 'python3', 'video_streaming/stream.py', str(port)])




    
async def setup(bot):
    await bot.add_cog(VideoPlayer(bot))