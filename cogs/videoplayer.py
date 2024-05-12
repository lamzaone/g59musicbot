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


    @commands.hybrid_command(name='anime', aliases=['an']) 
    @app_commands.choices(source=[
        app_commands.Choice(name='GogoAnime',value="gogoanime"),
        app_commands.Choice(name='AnimeFox',value="animefox"),
        app_commands.Choice(name='Animepahe',value="animepahe"),
        app_commands.Choice(name='Zoroxtv.to',value="zoro"),
    ])
    async def anime(self, ctx, name , episode: int = 1, source="gogoanime",):
        global process
        link = None
        if source == 'gogoanime':
            url = f"http://127.0.0.1:3000/anime/gogoanime/watch/{name}-episode-{episode}"
        # elif source == 'animefox':
        #     url = f"http://127.0.0.1:3000/anime/animefox/watch?episodeId={name}-episode-{episode}"
        # elif source == 'animepahe':
        #     url = f"http://127.0.0.1:3000/anime/animepahe/watch/{name}"
        elif source == 'zoro':
            url = f"http://127.0.0.1:3000/anime/animeflix/watch/{name}"
        if process:
            process.terminate()
            process = None

        print(url)
        try:
            if source == 'animefox':
                response = requests.get(url, params={"episodeId": f"{name}-episode-{episode}"})
            elif source == 'zoro':
                response = requests.get(url, params={
                    "episodeId": f"{name}",
                    "server": "vidcloud"
                })
            else:
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