import discord
from discord.ext import commands
from utils import serversettings as Settings, queues as Queues, update, musicplayer
import yt_dlp
import os
from config import config  # Make sure this import points to your bot's configuration
import asyncio
import json
import sys
import nacl
from typing import Literal, Optional


# FFmpeg path - ensure you have FFmpeg installed and update the path if needed

# Initialize Discord bot with command prefix and intents

bot = commands.Bot(command_prefix="", intents=config.intents)
tree = bot.tree
is_windows = os.name == 'nt'

@bot.event
async def on_ready():
    await tree.sync()
    print(f'[+] Booted {bot.user}...')
    await bot.change_presence(activity=discord.Game(name="!play <song>", ), status=discord.Status.do_not_disturb)
    # Reset queues and fetch settings for all guilds
    queues = {}
    settings = Settings.get_settings_all()


    # Initialize settings for all guilds
    try:
        for guild in bot.guilds:
            if Settings.get_settings(guild.id) is None:
                settings[str(guild.id)] = Settings.default_settings
        Settings.set_all_settings(settings)
        print('[+] Successfully initialized bot settings')
    except Exception as e:
        print('[!] Error initializing bot settings: ', e)


    # Initialize queues for all guilds
    try:
        for guild in bot.guilds:
            if Settings.get_settings(guild.id) is None:
                settings[str(guild.id)] = Settings.default_settings
            queues[str(guild.id)] = []
        with open(config.queues, 'w') as f:
            json.dump(queues, f, indent=4)
            print('[+] Successfully initialized queues')
    except Exception as e:
        print('[!] Error initializing queues: ', e)

    # Print URL for inviting the bot to a server
    oauth_url = discord.utils.oauth_url(bot.application_id, permissions=discord.Permissions(permissions=8))
    print(f'[+] Invite URL: {oauth_url}')




@bot.event
async def on_guild_join(guild):
    Settings.set_guild_settings(guild.id, Settings.default_settings)

    with open(config.queues, 'r') as f:
        queues = json.load(f)
        queues[str(guild.id)] = []
    with open(config.queues, 'w') as f:
        json.dump(queues, f, indent=4)
    print(f'[+] Joined {guild.name} with id {guild.id}')
    print(f'[+] Successfully initialized config/serversettings.json for {guild.name}')
    print(f'[+] Successfully initialized config/queues.json for {guild.name}')

### SET PREFIX COMMAND ###
@bot.command(name='prefix', help='Change the command prefix for the bot')
async def prefix(ctx, new_prefix: str):
    settings = Settings.get_settings(ctx.guild.id)
    settings['prefix'] = new_prefix
    Settings.set_guild_settings(ctx.guild.id, settings)
    await ctx.send(f"Prefix changed to `{new_prefix}`")

    #FIXED???
@tree.command(name='prefix', description='Change the command prefix for the bot')
async def __prefix(interaction: discord.Interaction, new_prefix: str):
    ctx = await commands.Context.from_interaction(interaction)
    await prefix(ctx, new_prefix)
    #await interaction.response.send_message(f"Prefix changed to {new_prefix}", ephemeral=False)





### PLAY COMMAND ###
@bot.command(name='play', help='Play music from YouTube using a search term or URL')
async def play(ctx, *, query: str):
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
                info = musicplayer.extract_yt_info(query)
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

        info = musicplayer.extract_yt_info(query)
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
            await play(ctx, query=next_song['url'])
        else:
            await ctx.voice_client.disconnect()
    except Exception as e:
        print(f"[-] An error occurred while playing music: {e}")



