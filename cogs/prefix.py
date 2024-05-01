import discord
from discord.ext import commands
from discord import app_commands
from utils import serversettings as Settings

class Prefix(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='prefix', description='Set the prefix for the bot')
    async def prefix(self, interaction: discord.Interaction, prefix: str) -> None:
        server_id = interaction.guild.id
        settings = Settings.get_settings(server_id)
        settings['prefix'] = prefix
        Settings.set_guild_settings(server_id, settings)
        await interaction.response.send_message(f"Prefix set to {prefix}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Prefix(bot))