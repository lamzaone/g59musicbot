import datetime
import math
import discord
from discord.ext import commands
from config import config
from utils import serversettings as Settings, queues as Queues, musicplayer
import os
import asyncio
import yt_dlp
import json
import random

is_windows = os.name == 'nt'

class Player(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    async def has_dj_role(ctx):
        # Get the role from your settings
        dj_role = Settings.get_dj_role(ctx.guild.id)
        role = discord.utils.get(ctx.guild.roles, id=dj_role)
        app_info = await ctx.bot.application_info()
        owner = app_info.owner
        return role in ctx.author.roles or ctx.author.guild_permissions.administrator or ctx.author.id == owner.id





    @commands.command(name='play', help='Play music from YouTube using a search term or URL')
    @commands.guild_only()
    async def play(self, ctx, *, query: str = None):
        if not hasattr(ctx.bot, 'repeat'):
            ctx.bot.repeat = "no"
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(":x: You are not connected to a voice channel.")
                return
        
            try:
                if "list=" in query:
                    OPTS={
                        'extract_flat': True,
                        'noplaylist': False,                        
                        'no_warnings': True,                   
                    }
                    if "watch?v=" in query or 'youtu.be' in query or "youtube.com" in query:
                        message = await ctx.send("This song is part of a playlist. Do you want to add the entire playlist to the queue?")
                        await message.add_reaction("✅")
                        await message.add_reaction("❌")
                        reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=lambda reaction, user: user == ctx.author and reaction.message == message)
                        try:
                            if reaction.emoji == "✅":
                                aux_query = query
                                query = query.split("list=")[1]
                                query = f"https://www.youtube.com/playlist?list={query}"
                                with yt_dlp.YoutubeDL(OPTS) as ydl:
                                    try:
                                        search_results = ydl.extract_info(query, download=False)['entries']
                                                                    
                                        queue = Queues.get_queue(ctx.guild.id)
                                        for video in search_results:
                                            queue.append({'title': video['title'], 'url': video['url']})
                                        Queues.update_queue(ctx.guild.id, queue)
                                        await ctx.send(f":white_check_mark: Added `{len(search_results)}` songs to the queue.")
                                        query=None
                                    except yt_dlp.DownloadError:                            
                                        query = aux_query
                            else:
                                pass
                        except asyncio.CancelledError:
                            await message.delete()
                            return
                        except asyncio.TimeoutError:
                            await message.delete()
                            return
                    
            except Exception as e:
                print("error"+e)
        
        async with ctx.typing():
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                try:
                    if "list=" in query:
                        OPTS={
                            'extract_flat': True,
                            'noplaylist': False,                        
                            'no_warnings': True,                   
                        }
                        if "watch?v=" in query or 'youtu.be' in query or "youtube.com" in query:
                            message = await ctx.send("This song is part of a playlist. Do you want to add the entire playlist to the queue?")
                            await message.add_reaction("✅")
                            await message.add_reaction("❌")
                            try:
                                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=lambda reaction, user: user == ctx.author and reaction.message == message)
                                if reaction.emoji == "✅":
                                    aux_query = query
                                    query = query.split("list=")[1]
                                    query = f"https://www.youtube.com/playlist?list={query}"
                                    with yt_dlp.YoutubeDL(OPTS) as ydl:
                                        try:
                                            search_results = ydl.extract_info(query, download=False)['entries']
                                                                        
                                            queue = Queues.get_queue(ctx.guild.id)
                                            for video in search_results:
                                                queue.append({'title': video['title'], 'url': video['url']})
                                            Queues.update_queue(ctx.guild.id, queue)
                                            await ctx.send(f":white_check_mark: Added `{len(search_results)}` songs to the queue.")
                                            query=None
                                        except yt_dlp.DownloadError:                            
                                            query = aux_query
                                else:
                                    pass
                            except asyncio.CancelledError:
                                await message.delete()
                                return
                            except asyncio.TimeoutError:
                                await message.delete()
                                return
                        
                except Exception as e:
                    print("error"+e)
            
                if query is None:
                    return
                try:
                    if ctx.voice_client.is_paused():
                        await ctx.send("reminder: Music is currently paused. use `/pause` to resume")
                    info = musicplayer.get_info(query)
                    queue = Queues.get_queue(ctx.guild.id)
                    queue.append({'title': info['title'], 'url': info['original_url']})
                    Queues.update_queue(ctx.guild.id, queue)
                    await ctx.send(f":white_check_mark: Added `{info['title']}` to the queue.")
                    return
                except Exception as e:
                    print(f"[-] An error occurred while adding to queue: {e}")
                    await ctx.send(":x: An error occurred while adding the song to the queue.") 
                    return
                except TypeError:
                    pass
            info = None
            while info is None:
                if query is None:
                    info = musicplayer.get_info(Queues.next_song(ctx.guild.id)['url'])
                else:
                    info = musicplayer.get_info(query)
                if info is None:
                    info = musicplayer.get_info(Queues.next_song(ctx.guild.id)['url'])
            
            ctx.bot.video_info = info
            ctx.bot.video_url = info['url']
            
            if is_windows:
                audio_source = discord.FFmpegPCMAudio(info['url'], executable=config.FFMPEG_PATH, **config.ffmpeg_options)
            else:
                audio_source = discord.FFmpegPCMAudio(info['url'], **config.ffmpeg_options)
            audio_source = discord.PCMVolumeTransformer(audio_source, Settings.get_settings(ctx.guild.id)['volume'])
            ctx.voice_client.play(audio_source)
            ctx.bot.audio_start_time = datetime.datetime.now()
            await ctx.send(f":arrow_forward: Now playing `{info['title']}` \n{info['original_url']}")
        
        try:
            while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                await asyncio.sleep(1)
            queue = Queues.get_queue(ctx.guild.id)
            if len(queue) > 0 or ctx.bot.repeat != "no":
                try:
                    if ctx.bot.repeat == "song":                    
                        next_song = ctx.bot.video_info['original_url']
                    elif ctx.bot.repeat == "queue":
                        next_song = Queues.repeat_queue(ctx.guild.id, ctx.bot.video_info)['url']
                    else:
                        next_song = Queues.next_song(ctx.guild.id)['url']
                    await self.play(ctx, query=next_song)
                except UnboundLocalError:
                    await ctx.voice_client.disconnect()
                    pass
            else:
                await ctx.voice_client.disconnect()
        except Exception as e:
            print(f"[-] An error occurred while playing music: {e}")


    ### REPEAT COMMAND ###
    @commands.hybrid_group(name='repeat', fallback='queue', help='repeat the current song or the entire queue', invoke_without_command=True, aliases=['loop'])
    async def repeat(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if ctx.bot.repeat == "queue" or ctx.bot.repeat == "song":
                ctx.bot.repeat = "no"
                await ctx.send(":repeat: Repeating has been disabled.")
            elif len(Queues.get_queue(ctx.guild.id)) > 0:
                ctx.bot.repeat = "queue"
                await ctx.send(":repeat: Repeating the queue.")
            else:
                ctx.bot.repeat = "song"
                await ctx.send(":repeat: Repeating the current song.")
        else:
            await ctx.send(":x: No music is currently playing.")

    @repeat.command(name='song', help='repeat the current song')
    async def repeat_song(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if ctx.bot.repeat == "song":
                ctx.bot.repeat = "no"
                await ctx.send(":repeat: Repeating has been disabled.")
            else:
                ctx.bot.repeat = "song"
                await ctx.send(":repeat: Repeating the current song.")
        else:
            await ctx.send(":x: No music is currently playing.")


    ### NOW PLAYING COMMAND ###
    @commands.hybrid_command(name='nowplaying', help='Display the currently playing song', aliases=['np', 'playing'])
    @commands.guild_only()
    async def nowplaying(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            info = ctx.bot.video_info
            embed = discord.Embed(color=discord.Color.blurple())
            duration = musicplayer.format_duration(info['duration'])
            uploaded = musicplayer.format_upload_date(info['upload_date'])
            embed.description = f"### [:loud_sound: {info['title']}]({info['original_url']})\nDuration: `{duration}` | Likes: `{info['like_count']}` | Uploaded: `{uploaded}`"
            embed.set_thumbnail(url=info['thumbnail'])
            embed.description += f"\n**Uploaded by:** {info['uploader']}"
            message = await ctx.send(embed=embed)
            try:
                while ctx.voice_client.is_playing():
                    startTime=ctx.bot.audio_start_time
                    currentTime=datetime.datetime.now()
                    elapsed = musicplayer.get_elapsed(startTime, currentTime)
                    embed.set_footer(text=f"{elapsed}/{duration}")
                    await message.edit(embed=embed)
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                await message.delete()
                return
            except Exception as e:
                print(f"[-] An error occurred while updating the now playing message: {e}")
                await message.delete()
                return
        else:
            await ctx.send(":x: No music is currently playing.")


    ### SKIP COMMAND ###
    @commands.command(name='skip', help='Skip the current song and play the next one in the queue')
    @commands.guild_only()
    async def skip(self, ctx, to: int = 0):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if to > 0:
                queue = Queues.get_queue(ctx.guild.id)
                if len(queue) >= to:
                    queue[0], queue[to-1] = queue[to-1], queue[0]
                    Queues.update_queue(ctx.guild.id, queue)
                    ctx.voice_client.stop()
                    return await ctx.send(f":fast_forward: Skipped to song `{to}` in the queue.")
                else:
                    await ctx.send(":x: Invalid song number.")
            ctx.voice_client.stop()
            await ctx.send(":fast_forward: Skipped the current song.")
        else:
            await ctx.send(":x: No music is currently playing.")


    ### STOP COMMAND ###
    @commands.command(name='stop', help='Stop playing music and disconnect from voice channel')
    @commands.guild_only()
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_connected():
            Queues.update_queue(ctx.guild.id, [])
            ctx.voice_client.stop()
            await ctx.send(":octagonal_sign: Music stopped and queue has been cleared.")
        else:
            await ctx.send(":x: No music is currently playing.")

            
    ### PAUSE COMMAND ###
    @commands.command(name='pause', help='Pause the currently playing music')
    @commands.guild_only()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send(":pause_button: Music paused.")
        elif ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send(":arrow_forward: Music resumed.")


    ### VOLUME COMMAND ###
    @commands.command(name='volume', help='Set the volume of the music')
    @commands.guild_only()
    @commands.check(has_dj_role)
    async def _volume(self, ctx, volume: int = None):
        settings = Settings.get_settings(ctx.guild.id)

        if volume is None:
            await ctx.send(":loud_sound: Current volume is `" + str(round(settings['volume'] * 100)) + "%`")
            return
        
        elif volume < 0 or volume > 100:
            await ctx.send(":loud_sound: Volume must be between `0-100` you dummy...")
            return

        current_volume = settings['volume'] * 100
        settings['volume'] = volume / 100
        Settings.set_guild_settings(ctx.guild.id, settings)

        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.source.volume = volume / 100

        await ctx.send(f":loud_sound: Volume set from `{round(current_volume)}%` to `{volume}%`")

    ### SEEK COMMAND ###
    @commands.command(name='seek', help='Set the playback position to a specific time in seconds')
    @commands.guild_only()
    async def seek(self, ctx, seconds: int):
        try:
            if ctx.voice_client and ctx.voice_client.is_playing():
                # Stop the current playback

                # Check if there's stored video information
                if hasattr(ctx.bot, 'video_info') and hasattr(ctx.bot, 'video_url'):
                    # Add the offset in seconds to the FFmpeg options to fast forward
                    settings = Settings.get_settings(ctx.guild.id)
                    seek_time = f"-ss {seconds}"
                    ffmpeg_opts = {**config.ffmpeg_options, "options": f"{config.ffmpeg_options['options']} {seek_time}"}
                    async with ctx.typing():
                        if is_windows:
                            audio_source = discord.FFmpegPCMAudio(ctx.bot.video_url, executable=config.FFMPEG_PATH , **ffmpeg_opts)
                            ctx.bot.audio_start_time = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
                        else:
                            audio_source = discord.FFmpegPCMAudio(ctx.bot.video_url, **ffmpeg_opts)
                        audio_source = discord.PCMVolumeTransformer(audio_source, settings['volume'])
                    ctx.voice_client.stop()
                    ctx.voice_client.play(audio_source)

                    await ctx.send(f":arrow_forward: Started playing at {seconds} seconds.")
                else:
                    await ctx.send(":x: No music data available to seek.")
            else:
                await ctx.send(":x: No music is currently playing.")
        except Exception as e:
            print(f"[-] An error occurred while seeking: {e}")

    ### YOUTUBE SEARCH ###
    @commands.command(name='search', help='Search for a song on YouTube')
    @commands.guild_only()
    async def search(self, ctx, query:str, limit:int=4):
        embed = discord.Embed(title=f"Searching for `{query}`", color=discord.Color.blurple())
        message = await ctx.send(embed=embed)
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        try:
            
            OPTS = config.YTDL_OPTS.copy()
            OPTS['extract_flat'] = True
            with yt_dlp.YoutubeDL(OPTS) as ydl:
                search_results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)['entries']
                embed.title = f"Search results for `{query}`"
                embed.description = ""
                
            for i, result in enumerate(search_results):
                embed.description += f"{i+1}: [{result['title']}]({result['url']})\n"
                await message.edit(embed=embed)

            for i in range(len(search_results)):
                await message.add_reaction(reactions[i])
            
            reaction = await self.bot.wait_for('reaction_add', timeout=30.0, check=lambda reaction, user: user == ctx.author and reaction.message == message)
            index = reactions.index(reaction[0].emoji)        
            await message.delete()
            await self.play(ctx, query=search_results[index]['url'])
        except asyncio.CancelledError:
            await message.delete()    
            return
        except asyncio.TimeoutError:
            await message.delete()
            return
        except Exception as e:  
            embed.title = "Error"
            embed.description = f"An error occurred while searching: {str(e)}"
            await message.edit(embed=embed)


    ### QUEUE SHUFFLE COMMAND ###
    @commands.command(name='shuffle', help='Shuffle the current queue')
    @commands.guild_only()
    async def shuffle(self, ctx):
        queue = Queues.get_queue(ctx.guild.id)
        if len(queue) > 0:
            import random
            random.shuffle(queue)
            Queues.update_queue(ctx.guild.id, queue)
            await ctx.send(":twisted_rightwards_arrows: Queue has been shuffled.")
        else:
            await ctx.send(":x: The queue is empty.")
    
    @commands.command(name='queue', help='Display the current queue')
    @commands.guild_only()
    async def queue(self, ctx):
        try:
            queue = Queues.get_queue(ctx.guild.id)
            if len(queue) > 0:
                embed = discord.Embed(title="Queue", color=discord.Color.blurple())
                
                if len(queue) >= 20:
                    page = 0
                    # get the queue in chunks of 20
                    def get_chunk(queue, page):
                        return queue[page*20:page*20+20]        
                    chunk = get_chunk(queue, page)

                    embed.description = ""
                    for i, song in enumerate(chunk):
                        embed.description += f"{i+1}: [{song['title']}]({song['url']})\n"
                    embed.set_footer(text=f"Page {page+1} of {math.ceil(len(queue)/20)}")
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('◀️')
                    await message.add_reaction('▶️')
                    await message.add_reaction('🔄')
                    await message.add_reaction('❌')

                    def check(reaction, user):
                        return user == ctx.author and reaction.message == message
                    
                    while True:
                        try:
                            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                            if reaction.emoji == '▶️':
                                page += 1
                                if page > math.ceil(len(queue)/20)-1:
                                    page = 0
                                chunk = get_chunk(queue, page)
                                embed.description = ""
                                for i, song in enumerate(chunk):
                                    embed.description += f"{i+1+(page*20)}: [{song['title']}]({song['url']})\n"
                                embed.set_footer(text=f"Page {page+1} of {math.ceil(len(queue)/20)}")
                                await message.edit(embed=embed)
                                await message.remove_reaction(reaction.emoji, ctx.author)
                            elif reaction.emoji == '◀️':
                                page -= 1
                                if page < 0:
                                    page = math.ceil(len(queue)/20)-1
                                chunk = get_chunk(queue, page)
                                embed.description = ""
                                for i, song in enumerate(chunk):
                                    embed.description += f"{i+1+(page*20)}: [{song['title']}]({song['url']})\n"
                                embed.set_footer(text=f"Page {page+1} of {math.ceil(len(queue)/20)}")
                                await message.edit(embed=embed)
                                await message.remove_reaction(reaction.emoji, ctx.author)
                            elif reaction.emoji == '🔄':
                                import random
                                random.shuffle(queue)
                                Queues.update_queue(ctx.guild.id, queue)
                                chunk = get_chunk(queue, page)
                                embed.description = ""
                                for i, song in enumerate(chunk):
                                    embed.description += f"{i+1+(page*20)}: [{song['title']}]({song['url']})\n"
                                embed.set_footer(text=f"Page {page+1} of {math.ceil(len(queue)/20)}")
                                await message.edit(embed=embed)
                                await message.remove_reaction(reaction.emoji, ctx.author)
                            elif reaction.emoji == '❌':
                                await message.delete()
                                break
                        except asyncio.CancelledError:
                            await message.delete()
                            return
                        except asyncio.TimeoutError:
                            await message.delete()
                            return
                else:
                    # if the queue is less than 20 songs, display the entire queue
                    embed.description = ""
                    for i, song in enumerate(queue):
                        embed.description += f"{i+1}: [{song['title']}]({song['url']})\n"
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('🔄')
                    await message.add_reaction('❌')
                    def check(reaction, user):
                        return user == ctx.author and reaction.message == message
                    
                    while True:
                        try:
                            reaction, _ = await self.bot.wait_for('reaction_add', timeout=3600.0, check=check)
                            if reaction.emoji == '🔄':
                                import random
                                random.shuffle(queue)
                                Queues.update_queue(ctx.guild.id, queue)
                                embed.description = ""
                                for i, song in enumerate(queue):
                                    embed.description += f"{i+1}: [{song['title']}]({song['url']})\n"
                                await message.edit(embed=embed)
                                await message.remove_reaction(reaction.emoji, ctx.author)
                            
                            elif reaction.emoji == '❌':
                                await message.delete()
                        except asyncio.CancelledError:
                            await message.delete()
                            return
                        except asyncio.TimeoutError:
                            await message.delete()
                            return
            else:
                await ctx.send(":x: The queue is empty.")
        except Exception as e:
            print(f"[-] An error occurred while displaying the queue: {e}")

    ### SET DJ ROLE COMMAND ###
    @commands.command(name='setdj', help='Set the DJ role for the server')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def set_dj(self, ctx, role: discord.Role = None):
        if role is None: ## get dj role name from id
            await ctx.send(f"Current DJ role: <@&{str(Settings.get_dj_role(ctx.guild.id))}>") 
            return
        settings = Settings.get_settings(ctx.guild.id)
        settings['dj_role'] = role.id
        Settings.set_guild_settings(ctx.guild.id, settings)
        await ctx.send(f":white_check_mark: DJ role set to `{role.name}`")

    @commands.hybrid_command(name='remove', help='Remove a song (or multiple ex: 4-10 [from 4 to 10]) from the queue', aliases=['delete'])
    @commands.guild_only()
    async def remove(self, ctx, index: str):
        try:
            queue = Queues.get_queue(ctx.guild.id)
            if len(queue) > 0:
                if "-" in index:
                    start, end = index.split("-")
                    start = int(start)-1
                    end = int(end)
                    if start < 0 or end > len(queue):
                        return await ctx.send(":x: Invalid range.")
                    queue = queue[:start] + queue[end:]
                else:
                    index = int(index)-1
                    if index < 0 or index > len(queue)-1:
                        return await ctx.send(":x: Invalid song number.")
                    queue.pop(index)
                Queues.update_queue(ctx.guild.id, queue)
                await ctx.send(":white_check_mark: Song(s) removed from the queue.")
            else:
                await ctx.send(":x: The queue is empty.")
        except ValueError:
            await ctx.send(":x: Invalid input.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))

