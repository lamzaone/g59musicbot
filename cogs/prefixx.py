import discord
from discord.ext import commands
from utils import serversettings as Settings

class Prefix(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.command(name='prefix', help='Change the command prefix for the bot')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix: str) -> None:
        settings = Settings.get_settings(ctx.guild.id)
        settings['prefix'] = new_prefix
        Settings.set_guild_settings(ctx.guild.id, settings)
        await ctx.send(f"Prefix changed to `{new_prefix}`")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Prefix(bot))
