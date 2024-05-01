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

    @commands.command(name='play', help='Play music from YouTube using a search term or URL')
    @commands.guild_only()
    async def play(self, ctx, *, query: str):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(":x: You are not connected to a voice channel.")
                return
        
        async with ctx.typing():
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
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
    @commands.has_permissions(manage_guild=True)
    async def _volume(self, ctx, volume: int = None):
        settings = Settings.get_settings(ctx.guild.id)

        if volume is None:
            await ctx.send(":loud_sound: Current volume is `" + str(round(settings['volume'] * 100)) + "%`")
            return
        
        elif volume < 0 or volume > 100:
            await ctx.send(":loud_sound: Volume must be between 0 and 100 you dummy...")
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


    @commands.command(name='search', help='Search for a song on YouTube')
    @commands.guild_only()
    async def search(self, ctx, *, query:str):
        embed = discord.Embed(title=f"Searching for `{query}`", color=discord.Color.blurple())
        message = await ctx.send(embed=embed)
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        try:
            search_results = []
            for i in range (4):
                OPTS = config.YTDL_OPTS.copy()
                OPTS['extract_flat'] = True
                with yt_dlp.YoutubeDL(OPTS) as ydl:
                    OPTS['playlist_items'] = str(i + 1)
                    search_result = ydl.extract_info(f"ytsearch4:{query}", download=False)['entries'][0]
                    embed.title = f"Search results for `{query}`"
                    embed.add_field(name=f"{i + 1}. {search_result['title']}", value=search_result['url'], inline=False)
                    await message.edit(embed=embed)
                    search_results.append(search_result)

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))