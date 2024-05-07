import discord
from discord.ext import commands
import os
from config import config
import json
from utils import queues as Queues, musicplayer
from cogs import player
import asyncio
import yt_dlp
import math

class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def initialize_playlists(self, guilds: list):
        for guild in guilds:
            #check if playlist dir exists, if not create it
            os.makedirs(os.path.join(playlist_dir(guild.id)), exist_ok=True)
    
    
        
    @commands.group(name='playlist', aliases=['pl'], help="!help playlist", invoke_without_command=True)
    #index or name of playlist to load
    async def playlist(self, ctx, playlist_name: str=None):
        embed = discord.Embed(title=f"Available playlists", description="", color=discord.Color.dark_magenta())
        message = await ctx.send(embed=embed)
        if playlist_name is None:
                embed.color = discord.Color.blurple()
                embed.title = "Available playlists"
                playlists = os.listdir(playlist_dir(ctx.guild.id))
                if len(playlists) == 0:
                    embed.description = "No playlists found"
                    message.edit(embed=embed)
                elif len(playlists) <= 7:
                    embed.description = '\n'.join([f'{i+1}: {playlist[:-5]}' for i, playlist in enumerate(playlists)])
                    await message.edit(embed=embed)
                else:
                    page = 0
                    def get_chunk(playlists, page):
                        return playlists[page*7:(page+1)*7]
                    embed.description = '\n'.join([f'{i+1}: {playlist[:-5]}' for i, playlist in enumerate(get_chunk(playlists, page))])
                    await message.edit(embed=embed)
                    await message.add_reaction('⬅️')
                    await message.add_reaction('➡️')
                    while True:
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == ctx.author and reaction.message.id == message.id and reaction.emoji in ['⬅️', '➡️'])
                            if reaction.emoji == '⬅️':
                                page -= 1
                                if page < 0:
                                    page = len(playlists)//7
                            elif reaction.emoji == '➡️':
                                page += 1
                                if page > len(playlists)//7:
                                    page = 0
                            embed.description = '\n'.join([f'{i+1+page*7}: {playlist[:-5]}' for i, playlist in enumerate(get_chunk(playlists, page))])
                            await message.edit(embed=embed)
                            await message.remove_reaction(reaction.emoji, user)
                        except asyncio.TimeoutError:
                            pass
                            
                        except asyncio.TimeoutError:
                            break
                    

                
                return    
        try:
            if playlist_name.isnumeric():
                playlist_name = os.listdir(playlist_dir(ctx.guild.id))[int(playlist_name)-1][:-5]
            playlist = get_playlist(ctx.guild.id, playlist_name)
            embed.title = f"Playlist `{playlist_name}`"
            embed.description = ""
            if len(playlist) == 0:
                embed.description = "Playlist is empty"
            elif len(playlist) <= 20:
                for i, song in enumerate(playlist, start=1):
                    embed.description += f'{i}: {song["title"]}\n'
            else:
                def get_chunk(playlist, page):
                    return playlist[page*20:(page+1)*20]
                page = 0
                for i, song in enumerate(get_chunk(playlist, page), start=1):
                    embed.description += f'{i}: {song["title"]}\n'
                embed.set_footer(text=f'Page {page+1}/{math.ceil(len(playlist)/20)}')
                await message.edit(embed=embed)
                await message.add_reaction('⬅️')
                await message.add_reaction('➡️')
                await message.add_reaction('🔀')
                await message.add_reaction('🔊')
                await message.add_reaction('❌')
                while True:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == ctx.author and reaction.message.id == message.id and reaction.emoji in ['⬅️', '➡️', '🔀', '🔊', '❌'])
                    if reaction.emoji == '⬅️':
                        page -= 1
                        if page < 0:
                            page = math.ceil(len(playlist)/20)-1
                    elif reaction.emoji == '➡️':
                        page += 1                        
                        if page > math.ceil(len(playlist)/20)-1:
                            page = 0
                    elif reaction.emoji == '🔀':
                        import random
                        random.shuffle(playlist)
                    elif reaction.emoji == '🔊':
                        queue = Queues.get_queue(ctx.guild.id)
                        for song in playlist:
                            queue.append(song)
                        Queues.update_queue(ctx.guild.id, queue)
                        player_cog = ctx.bot.get_cog('Player')
                        if not ctx.author.voice:
                            await ctx.send('You are not connected to a voice channel')
                            return
                        if ctx.voice_client is None:
                            await ctx.author.voice.channel.connect()
                        if not ctx.voice_client.is_playing():
                            message.delete()
                            await player_cog.play(ctx)
                            return
                        message
                    elif reaction.emoji == '❌':
                        await message.delete()
                        return
                    await message.remove_reaction(reaction, user)
                    embed.description = ""
                    embed.set_footer(text=f'Page {page+1}/{math.ceil(len(playlist)/20)}')
                    for i, song in enumerate(get_chunk(playlist, page), start=1):
                        embed.description += f'{i+(page*20)}: {song["title"]}\n'
                    await message.edit(embed=embed)
            await message.edit(embed=embed)
        except FileNotFoundError:
            await message.edit(content='Playlist not found')



    @playlist.command(name='create', aliases=['c'], brief='Create a new playlist')
    async def create(self, ctx, name: str):
        try: 
            create_playlist(ctx.guild.id, name)
            await ctx.send(f'Playlist `{name}` created successfully')
        except Exception as e:
            await ctx.send(f'Error creating playlist: {e}')
    
    @playlist.command(name='delete', aliases=['d'], brief='Delete a playlist')
    async def delete(self, ctx, playlist_name: str):
        try:
            if playlist_name.isnumeric() and int(playlist_name) <= len(os.listdir(playlist_dir(ctx.guild.id))):
                playlist_name = os.listdir(playlist_dir(ctx.guild.id))[int(playlist_name)-1][:-5]
            os.remove(os.path.join(playlist_dir(ctx.guild.id), f'{playlist_name}.json'))
            await ctx.send(f'Playlist `{playlist_name}` removed successfully')
        except FileNotFoundError:
            await ctx.send('Playlist not found')
        except Exception as e:
            await ctx.send(f'Error removing playlist: {e}')
        
    @playlist.command(name='add', aliases=['a'], brief='Add a song to a playlist')
    async def add(self, ctx, playlist_name: str, query: str=None):
        if playlist_name.isnumeric() and int(playlist_name) <= len(os.listdir(playlist_dir(ctx.guild.id))):
                playlist_name = os.listdir(playlist_dir(ctx.guild.id))[int(playlist_name)-1][:-5]
        if query is None:
            if not hasattr(ctx, 'voice_client') and ctx.voice_client.is_playing():
                await ctx.send('No song playing, please provide a query')
                return
            else:
                try:
                    info = ctx.bot.video_info
                    title = info['title']
                    url = info['original_url']
                    print(title, url)
                    add_to_playlist(ctx.guild.id, playlist_name, title, url)
                    await ctx.send(f'Song `{title}` added to playlist `{playlist_name}`')
                except Exception as e:
                    await ctx.send(f'Error adding song to playlist: {e}')
        else:
            try:
                if "list=" in query:
                    OPTS={
                        'extract_flat': True,
                        'noplaylist': False,                        
                        'no_warnings': True,                   
                    }
                    if "watch?v=" in query:
                        message = await ctx.send("This song is part of a youtube playlist. Do you want to add the entire playlist to your playlist?")
                        await message.add_reaction("✅")
                        await message.add_reaction("❌")
                        reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=lambda reaction, user: user == ctx.author and reaction.message == message)
                        if reaction.emoji == "✅":
                            aux_query = query
                            query = query.split("list=")[1]
                            query = f"https://www.youtube.com/playlist?list={query}"
                            with yt_dlp.YoutubeDL(OPTS) as ydl:
                                try:
                                    search_results = ydl.extract_info(query, download=False)['entries']
                                                                
                                    for search_result in search_results:
                                        title = search_result['title']
                                        url = search_result['url']
                                        add_to_playlist(ctx.guild.id, playlist_name, title, url)                                    
                                    await ctx.send(f'Added {len(search_results)} songs to playlist `{playlist_name}`')
                                except yt_dlp.DownloadError:                            
                                    query = aux_query
                            return
                        else:
                            pass
                    
            except Exception as e:
                print("error"+e)


            info=musicplayer.get_info(query)
            if info is None:
                await ctx.send('No results found')
                return
            else:
                title = info['title']
                url = info['original_url']
                add_to_playlist(ctx.guild.id, playlist_name, title, url)
                await ctx.send(f'Song `{title}` added to playlist `{playlist_name}`')

    @playlist.command(name='remove', aliases=['r'], brief='Remove a song from a playlist')
    async def remove(self, ctx, playlist_name: str, song_name: str):
        if playlist_name.isnumeric() and int(playlist_name) <= len(os.listdir(playlist_dir(ctx.guild.id))):
                playlist_name = os.listdir(playlist_dir(ctx.guild.id))[int(playlist_name)-1][:-5]
        try:
            removed_song = remove_from_playlist(ctx.guild.id, playlist_name, song_name)
            if removed_song is not None:
                await ctx.send(f'Song `{removed_song}` removed from playlist `{playlist_name}`')
            else:
                await ctx.send(f'Song `{song_name}` not found in playlist `{playlist_name}`')
        except FileNotFoundError:
            await ctx.send('Playlist not found')

    @playlist.command(name='load', aliases=['l'], brief='Load a playlist into the queue')
    async def load(self, ctx, playlist_name: str):
        if not ctx.author.voice:
            await ctx.send('You are not connected to a voice channel')
            return
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        try:
            if playlist_name.isnumeric() and int(playlist_name) <= len(os.listdir(playlist_dir(ctx.guild.id))):
                playlist_name = os.listdir(playlist_dir(ctx.guild.id))[int(playlist_name)-1][:-5]            
            playlist = get_playlist(ctx.guild.id, playlist_name)
            queue = Queues.get_queue(ctx.guild.id)
            for song in playlist:
                queue_item = {}
                queue_item['title'] = song['title']
                queue_item['url'] = song['url']
                queue.append(queue_item)
            embed = discord.Embed(title=f'Loaded playlist {playlist_name}', description=f'Loaded {len(playlist)} songs into the queue', color=discord.Color.green())    
            await ctx.send(embed=embed)
            
            Queues.update_queue(ctx.guild.id, queue)
            if not ctx.voice_client.is_playing():
                player_cog = ctx.bot.get_cog('Player')
                song_url = queue.pop(0).get('url')
                await player_cog.play(ctx)
        except Exception as e:
            await ctx.send(f'Error loading playlist: {e}')
            


        except FileNotFoundError:
            await ctx.send('Playlist not found')
        except Exception as e:
            await ctx.send(f'Error loading playlist: {e}')



