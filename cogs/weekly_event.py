import logging
import discord
from discord.ext import commands
from lib.wynn_api.player import get_player_main_stats
# logger = Logger()
logger = logging.getLogger('discord.cogs.weeklyevent')
from prisma import Prisma
from bot import Bot

class API(commands.Cog):
    bot: Bot
    prisma: Prisma
    
    def __init__(self, bot: Bot):
        self.bot = bot
        logger.info("API cog initialized")

    @commands.hybrid_group(name="score")
    async def score(self, ctx):
        """Score management commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use: add, set, or leaderboard")
    
    @score.command(name="set")
    async def score_set(self, ctx, user: discord.Member, week: int, value: int):
        """Set user's points"""
        logger.debug(f"Setting {user.id=} score in {week=} to {value=}")
        await ctx.send(f"Set {user.mention}'s score to {value} for week {week}")

async def setup(bot: Bot):
    await bot.add_cog(API(bot))
    logger.info("API cog loaded successfully")