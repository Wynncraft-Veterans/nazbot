"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.3.0
"""
import discord

from discord.ext import commands
from discord.ext.commands import Context


# Here we name the cog and create a new class for the cog.
class Return(commands.Cog, name="return"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="return",
        description="Commands implemented for weekly returns.",
    )
    @commands.has_permissions(manage_messages=True)
    async def testcommand(self, context: Context) -> None:
        embed = discord.Embed(description="This feature has not yet been implemented!", color=0xBEBEFE)
        await context.send(embed=embed)
        pass


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Return(bot))