async def setup(bot):
    await bot.add_cog(Playlist(bot))

def playlist_dir(guild_id):
    return os.path.join(config.playlists_folder, str(guild_id))

def create_playlist(guild_id, name):
    os.makedirs(playlist_dir(guild_id), exist_ok=True)
    with open(os.path.join(playlist_dir(guild_id), f'{name}.json'), 'w') as f:
        f.write('[]')


def add_to_playlist(guild_id, playlist_name, song_name, song_url):
    with open(os.path.join(playlist_dir(guild_id), f'{playlist_name}.json'), 'r') as f:
        playlist = json.load(f)
        song = {}
        song['title'] = song_name
        song['url'] = song_url
        playlist.append(song)
    with open(os.path.join(playlist_dir(guild_id), f'{playlist_name}.json'), 'w') as f:
        json.dump(playlist, f, indent=4)

def get_playlist(guild_id, playlist_name):
    with open(os.path.join(playlist_dir(guild_id), f'{playlist_name}.json'), 'r') as f:
        return json.load(f)
    
def remove_from_playlist(guild_id, playlist_name, song_name):
    playlist = get_playlist(guild_id, playlist_name)
    for song in playlist:
        if song_name.lower() in song['title'].lower():
            playlist.remove(song)
            with open(os.path.join(playlist_dir(guild_id), f'{playlist_name}.json'), 'w') as f:
                json.dump(playlist, f, indent=4)
            return song['title']
    return None
