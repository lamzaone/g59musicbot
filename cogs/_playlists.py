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
        if playlist_name is None:
            playlist_cog = self.bot.get_cog('Playlist')
            await interaction.response.defer()
            await playlist_cog.playlist(ctx, playlist_name)
        else:
            try:
                await interaction.response.defer()
                embed = discord.Embed(title=f"Available playlists", description="", color=discord.Color.dark_magenta())
                message = await interaction.followup.send(embed=embed)
                if playlist_name.isnumeric():
                    try:
                        playlist_name = os.listdir(playlist_dir(interaction.guild.id))[int(playlist_name)-1][:-5]
                    except IndexError:
                        embed.title = ""
                        embed.description = "Playlist not found"
                        await message.edit(embed=embed)
                        return
                if type(get_playlist(interaction.guild.id, playlist_name)) == tuple:
                    playlist_name, playlist = get_playlist(interaction.guild.id, playlist_name)
                else:
                    playlist = get_playlist(interaction.guild.id, playlist_name)
                if playlist is None:
                    embed.title = ""
                    embed.description = "Playlist not found"
                    await message.edit(embed=embed)
                    return
                embed.title = f"Playlist `{playlist_name}`"
                embed.description = ""
                if len(playlist) == 0:
                    embed.description = "Playlist is empty"                    
                    await message.edit(embed=embed)
                elif len(playlist) <= 20:
                    for i, song in enumerate(playlist, start=1):
                        embed.description += f'{i}: {song["title"]}\n'                        
                    await message.edit(embed=embed)
                    await message.add_reaction('🔀')
                    await message.add_reaction('🔊')
                    await message.add_reaction('❌')
                    while True:
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == interaction.user and reaction.message.id == message.id and reaction.emoji in ['🔀', '🔊', '❌'])
                            if reaction.emoji == '🔀':
                                import random
                                random.shuffle(playlist)
                            elif reaction.emoji == '🔊':
                                queue = Queues.get_queue(interaction.guild.id)
                                for song in playlist:
                                    queue.append(song)
                                Queues.update_queue(interaction.guild.id, queue)
                                ctx = await self.bot.get_context(interaction)
                                player_cog = ctx.bot.get_cog('_Player')
                                if not ctx.author.voice:
                                    await ctx.send(':x: You are not connected to a voice channel')
                                    return
                                if ctx.voice_client is None:
                                    await ctx.author.voice.channel.connect()
                                if not ctx.voice_client.is_playing():
                                    await message.delete()
                                    await ctx.send(f'Playlist `{playlist_name}` loaded {len(playlist)} songs to queue and started playing')
                                    await player_cog.play_song(interaction=interaction, query=None)
                                    return
                                else:
                                    await message.delete()
                                    await ctx.send(f'Playlist `{playlist_name}` loaded {len(playlist)} songs to queue')
                                    return
                            elif reaction.emoji == '❌':
                                await message.delete()
                                return
                            await message.remove_reaction(reaction, user)
                            embed.description = ""
                            for i, song in enumerate(playlist, start=1):
                                embed.description += f'{i}: {song["title"]}\n'
                            await message.edit(embed=embed)
                        except asyncio.CancelledError:
                            await message.delete()
                            return
                        except asyncio.TimeoutError:
                            await message.delete()
                            return
                        except UnboundLocalError:      
                            ctx.voice_client.stop()
                            ctx.voice_client.disconnect()
                            return None
                else:
                    def get_chunk(playlist, page):
                        return playlist[page*20:(page+1)*20]
                    page = 0
                    for i, song in enumerate(get_chunk(playlist, page), start=1):
                        embed.description += f'{i}: {song["title"]}\n'
                    embed.set_footer(text=f'Page {page+1}/{len(playlist)//20+1}')
                    await message.edit(embed=embed)
                    await message.add_reaction('⬅️')
                    await message.add_reaction('➡️')
                    await message.add_reaction('🔀')
                    await message.add_reaction('🔊')
                    await message.add_reaction('❌')
                    while True:
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == interaction.user and reaction.message.id == message.id and reaction.emoji in ['⬅️', '➡️', '🔀', '🔊', '❌'])
                            if reaction.emoji == '⬅️':
                                page -= 1
                                if page < 0:
                                    page = len(playlist)//20
                            elif reaction.emoji == '➡️':
                                page += 1
                                if page > len(playlist)//20:
                                    page = 0
                            elif reaction.emoji == '🔀':
                                import random
                                random.shuffle(playlist)
                            elif reaction.emoji == '🔊':
                                queue = Queues.get_queue(interaction.guild.id)
                                for song in playlist:
                                    queue.append(song)
                                Queues.update_queue(interaction.guild.id, queue)
                                ctx = await self.bot.get_context(interaction)
                                player_cog = ctx.bot.get_cog('_Player')
                                if not ctx.author.voice:
                                    await ctx.send('You are not connected to a voice channel')
                                    return
                                if ctx.voice_client is None:
                                    await ctx.author.voice.channel.connect()
                                if not ctx.voice_client.is_playing():
                                    await message.delete()
                                    await ctx.send(f'Playlist `{playlist_name}` loaded {len(playlist)} songs to queue and started playing')
                                    await player_cog.play_song(interaction=interaction, query=None)
                                    return
                                else:
                                    await message.delete()
                                    await ctx.send(f'Playlist `{playlist_name}` loaded {len(playlist)} songs to queue')
                                    return
                            elif reaction.emoji == '❌':
                                await message.delete()
                                return
                            await message.remove_reaction(reaction, user)
                            embed.description = ""
                            embed.set_footer(text=f'Page {page+1}/{len(playlist)//20+1}')
                            for i, song in enumerate(get_chunk(playlist, page), start=1):
                                embed.description += f'{i+(page*20)}: {song["title"]}\n'
                            await message.edit(embed=embed)
                        except asyncio.CancelledError:
                            await message.delete()
                            return
                        except asyncio.TimeoutError:
                            await message.delete()
                            return
                await message.edit(embed=embed)
            except FileNotFoundError:
                await message.edit(content='Playlist not found')

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

    @group.command(name='load', description='Load a playlist into the queue')
    async def load(self, interaction: discord.Interaction, playlist_name: str):
        ctx = await self.bot.get_context(interaction)
        if not ctx.author.voice:
            await ctx.send('You are not connected to a voice channel')
            return
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        

        try:            
            if playlist_name.isnumeric():
                try:
                    playlist_name = os.listdir(playlist_dir(interaction.guild.id))[int(playlist_name)-1][:-5]
                except IndexError:
                    await ctx.send('Playlist not found')
                    return
            if type(get_playlist(interaction.guild.id, playlist_name)) == tuple:
                playlist_name, playlist = get_playlist(interaction.guild.id, playlist_name)
            else:
                playlist = get_playlist(interaction.guild.id, playlist_name)
            if playlist is None:
                await ctx.send('Playlist not found')
                return
            queue = Queues.get_queue(interaction.guild.id)
            for song in playlist:
                queue_item = {}
                queue_item['title'] = song['title']
                queue_item['url'] = song['url']
                queue.append(queue_item)
            
            
            Queues.update_queue(interaction.guild.id, queue)
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
    try:
        with open(os.path.join(playlist_dir(guild_id), f'{playlist_name}.json'), 'r') as f:
            return json.load(f)        
    except FileNotFoundError:
        try:
            #get all playlists in the guild and look for the one that matches the name the most
            playlists = os.listdir(playlist_dir(guild_id))
            closest_match = None
            closest_match_score = 0
            for playlist in playlists:
                score = 0
                for i in range(min(len(playlist), len(playlist_name))):
                    if playlist[i].lower() == playlist_name[i].lower():
                        score += 1
                if score > closest_match_score:
                    closest_match = playlist
                    closest_match_score = score
            if closest_match_score/len(playlist) > 0.5:
                with open(os.path.join(playlist_dir(guild_id), closest_match), 'r') as f:
                    return closest_match[:-5], json.load(f)
            else:
                return None
        except FileNotFoundError:
            return None
        except TypeError:
            return None