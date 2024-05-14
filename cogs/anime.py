import subprocess
import discord
from discord.ext import commands
from discord import app_commands
import requests
import os

port = 5000
ip = requests.get('https://api.ipify.org').content.decode('utf8')
is_windows = os.name == 'nt'

#TODO: MAKE THIS NOT DEPENDENT ON THE API
class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='anime', aliases=['an']) 
    @app_commands.choices(source=[
        app_commands.Choice(name='GogoAnime',value="gogoanime"),
        ############## THE API IS NOT WORKING FOR THESE SITES
        # app_commands.Choice(name='AnimeFox',value="animefox"), 
        # app_commands.Choice(name='Animepahe',value="animepahe"),
        # app_commands.Choice(name='Zoroxtv.to',value="zoro"),
    ])
    async def anime(self, ctx, name , episode: int = 1, source="gogoanime",):
        if hasattr(ctx.bot, 'process'):
            if ctx.bot.process is not None:
                ctx.bot.process.kill()
                ctx.bot.process = None
        link = None
        if source == 'gogoanime':
            url = f"http://127.0.0.1:3000/anime/gogoanime/watch/{name}-episode-{episode}"
        elif source == 'animefox':
            url = f"http://127.0.0.1:3000/anime/animefox/watch?episodeId={name}-episode-{episode}"
        elif source == 'animepahe':
            url = f"http://127.0.0.1:3000/anime/animepahe/watch/{name}"
        elif source == 'zoro':
            url = f"http://127.0.0.1:3000/anime/zoro/watch?episodeId={name}?source=vidcloud"
            

        print(url)
        try:
            response = requests.get(url)
            print(response)
            data = response.json()
            link = data['sources'][::-1][0]['url']
            ctx.bot.process = subprocess.Popen(['python' if is_windows else 'python3', 'video_streaming/stream.py', str(port), link])            
            await ctx.send(f'http://{ip}:{port}')
        except Exception as e:
            print(e)
            await ctx.send('Anime not found')
            return
        

async def setup(bot):
    await bot.add_cog(Anime(bot))