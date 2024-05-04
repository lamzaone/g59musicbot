import discord
from discord.ext import commands, tasks
import asyncio

class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_check.start()

    @tasks.loop(seconds=5)  # Check for updates every 5 seconds
    async def update_check(self):
        if bot.check_for_updates(is_windows):
            owner = await self.bot.fetch_user(self.bot.owner_id)  # Fetch the bot owner's user object
            if owner:
                dm_channel = await owner.create_dm()  # Create a DM channel with the owner
                message = await dm_channel.send("An update is available. Would you like to update now?")
                # React to the message with "Yes" and "Not Now" options
                await message.add_reaction("✅")  # Yes
                # await message.add_reaction("⏰")  # Not Now

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:  # Ignore reactions by the bot itself
            return

        if reaction.message.channel.type == discord.ChannelType.private and user.id == self.bot.owner_id:  # Check if the reaction is in a private message with the owner
            if reaction.emoji == "✅":  # If the reaction is "Yes"
                await reaction.message.channel.send("Updating now...")
                # bot.update(is_windows)
                self.update_check.start()  # Restart the update check loop
            # if reaction.emoji == "⏰":  # If the reaction is "Yes"
            #     await reaction.message.channel.send("2h later, see you")
            #     # update.update(is_windows)
            #     await asyncio.sleep(2*60)
            #     self.update_check.start()  # Restart the update check loop

def setup(bot):
    bot.add_cog(Update(bot))