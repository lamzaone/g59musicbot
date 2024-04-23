import discord
from discord.ext import commands
import yt_dlp
import os
from config import config  # Make sure this import points to your bot's configuration
import asyncio

# FFmpeg path - ensure you have FFmpeg installed and update the path if needed
FFMPEG_PATH = os.path.join(os.getcwd(), 'ffmpeg/bin/ffmpeg.exe')

# Initialize Discord bot with command prefix and intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []



@bot.event
async def on_ready():
    print(f'Successfully booted: {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!play <song>", ), status=discord.Status.do_not_disturb)
    



@bot.command(name='play', help='Play music from YouTube using a search term or URL')
async def play(ctx, *, query: str):
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
            audio_source = discord.FFmpegPCMAudio(video_url, executable=FFMPEG_PATH, **config.ffmpeg_options)
            audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.5)
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
        
@bot.command(name='volume', help='Adjust the volume level.')
async def volume(ctx, volume: float):
    # Ensure the input volume is a percentage (e.g., 50 for 50%)
    volume = volume / 100  # Convert to a float from a percentage

    if ctx.voice_client and ctx.voice_client.is_playing():
        # Re-create the audio source with the new volume
        if bot.original_source is None:
            bot.original_source = ctx.voice_client.source  # Original audio source
        new_source = discord.PCMVolumeTransformer(bot.original_source, volume=volume)  # Create a new volume transformer

        # Stop current playback
        ctx.voice_client.source = new_source


        await ctx.send(f"Volume set to {volume * 100}%.")
    else:
        await ctx.send("No music is currently playing.")    

@bot.command(name='ping', help='Check the bot\'s latency')
async def ping(ctx):
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms, websocket latency: {round(bot.ws.latency * 1000)}ms')

@bot.command(name='seek', help='Set the playback position to a specific time in seconds')
async def fastforward(ctx, seconds: int):
    # Ensure there is a voice client playing music
    if ctx.voice_client and ctx.voice_client.is_playing():
        # Stop the current playback
        ctx.voice_client.stop()

        # Check if there's stored video information
        if hasattr(ctx.bot, 'video_info') and hasattr(ctx.bot, 'video_url'):
            # Add the offset in seconds to the FFmpeg options to fast forward
            seek_time = f"-ss {seconds}"
            ffmpeg_opts = {**config.ffmpeg_options, "options": f"{config.ffmpeg_options['options']} {seek_time}"}

            audio_source = discord.FFmpegPCMAudio(ctx.bot.video_url, executable=FFMPEG_PATH, **ffmpeg_opts)

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
