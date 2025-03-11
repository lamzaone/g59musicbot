import discord
from discord.ext import commands
from config import config
import os

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def cookies(self, ctx):
        # get message content
        cookies = ctx.message.content
        # place cookies into cookes.txt
        with open(config.cookies_file, 'w') as f:
            f.write(cookies)
        await ctx.send("Cookies saved")

async def setup(bot):
    await bot.add_cog(Cookies(bot))