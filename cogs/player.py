import discord
from discord.ext import commands
from config import config
from utils import serversettings as Settings, queues as Queues, musicplayer
import os
import asyncio
import yt_dlp
import json

is_windows = os.name == 'nt'

class Player(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    def has_dj_role(ctx):
        # Get the role from your settings
        dj_role = Settings.get_dj_role(ctx.guild.id)
        role = discord.utils.get(ctx.guild.roles, id=dj_role)
        return role in ctx.author.roles or ctx.author.guild_permissions.administrator


    @commands.command(name='play', help='Play music from YouTube using a search term or URL')
    @commands.guild_only()
    async def play(self, ctx, *, query: str = None):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(":x: You are not connected to a voice channel.")
                return
        
        async with ctx.typing():
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                if query is None:
                    await ctx.send(":x: Music is already playing. Use `/skip` to play the next song.")
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
            if query is None:
                info = musicplayer.get_info(Queues.next_song(ctx.guild.id)['url'])
            else:
                info = musicplayer.get_info(query)
            ctx.bot.video_info = info
            ctx.bot.video_url = info['url']
            if is_windows:
                audio_source = discord.FFmpegPCMAudio(info['url'], executable=config.FFMPEG_PATH, **config.ffmpeg_options)
            else:
                audio_source = discord.FFmpegPCMAudio(info['url'], **config.ffmpeg_options)
            audio_source = discord.PCMVolumeTransformer(audio_source, Settings.get_settings(ctx.guild.id)['volume'])
            ctx.voice_client.play(audio_source)
            await ctx.send(f":arrow_forward: Now playing `{info['title']}` \n{info['original_url']}")
        
        try:
            while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                await asyncio.sleep(1)
            queue = Queues.get_queue(ctx.guild.id)
            if len(queue) > 0:
                next_song = Queues.next_song(ctx.guild.id)
                await self.play(ctx, query=next_song['url'])
            else:
                await ctx.voice_client.disconnect()
        except Exception as e:
            print(f"[-] An error occurred while playing music: {e}")


        ### SKIP COMMAND ###
    @commands.command(name='skip', help='Skip the current song and play the next one in the queue')
    @commands.guild_only()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
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
                embed.description = ""
                for i, song in enumerate(queue, start=1):
                    embed.description += f"{i}: {song['title']}\n"
                await ctx.send(embed=embed)
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


    ### DJ ROLE COMMAND CHECK ###


async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))

