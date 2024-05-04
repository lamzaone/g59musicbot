import discord
from discord import app_commands
from discord.ext import commands

class _Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ping', description='Check the bot\'s latency')
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f' ping: `{round(self.bot.latency * 1000)} ms` | websocket: `{round(self.bot.ws.latency * 1000)} ms`', ephemeral=False)


async def setup(bot):
    await bot.add_cog(_Ping(bot))