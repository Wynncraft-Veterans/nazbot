import logging
import discord
from discord.ext import commands
from lib.lib import unwrap
from lib.wynn_api.player import get_player_main_stats
# logger = Logger()
logger = logging.getLogger('discord.cogs.weeklyevent')
from prisma import Prisma
from bot import Bot

class WeeklyEvent(commands.Cog):
    bot: Bot
    
    def __init__(self, bot: Bot):
        self.bot = bot
        logger.info("API cog initialized")

    @commands.hybrid_group(name="score")
    async def score(self, ctx: commands.Context):
        """Score management commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use: add, set, or leaderboard")
    
    @score.command(name="set")
    async def score_set(self, ctx: commands.Context, user: discord.Member, week: int, value: int):
        """Set user's points"""
        logger.debug(f"Setting {user.id=} score in {week=} to {value=}")
        disc_id = (await self.bot.db.discordaccount.upsert(where={"discUUID": str(user.id)}, data={"create": {"discUUID": str(user.id)}, "update": {}})).id
        event_id = (await self.bot.db.weeklyevent.upsert(where={"week": week}, data={"create": {"week": week}, "update": {}})).id
        await self.bot.db.score.upsert(
            where={
                "weeklyEventId_discordAccountId": {
                    "discordAccountId": disc_id,
                    "weeklyEventId": event_id
                }
            },
            data={
                "create": {
                    "discordAccountId": disc_id,
                    "weeklyEventId": event_id,
                    "score": value
                },
                "update": {
                    "score": {"set": value}
                },
            }
        )
        await ctx.send(f"Set {user.mention}'s score to {value} for week {week}")


    @score.command(name="add")
    async def score_add(self, ctx, user: discord.Member, week: int, value: int):
        """Add points to a user"""
        disc_id = (await self.bot.db.discordaccount.upsert(where={"discUUID": str(user.id)}, data={"create": {"discUUID": str(user.id)}, "update": {}})).id
        event_id = (await self.bot.db.weeklyevent.upsert(where={"week": week}, data={"create": {"week": week}, "update": {}})).id
        await self.bot.db.score.upsert(
            where={
                "weeklyEventId_discordAccountId": {
                    "discordAccountId": disc_id,
                    "weeklyEventId": event_id
                }
            },
            data={
                "create": {
                    "discordAccountId": disc_id,
                    "weeklyEventId": event_id,
                    "score": value
                },
                "update": {
                    "score": {"increment": value}
                },
            }
        )
        
        await ctx.send(f"Added {value} points to {user.mention} for week {week}")
    
    @score.command(name="print")
    async def score_print(self, ctx, user: discord.Member, week: int):
        disc_id = (await self.bot.db.discordaccount.upsert(where={"discUUID": str(user.id)}, data={"create": {"discUUID": str(user.id)}, "update": {}})).id
        event_id = (await self.bot.db.weeklyevent.upsert(where={"week": week}, data={"create": {"week": week}, "update": {}})).id
        score = await self.bot.db.score.find_unique(where={
            "weeklyEventId_discordAccountId": {
                "discordAccountId": disc_id,
                "weeklyEventId": event_id
            },
        })
        if score:
            await ctx.send(f"{user.mention} has {score.score} points for week {week}")
        else:
            await ctx.send(f"{user.mention} does not have any points registered for week {week}")
    
    @score.command(name="leaderboard")
    async def score_leaderboard(self, ctx: commands.Context, week: int, amount: int = 10):
        event_id = (await self.bot.db.weeklyevent.upsert(where={"week": week}, data={"create": {"week": week}, "update": {}})).id
        scores = await self.bot.db.score.find_many(
            take=amount,
            order={"score": "desc"},
            where={
                "weeklyEventId": event_id,
                "score": {"gt": 0}
            },
            include={"discordAccount": True}
        )
        text = '\n'.join(
            f"<@{unwrap(scores[0].discordAccount).discUUID}> {score.score}"
            for score in scores
        )
        if text:
            await ctx.send(text)
        else:
            await ctx.send(f"Noone has any points for week {week}")

async def setup(bot: Bot):
    await bot.add_cog(WeeklyEvent(bot))
    logger.info("API cog loaded successfully")