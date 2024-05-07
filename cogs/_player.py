###########################################
###########################################
# WARNING: THIS FILE DEPENDS ON player.py #
###########################################
###########################################

import discord
from discord.ext import commands
from discord import app_commands
from utils import serversettings as Settings, queues as Queues, musicplayer
import yt_dlp
from config import config
from cogs import player
import asyncio
import os

is_windows = os.name == 'nt'

class _Player(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='play', description='Play music from YouTube using a search term or URL')
    async def _play(self, interaction: discord.Interaction, query: str= None):
        # Ensure the interaction is acknowledged only once
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)  # Acknowledge the interaction with a "thinking" state
        # Call the play_song function ( because if i try writing all the logic inside _play, i can't recursively call it from itself :( )
        await self.play_song(interaction, query)

    ### START PLAYING SONG FUNCTION ###
    async def play_song(self, interaction, query=None):
        if interaction.guild:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if voice_client is None:
                #connect to the voice channel of the user
                if interaction.user.voice:
                    await interaction.user.voice.channel.connect()
                else:
                    await interaction.followup.send(":x: You must be in a voice channel.", ephemeral=False)
                    return  
                
            try:
                if query is not None:
                    if "list=" in query:
                        OPTS={
                            'extract_flat': True,
                            'noplaylist': False,                        
                            'no_warnings': True,                   
                        }
                        if "watch?v=" in query or 'youtu.be' in query or "youtube.com" in query:
                            message = await interaction.followup.send("The link contains a playlist, do you wish to add the whole playlist to the queue?", ephemeral=False)
                            await message.add_reaction("✅")
                            await message.add_reaction("❌")
                        def check(reaction, user):
                            return user == interaction.user and reaction.message.id == message.
                        try:
                            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                            if reaction.emoji == "✅":
                                aux_query = query
                                query = query.split("list=")[1]
                                query = f"https://www.youtube.com/playlist?list={query}"
                                with yt_dlp.YoutubeDL(OPTS) as ydl:
                                    try:
                                        search_results = ydl.extract_info(query, download=False)['entries']                                                        
                                        queue = Queues.get_queue(interaction.guild.id)
                                        for video in search_results:
                                            queue.append({'title': video['title'], 'url': video['url']})
                                        Queues.update_queue(interaction.guild.id, queue)
                                        await interaction.followup.send(f":white_check_mark: Added `{len(search_results)}` songs to the queue.")
                                        query=None
                                    except yt_dlp.DownloadError:                            
                                        query = aux_query
                            else:
                                pass
                            await message.delete()
                        except asyncio.CancelledError:
                            await message.delete()
                            return
                        except asyncio.TimeoutError:
                            await message.delete()
                            return
                    
            except Exception as e:
                print("error"+e)         

            #get voice channel again after connecting
            voice_client = discord.utils.get(self.bot.voice_clients, guild= interaction.guild)
            if voice_client.is_playing() or voice_client.is_paused():
                    if query is None:
                        return
                    try:
                        info = musicplayer.get_info(query)
                        queue = Queues.get_queue(interaction.guild.id)
                        queue.append({"title": info['title'], "url": info['original_url']})
                        Queues.update_queue(interaction.guild.id, queue)
                        await interaction.followup.send(f":white_check_mark: Added `{info['title']}` to the queue.", ephemeral=False)
                        return #exit the function
                    except Exception as e:
                        await interaction.followup.send(":x: An error occurred while adding to the queue.", ephemeral=False)
                        print(f"Error adding to queue: {e}")
                        return #exit the function
            # get voice client
        if not voice_client:
            await interaction.followup.send(":x: The bot is not connected to a voice channel.", ephemeral=False)
            return

        ctx = await self.bot.get_context(interaction)
        try:

            info = None
            while info is None:
                if query is None:
                    info = musicplayer.get_info(Queues.next_song(ctx.guild.id)['url'])
                else:
                    info = musicplayer.get_info(query)
                if info is None:
                    info = musicplayer.get_info(Queues.next_song(ctx.guild.id)['url'])
            video_url = info['url']
            if is_windows:
                audio_source = discord.FFmpegPCMAudio(video_url,executable=config.FFMPEG_PATH,**config.ffmpeg_options)
            else:
                audio_source = discord.FFmpegPCMAudio(video_url, **config.ffmpeg_options)

            ctx.bot.video_info = info
            ctx.bot.video_url = video_url
            audio_source = discord.PCMVolumeTransformer(audio_source, Settings.get_settings(interaction.guild.id)['volume'])
            voice_client.play(audio_source)
            await interaction.followup.send(f":arrow_forward: Now playing `{info['title']}` \n{info['original_url']}")
            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(1)
            await self.on_song_end(interaction)
        except Exception as e:
            await interaction.followup.send(":x: Error playing music.", ephemeral=False)
            print(f"Error playing music: {e}")

    ### ON SONG END HANDLER ###
    async def on_song_end(self, interaction):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_connected():
            queue = Queues.get_queue(interaction.guild.id)

            if queue:
                next_song = Queues.next_song(interaction.guild.id)
                await self.play_song(interaction, next_song['url'])
            else:
                await voice_client.disconnect()





    @app_commands.command(name='skip', description='Skip the current song and play the next one in the queue')
    @commands.guild_only()
    async def _skip(self, interaction: discord.Interaction, to: int = 1):
        ctx = await self.bot.get_context(interaction)
        player_cog = ctx.bot.get_cog('Player')
        await player_cog.skip(ctx, to=to)
            



    @app_commands.command(name='stop', description='Stop playing music and disconnect from voice channel')
    @commands.guild_only()
    async def _stop(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        player_cog = ctx.bot.get_cog('Player')
        await player_cog.stop(ctx)


            
    @app_commands.command(name='pause', description='Pause the currently playing music')
    @commands.guild_only()
    async def _pause(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        player_cog = ctx.bot.get_cog('Player')
        await player_cog.pause(ctx)




    @app_commands.command(name='volume', description='Set the volume of the music')
    async def __volume(self, interaction: discord.Interaction, volume:int = None):
        ctx = await self.bot.get_context(interaction)
        if not ctx.guild:
            await interaction.response.send_message(":x: This command can only be used in a server.", ephemeral=True)
            return
        if not ctx.author.guild_permissions.administrator and not ctx.author.get_role(Settings.get_dj_role(ctx.guild.id)):
            await interaction.response.send_message(":x: You must have the `Administrator` permission to use this command.", ephemeral=True)
            return
        player_cog = ctx.bot.get_cog('Player')
        await player_cog._volume(ctx,volume if volume is not None else None)

    @app_commands.command(name='seek', description='Set the playback position to a specific time in seconds')
    async def _seek(self, interaction: discord.Interaction, seconds: int): 
        ctx = await self.bot.get_context(interaction)
        player_cog = ctx.bot.get_cog('Player')
        await player_cog.seek(ctx, seconds=seconds)



    @app_commands.command(name='search', description='Search for a song on YouTube')
    async def _search(self, interaction: discord.Interaction, query: str, limit: int = 4):
        if limit > 10:
            await interaction.response.send_message(":x: You can only search for a maximum of 10 results.", ephemeral=True)
            return
        # Initial response to acknowledge the command
        await interaction.response.defer(thinking=True)
        embed = discord.Embed(title=f"Searching for `{query}`", color=discord.Color.blurple())
        # Use followup to send additional messages after deferring the response
        message = await interaction.followup.send(embed=embed, wait=True)    
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

            for i in range(min(len(search_results), len(reactions))):
                await message.add_reaction(reactions[i])

            def reaction_check(reaction, user):
                return user == interaction.user and reaction.message.id == message.id
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=reaction_check)
                index = reactions.index(reaction.emoji)
                await message.delete()
                await self.play_song(interaction=interaction, query=search_results[index]['url'])
            except asyncio.CancelledError:
                await message.delete()
                return
            except asyncio.TimeoutError:
                await message.delete()
                return


        except Exception as e:
            embed.title = "Error"
            embed.description = f"An error occurred: {str(e)}"
            await interaction.followup.send(embed=embed)

        ### SET DJ ROLE COMMAND ###
    @app_commands.command(name='setdj', description='Set the DJ role for the server')
    @commands.guild_only()
    async def set_dj(self, interaction: discord.Interaction , role: discord.Role = None):
        if not interaction.guild:
            await interaction.response.send_message(":x: This command can only be used in a server.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(":x: You must have the `Administrator` permission to use this command.", ephemeral=True)
            return
        ctx = await self.bot.get_context(interaction)
        player_cog = ctx.bot.get_cog('Player')
        await player_cog.set_dj(ctx, role=role)

    @app_commands.command(name='queue', description='Display the current queue')
    async def _queue(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        player_cog = ctx.bot.get_cog('Player')
        await player_cog.queue(ctx)

    @app_commands.command(name='shuffle', description='Shuffle the queue')
    async def _shuffle(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        player_cog = ctx.bot.get_cog('Player')
        await player_cog.shuffle(ctx)


async def setup(bot: commands.Bot):
    await bot.add_cog(_Player(bot))