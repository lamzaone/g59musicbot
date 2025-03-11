import asyncio
from discord.ext import commands
from config import config

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='cookies',  brief='Add youtube cookies', description='Add youtube cookies for bypassing youtube authentication')
    @commands.is_owner()
    async def cookies(self, ctx):
        # after cookies command used, ask for a new message from the same user with the cookies
        await ctx.send("Please send the cookies in the next message")
        def check(m):
            return m.author == ctx.author
        try:
            message = await self.bot.wait_for('message', check=check, timeout=60)
            # check if cookies were sent as an attachment, or as text
            if message.attachments:
                cookies = await message.attachments[0].read()
                try:
                    with open(config.cookies_file, 'ab') as f:  # append in binary mode
                        f.write(cookies)
                except Exception as e:
                    await ctx.send(f"[-] An error occurred: {e}")
                    return
            else:
                cookies = message.content
                # append the cookies to the cookies file
                try:
                    with open(config.cookies_file, 'a') as f:  # append in text mode
                        f.write(cookies)
                except Exception as e:
                    await ctx.send(f"[-] An error occurred: {e}")
                    return
            await ctx.send("Cookies have been added.")
            message.delete()
        except asyncio.TimeoutError:
            await ctx.send("[-] Timed out. Please try again.")
        except Exception as e:
            await ctx.send(f"[-] An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Cookies(bot))
