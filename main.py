import discord
from discord.ext import commands
#from utils import musicplayer
import yt_dlp
import os
from config import config  # Make sure this import points to your bot's configuration
import asyncio
import json

# FFmpeg path - ensure you have FFmpeg installed and update the path if needed
FFMPEG_PATH = os.path.join(os.getcwd(), 'ffmpeg/bin/ffmpeg.exe')

# Initialize Discord bot with command prefix and intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
on_windows = os.name == 'nt'




@bot.event
async def on_ready():
    print(f'Booting {bot.user}...')
    print(discord.utils.oauth_url(bot.application_id, permissions=discord.Permissions(permissions=8)))
    await bot.change_presence(activity=discord.Game(name="!play <song>", ), status=discord.Status.do_not_disturb)
    config.init()
    queues = {}

    with open(config.serversettings, 'r') as f:
        settings = json.load(f)
        print('[+] Successfully loaded settings')    

    for guild in bot.guilds:
        if str(guild.id) not in settings:
            settings[str(guild.id)] = { "volume": 0.5, \
                                        "prefix": "!"}
            

        queues[str(guild.id)] = []
    with open(config.serversettings, 'w') as f:
        json.dump(settings, f, indent=4)
        print('[+] Successfully initialized settings')
    with open(config.queues, 'w') as f:
        json.dump(queues, f, indent=4)
        print('[+] Successfully initialized queues')

    # load prefixes from settings file
    # for guild in bot.guilds:
    #     with open(config.serversettings, 'r') as f:
    #         settings = json.load(f)
    #         settings = settings[str(guild.id)]
    #     bot.command_prefix = settings['prefix']


@bot.event
async def on_guild_join(guild):
    with open(config.serversettings, 'r') as f:
        settings = json.load(f)
        settings[str(guild.id)] = { "volume": 0.5, \
                                    "prefix": "!" }
        
    with open(config.serversettings, 'w') as f:
        json.dump(settings, f, indent=4)
    with open(config.queues, 'r') as f:
        queues = json.load(f)
        queues[str(guild.id)] = []
    with open(config.queues, 'w') as f:
        json.dump(queues, f, indent=4)
    print(f'[+] Joined {guild.name} with id {guild.id}')
    print('[+] Successfully initialized settings')
    print('[+] Successfully initialized queues')


@bot.command(name='prefix', help='Change the command prefix for the bot')
async def prefix(ctx, new_prefix: str):
    await ctx.send(f"Command disabled. Use the default prefix: {bot.command_prefix}")


    # with open(config.serversettings, 'r') as f:
    #     settings = json.load(f)
    # settings[str(ctx.guild.id)]['prefix'] = new_prefix
    # with open(config.serversettings, 'w') as f:
    #     json.dump(settings, f, indent=4)
    # bot.command_prefix = new_prefix
    # await ctx.send(f"Prefix changed to {new_prefix}")






@bot.command(name='play', help='Play music from YouTube using a search term or URL')
async def play(ctx, *, query: str):
    # retrieve settings for the guild from the settings file
    with open(config.serversettings, 'r') as f:
        settings = json.load(f)
        settings = settings[str(ctx.guild.id)]
    # Connect to the voice channel
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel to play music.")
        return
    
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None or not ctx.voice_client.is_connected():
        await voice_channel.connect()

    voice_client = ctx.voice_client

    
    # Trigger bot typing status

    
    # check if bot is playing music
    if voice_client.is_playing() and ("youtube.com/watch?" in query or "youtu.be/" in query):
        async with ctx.typing():
            try:
                with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
                        info = ydl.extract_info(query, download=False)
                        original_url = info['original_url']
                        url = info['url']
                        title = info['title']
                        with open(config.queues, 'r') as f:
                            queues = json.load(f)
                        queues[str(ctx.guild.id)].append({"title": title, "url": url, "original_url": original_url})
                        with open(config.queues, 'w') as f:
                            json.dump(queues, f, indent=4)
                        await ctx.send(f"Added {title} to the queue.")
                return
            except Exception as e:
                await ctx.send("An error occurred while trying to retrieve the music info.")
                return
    elif voice_client.is_playing():
        async with ctx.typing():
            try:
                with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
                    info = ydl.extract_info(query, download=False)['entries'][0]
                    original_url = info['original_url']
                    title = info['title']
                    url = info['url']
                    with open(config.queues, 'r') as f:
                        queues = json.load(f)
                    queues[str(ctx.guild.id)].append({"title": title, "url": url, "original_url": original_url})
                    with open(config.queues, 'w') as f:
                        json.dump(queues, f, indent=4)
                    await ctx.send(f"Added {title} to the queue.")
                return
            except Exception as e:
                await ctx.send("An error occurred while trying to retrieve the music info.")
                return

    
    
    try:
        with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
            async with ctx.typing():
                if type(query) == str:
                    if "youtube.com/watch?" in query or "youtu.be/" in query:
                        info = ydl.extract_info(query, download=False)
                    else:
                        info = ydl.extract_info(query, download=False)['entries'][0]

                    video_url = info['url']

                    ctx.bot.video_info = info
                    ctx.bot.video_url = video_url
                    # Play the audio using FFmpeg
                    if on_windows:
                        audio_source = discord.FFmpegPCMAudio(video_url, executable=FFMPEG_PATH, **config.ffmpeg_options)
                    else:
                        audio_source = discord.FFmpegPCMAudio(video_url, **config.ffmpeg_options)
                    audio_source = discord.PCMVolumeTransformer(audio_source, settings['volume'])
                    voice_client.play(audio_source)
                    await ctx.send(f":notes: Now playing: {info['title']} from {info['original_url']}")
                else:
                    if on_windows:
                        audio_source = discord.FFmpegPCMAudio(query['url'], executable=FFMPEG_PATH, **config.ffmpeg_options)
                    else:
                        audio_source = discord.FFmpegPCMAudio(query['url'], **config.ffmpeg_options)
                    
                    ctx.bot.video_url = query['url']
                    audio_source = discord.PCMVolumeTransformer(audio_source, settings['volume'])
                    voice_client.play(audio_source)
                    await ctx.send(f":notes: Now playing: {query['title']} from {query['original_url']}")

            
            # disconnect when the song is over but not when pausing

            while voice_client.is_connected() and (voice_client.is_playing() or ctx.voice_client.is_paused()):
                await asyncio.sleep(1)
        
            #play next song in queue
            with open(config.queues, 'r') as f:
                queues = json.load(f)
            if len(queues[str(ctx.guild.id)]) > 0:
                await skip(ctx)
            else:
                # ignore if already stopped
                if voice_client.is_connected():
                    await ctx.voice_client.disconnect()
                    # await ctx.send("Music stopped, queue is empty.")


    except Exception as e:
        print(f"Error playing music: {e}")
        await ctx.send("An error occurred while trying to play the music.")


