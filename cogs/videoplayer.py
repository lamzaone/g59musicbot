import socket
import subprocess
import psutil
from video_streaming import stream
import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from requests import get
import requests
import json

ip = get('https://api.ipify.org').content.decode('utf8')

class VideoPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def playvideo(self, ctx, url):
        if os.path.exists('video_streaming/static/video.mp4'):
            os.remove('video_streaming/static/video.mp4')            

        for proc in psutil.process_iter():
            try:
                if proc.name() == 'python' and 'stream.py' in proc.cmdline():
                    proc.terminate()
            except psutil.NoSuchProcess:
                pass


        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'video_streaming/static/video.mp4',
            'default_search': 'auto',
        }
        link = None
        async with ctx.typing():
            try:
                # code start here
                idname= "overlord-iv"
                url = f"http://127.0.0.1:3000/anime/gogoanime/watch/overlord-iv-episode-3"
                response = requests.get(url)
                print(response)
                data = response.json()
                link = data['sources'][::-1][1]['url']
            except Exception as e:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                pass

        print(ip)
        # port = int(str(ctx.guild.id)[-4:])
        port = 5000
        print(port)
        await ctx.send(f'http://{ip}:{port}')

        if link is not None:
            subprocess.Popen(['python', 'video_streaming/stream.py', str(port), link])
        else:
            subprocess.Popen(['python', 'video_streaming/stream.py', str(port)])




async def setup(bot):
    await bot.add_cog(VideoPlayer(bot))