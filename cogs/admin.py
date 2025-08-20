import logging
from discord.ext import commands
logger = logging.getLogger('discord.cogs.admin')
from bot import Bot

class Admin(commands.Cog):
    bot: Bot
    
    def __init__(self, bot: Bot):
        self.bot = bot
        logger.info("Admin cog initialized")
    
    @commands.hybrid_command(name='sync', description='Sync slash commands')
    @commands.has_permissions(administrator=True)
    async def sync_commands(self, ctx: commands.Context):
        """Manually sync slash commands"""
        logger.info(f"Sync command initiated by {ctx.author} ({ctx.author.id}) in {ctx.guild}")
        try:
            synced = await self.bot.tree.sync()
            logger.info(f"Successfully synced {len(synced)} slash commands")
            await ctx.send(f'Successfully synced {len(synced)} command(s)')
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            await ctx.send(f'Failed to sync commands: {e}')
    
    @commands.hybrid_command(name='reload', description='Reload a specific cog')
    @commands.has_permissions(administrator=True)
    async def reload_cog(self, ctx: commands.Context, cog_name: str):
        """Reload a specific cog"""
        logger.info(f"Reload command initiated by {ctx.author} ({ctx.author.id}) for cog '{cog_name}'")
        try:
            await self.bot.reload_extension(f'cogs.{cog_name}')
            logger.info(f"Successfully reloaded cog '{cog_name}'")
            await ctx.send(f'Successfully reloaded {cog_name}')
            await self.bot.tree.sync()
            logger.debug(f"Synced slash commands after reloading '{cog_name}'")
        except Exception as e:
            logger.error(f"Failed to reload cog '{cog_name}': {e}")
            await ctx.send(f'Failed to reload {cog_name}: {e}')
    
    @commands.hybrid_command(name='load', description='Load a specific cog')
    @commands.has_permissions(administrator=True)
    async def load_cog(self, ctx: commands.Context, cog_name: str):
        """Load a specific cog"""
        logger.info(f"Load command initiated by {ctx.author} ({ctx.author.id}) for cog '{cog_name}'")
        try:
            await self.bot.load_extension(f'cogs.{cog_name}')
            logger.info(f"Successfully loaded cog '{cog_name}'")
            await ctx.send(f'Successfully loaded {cog_name}')
            await self.bot.tree.sync()
            logger.debug(f"Synced slash commands after loading '{cog_name}'")
        except Exception as e:
            logger.error(f"Failed to load cog '{cog_name}': {e}")
            await ctx.send(f'Failed to load {cog_name}: {e}')
    
    @commands.hybrid_command(name='unload', description='Unload a specific cog')
    @commands.has_permissions(administrator=True)
    async def unload_cog(self, ctx: commands.Context, cog_name: str):
        """Unload a specific cog"""
        logger.info(f"Unload command initiated by {ctx.author} ({ctx.author.id}) for cog '{cog_name}'")
        try:
            await self.bot.unload_extension(f'cogs.{cog_name}')
            logger.info(f"Successfully unloaded cog '{cog_name}'")
            await ctx.send(f'Successfully unloaded {cog_name}')
            await self.bot.tree.sync()
            logger.debug(f"Synced slash commands after unloading '{cog_name}'")
        except Exception as e:
            logger.error(f"Failed to unload cog '{cog_name}': {e}")
            await ctx.send(f'Failed to unload {cog_name}: {e}')

async def setup(bot: Bot):
    await bot.add_cog(Admin(bot))
    logger.info("Admin cog loaded successfully")