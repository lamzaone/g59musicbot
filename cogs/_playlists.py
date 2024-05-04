import discord
from discord.ext import commands
from discord import app_commands
from utils import queues as Queues
from config import config
import os
import json
import asyncio

class _Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    group = app_commands.Group(name='playlist', description='Manage playlists')
    @group.command(name='list', description='Manage playlists')
    async def list(self, interaction: discord.Interaction, playlist_name: str=None):
        ctx = await self.bot.get_context(interaction)
        playlist_cog = self.bot.get_cog('Playlist')
        await interaction.response.defer()
        await playlist_cog.playlist(ctx, playlist_name)

    @group.command(name='create', description='Create a new playlist')
    async def create(self, interaction: discord.Interaction, name: str):
        ctx = await self.bot.get_context(interaction)
        playlist_cog = self.bot.get_cog('Playlist')
        await playlist_cog.create(ctx, name)
        
    @group.command(name='delete', description='Delete a playlist')
    async def delete(self, interaction: discord.Interaction, name: str):
        ctx = await self.bot.get_context(interaction)
        playlist_cog = self.bot.get_cog('Playlist')
        await playlist_cog.delete(ctx, name)

    @group.command(name='add', description='Add a song to a playlist')
    async def add(self, interaction: discord.Interaction, name: str, url: str = None):
        ctx = await self.bot.get_context(interaction)
        playlist_cog = self.bot.get_cog('Playlist')
        await playlist_cog.add(ctx, name, url)

    @group.command(name='remove', description='Remove a song from a playlist')
    async def remove(self, interaction: discord.Interaction, name: str, song_name: str):
        ctx = await self.bot.get_context(interaction)
        playlist_cog = self.bot.get_cog('Playlist')
        await playlist_cog.remove(ctx, name, song_name)

    # FIXME: This command is not working as I intend to, cba to fix now but it's not a big deal. Works fine but won't display how many songs were loaded.
    @group.command(name='load', description='Load a playlist into the queue')
    async def load(self, interaction: discord.Interaction, playlist_name: str):
        ctx = await self.bot.get_context(interaction)
        if playlist_name.isnumeric() and int(playlist_name) <= len(os.listdir(playlist_dir(ctx.guild.id))):
                playlist_name = os.listdir(playlist_dir(ctx.guild.id))[int(playlist_name)-1][:-5]
        if not ctx.author.voice:
            await ctx.send('You are not connected to a voice channel')
            return
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        

        try:            
            playlist = get_playlist(ctx.guild.id, playlist_name)
            queue = Queues.get_queue(ctx.guild.id)
            for song in playlist:
                queue_item = {}
                queue_item['title'] = song['title']
                queue_item['url'] = song['url']
                queue.append(queue_item)
            
            
            Queues.update_queue(ctx.guild.id, queue)
            embed = discord.Embed(title=f'Loaded playlist {playlist_name}', description=f'Loaded {len(playlist)} songs into the queue', color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
            if not ctx.voice_client.is_playing():
                play_cog = self.bot.get_cog('_Player')
                await play_cog.play_song(interaction=interaction, query=None)
        except Exception as e:
            await ctx.send(f'Error loading playlist: {e}')

    async def setup(self, bot):
        await bot.tree.add_command(self.group)


async def setup(bot):
    await bot.add_cog(_Playlist(bot))

def playlist_dir(guild_id):
    return os.path.join(config.playlists_folder, str(guild_id))

def get_playlist(guild_id, playlist_name):
    with open(os.path.join(playlist_dir(guild_id), f'{playlist_name}.json'), 'r') as f:
        return json.load(f)