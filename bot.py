import logging
import discord
from discord.ext import commands
import os
from prisma import Prisma
logger = logging.getLogger('discord.bot')
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class Bot(commands.Bot):
    db: Prisma
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = None # type: ignore
        # should technically be assigned & connected before anything can
        #  actually call this. keeping it None just in case it does happen
        #  it'll be easier to debug like this.
    
    async def setup_hook(self):
        try:
            self.db = Prisma()
            await self.db.connect()
            logger.info('Connected to database')
        except Exception as e:
            logger.error(f'Failed to connect to database: {e}')
        # Then load cogs
        await self._load_cogs()
    
    async def _load_cogs(self):
        """Load all cogs from the cogs directory"""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f'cogs.{cog_name}')
                    logger.info(f'Loaded cog: {cog_name}')
                except Exception as e:
                    logger.error(f'Failed to load cog {cog_name}: {e}')
    
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guild(s)')
        try:
            synced = await self.tree.sync()
            logger.info(f'Synced {len(synced)} command(s)')
        except Exception as e:
            logger.error(f'Failed to sync commands: {e}')
    
    async def close(self):
        logger.info('Shutting down bot...')
        assert self.db is not None
        if self.db:
            await self.db.disconnect()
            logger.info('Disconnected from database')
        await super().close()

if __name__ == '__main__':
    bot = Bot(command_prefix=os.environ['PREFIX'], intents=intents)
    bot.run(os.environ['TOKEN'])