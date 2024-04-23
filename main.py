import discord
from discord.ext import commands
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
queue = []



@bot.event
async def on_ready():
    print(f'Successfully booted: {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!play <song>", ), status=discord.Status.do_not_disturb)
    with open(config.serversettings, 'r') as f:
        settings = json.load(f)
    for guild in bot.guilds:
        if str(guild.id) not in settings:
            settings[str(guild.id)] = {"volume": 0.5}
    with open(config.serversettings, 'w') as f:
        json.dump(settings, f, indent=4)
    



@bot.command(name='play', help='Play music from YouTube using a search term or URL')
async def play(ctx, *, query: str):
    # retrieve settings for the guild from the settings file
    with open(config.serversettings, 'r') as f:
        settings = json.load(f)
        settings = settings[str(ctx.guild.id)]
        print(settings)
    # Connect to the voice channel
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel to play music.")
        return
    
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None or not ctx.voice_client.is_connected():
        await voice_channel.connect()

    voice_client = ctx.voice_client

    
    try:
        with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
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
            # disconnect when the song is over but not when pausing
            while voice_client.is_connected() and (voice_client.is_playing() or ctx.voice_client.is_paused()):
                await asyncio.sleep(1)
            await stop(ctx)


    except Exception as e:
        print(f"Error playing music: {e}")
        await ctx.send("An error occurred while trying to play the music.")

@bot.command(name='stop', help='Stop playing music and disconnect from voice channel')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect()
        await ctx.send("Music stopped.")

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
        settings = settings[str(ctx.guild.id)]

    if volume is None:
        await ctx.send("Current volume is " + str(settings['volume'] * 100) + "%")
        return
    elif volume < 0 or volume > 100:
        await ctx.send("Volume must be between 0 and 100 you dummy...")
        return

    settings['volume'] = volume / 100
    with open(config.serversettings, 'w') as f:
        json.dump({ctx.guild.id: settings}, f, indent=4)

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.source.volume = volume / 100

    await ctx.send(f"Volume set to {volume}%")
    



@bot.command(name='ping', help='Check the bot\'s latency')
async def ping(ctx):
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms, websocket latency: {round(bot.ws.latency * 1000)}ms')

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
