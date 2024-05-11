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

ip = get('https://api.ipify.org').content.decode('utf8')

class VideoPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def playvideo(self, ctx, url):
        if os.path.exists('video_streaming/static/video.webm'):
            os.remove('video_streaming/static/video.webm')            

        for proc in psutil.process_iter():
            try:
                if proc.name() == 'python' and 'stream.py' in proc.cmdline():
                    proc.terminate()
            except psutil.NoSuchProcess:
                pass


        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'video_streaming/static/video.webm',
            'default_search': 'auto',
        }

        async with ctx.typing():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        print(ip)
        # port = int(str(ctx.guild.id)[-4:])
        port = 5000
        print(port)
        await ctx.send(f'http://{ip}:{port}')

        subprocess.Popen(['python', 'video_streaming/stream.py', str(port)])




async def setup(bot):
    await bot.add_cog(VideoPlayer(bot))