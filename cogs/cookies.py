import discord
from discord.ext import commands
from config import config
import os

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='cookies',  brief='Add youtube cookies', description='Add youtube cookies for bypassing youtube authentication')
    @commands.is_owner()
    async def cookies(self, ctx):
        # get message content without !cookies command
        message = ctx.message.content[len(ctx.prefix)+len(ctx.invoked_with):].strip()
        # check if the message is empty
        if not message:
            await ctx.send("No cookies provided")
            return
        # check if the message has an attachment (cookie file)
        if ctx.message.attachments:
            # get the first attachment
            attachment = ctx.message.attachments[0]
            # check if the attachment is a text file
            if attachment.filename.endswith('.txt'):
                # download the attachment
                await attachment.save(config.cookies_file)
                await ctx.send("Cookies saved")
                return
        with open(config.cookies_file, 'w') as f:
            f.write(message)
        await ctx.send("Cookies saved")

async def setup(bot):
    await bot.add_cog(Cookies(bot))