import requests
import base64
import discord
from discord.ext import commands
from config import config


class PicChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='banner',  brief='Change the bot\'s banner', description='Change the bot\'s banner to the image you provide')
    @commands.is_owner()
    async def banner(self, ctx, url:str = None):
        if not ctx.message.attachments and not url:
            await ctx.send("Please attach an image or provide an URL to change the bot's banner")
            return
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        try:
            image = requests.get(url)
            encoded_image = base64.b64encode(image.content).decode("utf-8")

            headers = {
                "Authorization": f"Bot {config.bot_token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
                "Content-Type": "application/json"
            }
            data = {
                "banner": f"data:image/png;base64,{encoded_image}"
            }
            url = "https://discord.com/api/v9/users/@me"

            response = requests.patch(url, headers=headers, json=data)
            if response.status_code != 200:
                ctx.send(f"An error occurred: {response.json()}")
                return

            await ctx.send(":white_check_mark: Banner changed successfully!")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.hybrid_command(name='avatar',  brief='Change the bot\'s avatar', description='Change the bot\'s avatar to the image you provide')
    @commands.is_owner()
    async def avatar(self, ctx, url:str = None):

        if not ctx.message.attachments and not url:
            await ctx.send("Please attach an image or provide an URL to change the bot's avatar")
            return
        
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url

        try:                
            image = requests.get(url)
            await self.bot.user.edit(avatar=image.content)
            await ctx.send(":white_check_mark: Avatar changed successfully!")

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(PicChanger(bot))


    









