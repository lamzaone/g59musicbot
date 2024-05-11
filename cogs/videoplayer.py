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


# port = int(str(ctx.guild.id)[-4:])
port = 5000
ip = get('https://api.ipify.org').content.decode('utf8')

process = None

class VideoPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def playvideo(self, ctx, url):
        global process
        if os.path.exists('video_streaming/static/video.mp4'):
            os.remove('video_streaming/static/video.mp4')            

        if process:
            process.terminate()
            process = None


        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'video_streaming/static/video.mp4',
            'default_search': 'auto',
        }

        async with ctx.typing():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await ctx.send(f'http://{ip}:{port}')

        process = subprocess.Popen(['python', 'video_streaming/stream.py', str(port)])


    @commands.command(name='anime', aliases=['an']) 
    async def anime(self, ctx, name, episode: int = 1):
        global process
        link = None
        url = f"http://127.0.0.1:3000/anime/gogoanime/watch/{name}-episode-{episode}"
        api = f"http://api.gogoanime.cloud/api/v1/search/{name}"
        if process:
            process.terminate()
            process = None

        try:
            response = requests.get(url)
            print(response)
            data = response.json()
            link = data['sources'][::-1][1]['url']
            process = subprocess.Popen(['python', 'video_streaming/stream.py', str(port), link])            
            await ctx.send(f'http://{ip}:{port}')
        except Exception as e:
            print(e)
            await ctx.send('Anime not found')
            return

async def setup(bot):
    await bot.add_cog(VideoPlayer(bot))