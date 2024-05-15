import subprocess
import sys
import discord
from discord.ext import commands
import os

on_windows = os.name == 'nt'
class Restart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("Restarting...")
        python_exe = 'python3' if not on_windows else 'python'
        restart_command = [python_exe, 'main.py', 'updated']
        # Start the bot as a new process and kill parent process
        script_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen(restart_command, cwd=script_dir)
        sys.exit(0)
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Restart(bot))