import discord
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='ping', help='Check the bot\'s latency')
    async def ping(self, ctx):
        await ctx.send(f'!ping: `{round(self.bot.latency * 1000)}ms` | websocket: `{round(self.bot.ws.latency * 1000)}ms`')



async def setup(bot):
    await bot.add_cog(Ping(bot))

