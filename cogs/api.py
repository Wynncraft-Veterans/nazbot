import logging
from discord.ext import commands
from lib.wynn_api.player import get_player_main_stats
logger = logging.getLogger('discord.cogs.api')
from bot import Bot


class API(commands.Cog):
    bot: Bot
    
    def __init__(self, bot: Bot):
        self.bot = bot
        logger.info("API cog initialized")
    
    @commands.hybrid_command(name='joindate', description='Sync slash commands')
    async def joindate(self, ctx: commands.Context, username_or_uuid: str):
        try:
            player = await get_player_main_stats(username_or_uuid)
            await ctx.send(player.firstJoin)
        except Exception as e:
            logger.error(f'[/joindate] {e}')
            await ctx.send(f'[/joindate] {e}')

async def setup(bot: Bot):
    await bot.add_cog(API(bot))
    logger.info("API cog loaded successfully")