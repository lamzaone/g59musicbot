import discord
from discord.ext import commands
from discord import app_commands
from utils import serversettings as Settings
from cogs import prefixx

class _Prefix(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='prefix', description='Set the prefix for the bot', )
    async def prefix(self, interaction: discord.Interaction, prefix: str):
        prefix_cog = self.bot.get_cog('Prefix')
        ctx = await self.bot.get_context(interaction)
        await prefix_cog.prefix(ctx, prefix)
        

async def setup(bot: commands.Bot):
    await bot.add_cog(_Prefix(bot))