### /PLAY COMMAND ###
@tree.command(name='play', description='Play music from YouTube using a search term or URL')
async def _play(interaction: discord.Interaction, query: str):
    # Ensure the interaction is acknowledged only once
    if not interaction.response.is_done():
        await interaction.response.defer(thinking=True)  # Acknowledge the interaction with a "thinking" state

    
    if interaction.guild:
        #check if bot is connected to a voice channel
        voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if voice_client is None:
            #connect to the voice channel of the user
            if interaction.user.voice:
                await interaction.user.voice.channel.connect()
            else:
                await interaction.followup.send(":x: You must be in a voice channel.", ephemeral=False)
                return
        
        #get voice channel again after connecting
        voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)

        #check if music is playing or paused to add music to Queue instead of playing
        if voice_client.is_playing() or voice_client.is_paused():
            try:
                info = musicplayer.extract_yt_info(query)
                queue = Queues.get_queue(interaction.guild.id)
                queue.append({"title": info['title'], "url": info['original_url']})
                Queues.update_queue(interaction.guild.id, queue)
                await interaction.followup.send(f":white_check_mark: Added `{info['title']}` to the queue.", ephemeral=False)
                return #exit the function
            except Exception as e:
                await interaction.followup.send(":x: An error occurred while adding to the queue.", ephemeral=False)
                print(f"Error adding to queue: {e}")
                return #exit the function

    # Call the play_song function ( because if i try writing all the logic inside _play, i can't recursively call it from itself :( )
    await play_song(interaction, query)

async def play_song(interaction, query):
    # get voice client
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not voice_client:
        await interaction.followup.send(":x: The bot is not connected to a voice channel.", ephemeral=False)
        return

    ctx = await commands.Context.from_interaction(interaction)
    try:
        with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
            info = musicplayer.extract_yt_info(query)
            video_url = info['url']

            audio_source = discord.FFmpegPCMAudio(
                video_url,
                executable=config.FFMPEG_PATH if is_windows else None,
                **config.ffmpeg_options
            )

            ctx.bot.video_info = info
            ctx.bot.video_url = video_url
            audio_source = discord.PCMVolumeTransformer(audio_source, Settings.get_settings(interaction.guild.id)['volume'])
            voice_client.play(audio_source)
            await interaction.followup.send(f":arrow_forward: Now playing `{info['title']}` \n{info['original_url']}")
            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(1)
            await on_song_end(interaction)
    except Exception as e:
        await interaction.followup.send(":x: Error playing music.", ephemeral=False)
        print(f"Error playing music: {e}")

