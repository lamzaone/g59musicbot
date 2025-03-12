import requests
import base64
import discord
from discord.ext import commands
from config import config
import os


class PicChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='banner',  brief='Change the bot\'s banner', description='Change the bot\'s banner to the image you provide')
    @commands.is_owner()
    async def banner(self, ctx, url:str = None):
        if not ctx.message.attachments and not url:
            await ctx.send(":information_source: Please attach an image or provide an URL to change the bot's banner\n- If you pass an URL as argument and it doesn't work, try attaching the image file to your message instead.")
            return
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        try:
            image = requests.get(url)
            encoded_image = base64.b64encode(image.content).decode("utf-8")

            headers = {
                "Authorization": f"Bot {config.bot_token.strip()}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
                "Content-Type": "application/json"
            }
            data = {
                "banner": f"data:image/png;base64,{encoded_image}"
            }
            url = "https://discord.com/api/v9/users/@me"

            response = requests.patch(url, headers=headers, json=data)
            if response.status_code != 200:
                await ctx.send(f"An error occurred: {response.json()}")
                return

            await ctx.send(":white_check_mark: Banner changed successfully!")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.hybrid_command(name='avatar',  brief='Change the bot\'s avatar', description='Change the bot\'s avatar to the image you provide')
    @commands.is_owner()
    async def avatar(self, ctx, url:str = None):

        if ctx.message.content.split(" ")[1]:
            url = ctx.message.content.split(" ")[1]
            if "http" not in url and url != "none" and url != "default":
                await ctx.send(":information_source: Please provide a valid URL or write \"none\" to remove the avatar, or write \"default\" to use the default avatar.")
                return
        elif ctx.message.attachments:
            url = ctx.message.attachments[0].url
        
        print(url)

        if url == "none":
            await self.bot.user.edit(avatar=None)
            await ctx.send(":white_check_mark: Avatar removed successfully!")
            return
        
        if url == "default":
            with open(os.path.join(config.config_path, "default.gif"), "rb") as image_file:
                image = image_file.read()
            await ctx.bot.user.edit(avatar=image)
            await ctx.send(":white_check_mark: Avatar changed to default successfully!")
            return
    
        if not url:
            await ctx.send(":information_source: Please attach an image or provide an URL to change the bot's avatar, or write \"none\" to remove it. \nIf you want to use the default avatar, write \"default\".")
            return

        try:                
            image = requests.get(url)
            await self.bot.user.edit(avatar=image.content)
            await ctx.send(":white_check_mark: Avatar changed successfully!")

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    try:
        if not bot.user.avatar:
            print("[-] Bot avatar not found. Setting default avatar...")
            with open(os.path.join(config.config_path, "default.gif"), "rb") as image_file:
                image = image_file.read()
            await bot.user.edit(avatar=image)
    except Exception as e:
        print(f"An error occurred while setting the default avatar: {e}")
    await bot.add_cog(PicChanger(bot))



    









