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
    async def _play(self, interaction: discord.Interaction, query: str):
        # Ensure the interaction is acknowledged only once
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)  # Acknowledge the interaction with a "thinking" state
        # Call the play_song function ( because if i try writing all the logic inside _play, i can't recursively call it from itself :( )
        await self.play_song(interaction, query)

    ### START PLAYING SONG FUNCTION ###
    async def play_song(self, interaction, query):
        if interaction.guild:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if voice_client is None:
                #connect to the voice channel of the user
                if interaction.user.voice:
                    await interaction.user.voice.channel.connect()
                else:
                    await interaction.followup.send(":x: You must be in a voice channel.", ephemeral=False)
                    return            
            #get voice channel again after connecting
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if voice_client.is_playing() or voice_client.is_paused():
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
            info = musicplayer.get_info(query)
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
    async def _skip(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        player_cog = ctx.bot.get_cog('Player')
        await player_cog.skip(ctx)
            



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
    async def _search(self, interaction: discord.Interaction, query: str, results: int = 4):
        if results > 10:
            await interaction.response.send_message(":x: You can only search for a maximum of 10 results.", ephemeral=True)
            return
        # Initial response to acknowledge the command
        await interaction.response.defer(thinking=True)
        embed = discord.Embed(title=f"Searching for `{query}`", color=discord.Color.blurple())
        # Use followup to send additional messages after deferring the response
        message = await interaction.followup.send(embed=embed, wait=True)    
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        try:
            search_results = []
            embed.title = f"Search results for `{query}`"
            embed.description = ""
            for i in range (results):
                OPTS = config.YTDL_OPTS.copy()
                OPTS['extract_flat'] = True
                with yt_dlp.YoutubeDL(OPTS) as ydl:
                    OPTS['playlist_items'] = str(i + 1)
                    search_result = ydl.extract_info(f"ytsearch{results}:{query}", download=False)['entries'][0]
                    embed.title = f"Search results for `{query}`"
                    embed.add_field(name=f"{i + 1}. {search_result['title']}", value=search_result['url'], inline=False)
                    await message.edit(embed=embed)
                    search_results.append(search_result)

            for i in range(min(len(search_results), len(reactions))):
                await message.add_reaction(reactions[i])

            def reaction_check(reaction, user):
                return user == interaction.user and reaction.message.id == message.id
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=reaction_check)
            index = reactions.index(reaction.emoji)
            await message.delete()
            await self.play_song(interaction=interaction, query=search_results[index]['url'])
        except asyncio.TimeoutError:
            await interaction.followup.send("Reaction timeout, please try again.")

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