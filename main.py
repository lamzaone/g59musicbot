import discord
from discord.ext import commands
from utils import serversettings as Settings, queues as Queues, update
import os
from config import config  # Make sure this import points to your bot's configuration
import asyncio
import json
import sys
import nacl



# Initialize Discord bot with command prefix and intents
bot = commands.Bot(command_prefix=commands.when_mentioned_or(""), intents=config.intents)
tree = bot.tree
is_windows = os.name == 'nt'

async def load_cogs():
    cogs = config.get_cogs()
    for cog in cogs:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"[+] Successfully loaded {cog}")
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
        await Settings.check_guilds(bot.guilds)
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


if __name__ == '__main__':
    args = sys.argv[1:]
    main(*args)