@bot.command(name='skip', help='Skip the currently playing music')
async def skip(ctx):
    #check if the bot is connected to a voice channel and the queue is not empty
    if ctx.voice_client.is_connected() and ctx.voice_client.is_playing():
        with open(config.queues, 'r') as f:
            queues = json.load(f)
        if len(queues) > 0:
            query = queues[str(ctx.guild.id)].pop(0)
            with open(config.queues, 'w') as f:
                json.dump(queues, f, indent=4)
            ctx.voice_client.stop()
            await play(ctx, query=query)
        else:
            ctx.voice_client.disconnect()
            await ctx.send("Music stopped, queue is empty.")


@bot.command(name='stop', help='Stop playing music and disconnect from voice channel')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect()
        with open(config.queues, 'r') as f:
            queues = json.load(f)
            queues[str(ctx.guild.id)] = []
        with open(config.queues, 'w') as f:
            json.dump(queues, f, indent=4)
        await ctx.send("Music stopped and queue has been cleared.")

@bot.command(name='pause', help='Pause the currently playing music')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Music paused.")
    elif ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Music resumed.")
        

@bot.command(name='volume', help='Set the volume of the music')
async def volume(ctx, volume: int = None):
    #change the settings for the guild in the settings file
    with open(config.serversettings, 'r') as f:
        settings = json.load(f)        

    if volume is None:
        await ctx.send("Current volume is " + str(settings[str(ctx.guild.id)]['volume'] * 100) + "%")
        return
    elif volume < 0 or volume > 100:
        await ctx.send("Volume must be between 0 and 100 you dummy...")
        return

    settings[str(ctx.guild.id)]['volume'] = volume / 100
    with open(config.serversettings, 'w') as f:
        json.dump(settings, f, indent=4)

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.source.volume = volume / 100

    await ctx.send(f"Volume set to {volume}%")
    



@bot.command(name='ping', help='Check the bot\'s latency')
async def ping(ctx):
    await ctx.send(f'ping: {round(bot.latency * 1000)}ms | websocket: {round(bot.ws.latency * 1000)}ms')

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

            if on_windows:
                audio_source = discord.FFmpegPCMAudio(ctx.bot.video_url, executable=FFMPEG_PATH , **ffmpeg_opts)
            else:
                audio_source = discord.FFmpegPCMAudio(ctx.bot.video_url, **ffmpeg_opts)
            audio_source = discord.PCMVolumeTransformer(audio_source, settings['volume'])

            ctx.voice_client.play(audio_source)

            await ctx.send(f"Started playing at {seconds} seconds.")
        else:
            await ctx.send("No music data available to seek.")
    else:
        await ctx.send("No music is currently playing.")

@bot.event
async def on_message(message):
    if message.author.id == 473624857389694977:
        await message.channel.send(f'Daca te cheama szabo esti gay! :frumosul:')
    await bot.process_commands(message)

bot.run(config.bot_token)
# generate invite link
