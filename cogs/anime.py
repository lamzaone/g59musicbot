import asyncio
import discord
from discord.ext import commands
import requests
import os
import subprocess
import json

port = 5000
ip = requests.get('https://api.ipify.org').content.decode('utf8')
is_windows = os.name == 'nt'

async def runProcess(exe):
    p = await asyncio.create_subprocess_exec(
        *exe,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
    )

    output = ''
    select_prompt_reached = False

    # Read the output from the process
    while True:
        line = await p.stdout.readline()
        if not line:
            break
        decoded_line = line.decode().strip()
        output += decoded_line + '\n'
        if "Select the search result" in decoded_line:
            select_prompt_reached = True
            break

    return p, output.strip(), select_prompt_reached

async def sendInputToProcess(p, user_input):
    p.stdin.write(user_input.encode() + b'\n')
    await p.stdin.drain()

    output = ''
    # Read the remaining output from the process
    while True:
        line = await p.stdout.readline()
        if not line:
            break
        output += line.decode().strip() + '\n'

    await p.wait()
    return output.strip()

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def anime(self, ctx, name: str, episode: int = 1):
        
        if hasattr(ctx.bot, 'process'):
            if ctx.bot.process is not None:
                ctx.bot.process.kill()
                ctx.bot.process = None

        # Define the command to run
        cmd = ["animdl", "grab", name, "-r", str(episode)]

        # Execute the command and capture the output until the select prompt
        process, output, select_prompt_reached = await runProcess(cmd)

        # Send the initial output to Discord
        await ctx.send(f"```{output}```")

        if select_prompt_reached:
            # Wait for user's response
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send('You took too long to respond')
                process.kill()
                return

            # Process user's response
            user_input = msg.content

            # Send the user's input back to the CLI command and capture the output
            final_output = await sendInputToProcess(process, user_input)

            # Extract JSON part from the final output
            json_start_index = final_output.find("{")
            if json_start_index != -1:
                final_output = final_output[json_start_index:]
                try:
                    output_dict = json.loads(final_output)
                    
                    # Extract the highest quality stream link
                    highest_quality = -1
                    highest_link = None
                    for stream in output_dict.get('streams', []):
                        quality = stream.get('quality', 0)
                        if quality > highest_quality:
                            highest_quality = quality
                            highest_link = stream.get('stream_url', None)
                    
                    if highest_link:
                        await ctx.send(f"Stream link: http://{ip}:{port}")
                        ctx.bot.process = subprocess.Popen(['python' if is_windows else 'python3', 'video_streaming/stream.py', str(port), highest_link])                        
                    else:
                        await ctx.send("No valid stream links found in the JSON output.")
                except json.JSONDecodeError:
                    await ctx.send("Failed to decode JSON from the output.")
            else:
                await ctx.send("No JSON output found.")

async def setup(bot):
    await bot.add_cog(Anime(bot))

# Assuming `bot` is already defined somewhere in your code.
# Example:
# bot = commands.Bot(command_prefix="!")
# asyncio.run(setup(bot))
# bot.run("YOUR_BOT_TOKEN")
