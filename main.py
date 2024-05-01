import discord
from discord.ext import commands
from discord import app_commands
from utils import serversettings as Settings, queues as Queues, update, musicplayer
import yt_dlp
import os
from config import config  # Make sure this import points to your bot's configuration
import asyncio
import json
import sys
import nacl
from typing import Literal, Optional



# Initialize Discord bot with command prefix and intents
bot = commands.Bot(command_prefix=commands.when_mentioned_or(""), intents=config.intents)
tree = bot.tree
is_windows = os.name == 'nt'



async def load_cogs():
    cogs = config.get_cogs()
    for cog in cogs:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"[+] Loaded")
        except Exception as e:
            print(f"[-] An error occurred while loading {cog}: {e}")

@bot.event
async def on_ready():
    await load_cogs()
    await tree.sync()
    print(f'[+] Booted {bot.user}...')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/play <song>"), status=discord.Status.dnd)
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



### INITIALIZE GUILD SETTINGS AND QUEUES ON GUILD JOIN ###
@bot.event
async def on_guild_join(guild):
    Settings.set_guild_settings(guild.id, Settings.default_settings)
    Queues.update_queue(guild.id, [])
    print(f'[+] Joined {guild.name} with id {guild.id}')
    print(f'[+] Successfully initialized config/serversettings.json for {guild.name}')
    print(f'[+] Successfully initialized config/queues.json for {guild.name}')

### SET PREFIX COMMAND ###
# @bot.command(name='prefix', help='Change the command prefix for the bot')
# @commands.guild_only()
# @commands.has_permissions(administrator=True)
# async def prefix(ctx, new_prefix: str):
#     settings = Settings.get_settings(ctx.guild.id)
#     settings['prefix'] = new_prefix
#     Settings.set_guild_settings(ctx.guild.id, settings)
#     await ctx.send(f"Prefix changed to `{new_prefix}`")

# @tree.command(name='prefix', description='Change the command prefix for the bot')
# async def _prefix(interaction: discord.Interaction, new_prefix: str):
#     ctx = await commands.Context.from_interaction(interaction)
#     if not ctx.guild:
#         await interaction.response.send_message(":x: This command can only be used in a server.", ephemeral=True)
#         return
#     if not ctx.author.guild_permissions.administrator:
#         await interaction.response.send_message(":x: You must have the `Administrator` permission to use this command.", ephemeral=True)
#         return
#     await prefix(ctx, new_prefix)









### PING COMMAND ###
@bot.command(name='ping', help='Check the bot\'s latency')
async def ping(ctx):
    await ctx.send(f'ping: `{round(bot.latency * 1000)}ms` | websocket: `{round(bot.ws.latency * 1000)}ms`')

@tree.command(name='ping', description='Check the bot\'s latency')
async def _ping(interaction: discord.Interaction):
    ctx = await commands.Context.from_interaction(interaction)
    await ping(ctx)







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



@bot.event
async def on_message(message):
    if message.guild is not None:
        prefix = Settings.get_settings(message.guild.id)['prefix']
        if message.content.startswith(prefix):
            message.content = message.content[len(prefix):]
            await bot.process_commands(message)
    else:
        await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f":x: You need to have `{', '.join(error.missing_permissions)}` permissions to use this command.", ephemeral=True)
        return
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        await ctx.send(":x: You do not have permission to use this command.")
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(":x: Missing required argument.")
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send(":x: Invalid argument.")
        return
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f":x: Command on cooldown. Try again in {error.retry_after:.2f} seconds.")
        return
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(":x: An error occurred while executing the command.")
        return

    raise error



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