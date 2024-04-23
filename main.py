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
    print(f'Logged in as {bot.user}')

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

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(config.YTDL_OPTS) as ydl:
                if "youtube.com/watch?" in query or "youtu.be/" in query:
                    info = ydl.extract_info(query, download=False)
                else:
                    info = ydl.extract_info(query, download=False)['entries'][0]

                video_url = info['url']

                # Play the audio using FFmpeg
                audio_source = discord.FFmpegPCMAudio(video_url, executable=FFMPEG_PATH, **config.ffmpeg_options)
                voice_client.play(audio_source)

                await ctx.send(f":notes: Now playing: {info['title']} from {info['original_url']}")

        except Exception as e:
            print(f"Error playing music: {e}")
            await ctx.send("An error occurred while trying to play the music.")

@bot.command(name='stop', help='Stop playing music and disconnect from voice channel')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect()

@bot.command(name='pause', help='Pause the currently playing music')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Music paused.")
    elif ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Music resumed.")
bot.run(config.bot_token)