### ON SONG END HANDLER ###
async def on_song_end(interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_connected():
        queue = Queues.get_queue(interaction.guild.id)
        
        if queue:
            next_song = queue.pop(0)  # Get the next song
            Queues.update_queue(interaction.guild.id, queue)  # Save the queue
            await play_song(interaction, next_song['url'])  # Play the next song
        else:
            await voice_client.disconnect()  # Disconnect if the queue is empty



### SKIP COMMAND ###
@bot.command(name='skip', help='Skip the current song and play the next one in the queue')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send(":fast_forward: Skipped the current song.")
    else:
        await ctx.send(":x: No music is currently playing.")
@tree.command(name='skip', description='Skip the current song and play the next one in the queue')
async def _skip(interaction: discord.Interaction):
    ctx = await commands.Context.from_interaction(interaction)
    await skip(ctx)
        


### STOP COMMAND ###
@bot.command(name='stop', help='Stop playing music and disconnect from voice channel')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        queue = Queues.get_queue(ctx.guild.id)
        queue = {}
        Queues.update_queue(ctx.guild.id, queue)
        ctx.voice_client.stop()
        await ctx.send(":octagonal_sign: Music stopped and queue has been cleared.")
    else:
        await ctx.send(":x: No music is currently playing.")

@tree.command(name='stop', description='Stop playing music and disconnect from voice channel')
async def _stop(interaction: discord.Interaction):
    ctx = await commands.Context.from_interaction(interaction)
    await stop(ctx)
    #await interaction.response.send_message("Stopping music...", ephemeral=False)


### PAUSE COMMAND ###
@bot.command(name='pause', help='Pause the currently playing music')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send(":pause_button: Music paused.")
    elif ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send(":arrow_forward: Music resumed.")
        
@tree.command(name='pause', description='Pause the currently playing music')
async def _pause(interaction: discord.Interaction):
    ctx = await commands.Context.from_interaction(interaction)
    await pause(ctx)
    #await interaction.response.send_message("Pausing music...", ephemeral=False)


### VOLUME COMMAND ###
@bot.command(name='volume', help='Set the volume of the music')
async def volume(ctx, volume: int = None):
    #change the settings for the guild in the settings file
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


#FIXME: disabled command cuz error
#@tree.command(name='volume', description='Set the volume of the music')
async def _volume(interaction: discord.Interaction, volume:int = None):
    ctx = await commands.Context.from_interaction(interaction)
    if volume is not None:
        await volume(ctx, volume=volume)
    else:
        await volume(ctx)
    #await interaction.response.send_message("Changing volume...", ephemeral=False)


### PING COMMAND ###
@bot.command(name='ping', help='Check the bot\'s latency')
async def ping(ctx):
    await ctx.send(f'ping: `{round(bot.latency * 1000)}ms` | websocket: `{round(bot.ws.latency * 1000)}ms`')

@tree.command(name='ping', description='Check the bot\'s latency')
async def _ping(interaction: discord.Interaction):
    ctx = await commands.Context.from_interaction(interaction)
    await ping(ctx)
    #await interaction.response.send_message("Checking ping...", ephemeral=False)



### SEEK COMMAND ###
@bot.command(name='seek', help='Set the playback position to a specific time in seconds')
async def seek(ctx, seconds: int):
    # Ensure there is a voice client playing music
    if ctx.voice_client and ctx.voice_client.is_playing():
        # Stop the current playback
        ctx.voice_client.stop()

        # Check if there's stored video information
        if hasattr(ctx.bot, 'video_info') and hasattr(ctx.bot, 'video_url'):
            # Add the offset in seconds to the FFmpeg options to fast forward
            with open(config.serversettings, 'r') as f:
                settings = json.load(f)
                settings = settings[str(ctx.guild.id)]
            seek_time = f"-ss {seconds}"
            ffmpeg_opts = {**config.ffmpeg_options, "options": f"{config.ffmpeg_options['options']} {seek_time}"}

            if is_windows:
                audio_source = discord.FFmpegPCMAudio(ctx.bot.video_url, executable=config.FFMPEG_PATH , **ffmpeg_opts)
            else:
                audio_source = discord.FFmpegPCMAudio(ctx.bot.video_url, **ffmpeg_opts)
            audio_source = discord.PCMVolumeTransformer(audio_source, settings['volume'])

            ctx.voice_client.play(audio_source)

            await ctx.send(f":arrow_forward: Started playing at {seconds} seconds.")
        else:
            await ctx.send(":x: No music data available to seek.")
    else:
        await ctx.send(":x: No music is currently playing.")


### SYNC COMMANDS ###
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")



@tree.command(name='seek', description='Set the playback position to a specific time in seconds')
async def _seek(interaction: discord.Interaction, seconds: int):
    ctx = await commands.Context.from_interaction(interaction)
    await seek(ctx, seconds=seconds)
    #await interaction.response.send_message("Seeking music...", ephemeral=False)



@bot.event
async def on_message(message):
    prefix = Settings.get_settings(message.guild.id)['prefix']
    if message.content.startswith(prefix):
        message.content = message.content[len(prefix):]
        await bot.process_commands(message)






def main(*args):

    # Check for updates
    if args:
        if args[0] == 'updated':
            print("[+] Successfully updated to the latest version!")
    else:
        if update.check_for_updates(is_windows):
            update.update(is_windows)
            sys.exit(0)

    # Initialize the bot        
    try:
        config.init()
        bot.run(config.bot_token)
    except Exception as e:
        print(f"[-] An error occurred while running the bot: {e}")
        return



# Entry point
if __name__ == '__main__':
    args = sys.argv[1:]  # All arguments after the script name
    main(*args)