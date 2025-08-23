import logging
import discord
from discord.ext import commands, tasks
from lib.lib import unwrap
from lib.wynn_api.player import get_player_main_stats
logger = logging.getLogger('discord.cogs.activity')
from prisma import Prisma
from bot import Bot

class Activity(commands.Cog):
    bot: Bot
    
    def __init__(self, bot: Bot):
        self.bot = bot
        logger.info("Activity cog initialized")

    @tasks.loop(hours=1)
    async def check_people_online(self):
        
        ...

    async def _low_count_alert(self):
        ...

async def setup(bot: Bot):
    await bot.add_cog(Activity(bot))
    logger.info("Activity cog loaded successfully")