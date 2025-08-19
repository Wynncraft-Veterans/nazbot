import discord
from discord.ext import commands
import asyncio
import os
from lib.logger import Logger
logger = Logger()
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.environ['PREFIX'], intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guild(s)')
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} command(s)')
    except Exception as e:
        logger.error(f'Failed to sync commands: {e}')

async def load_cogs():
    """Load all cogs from the cogs directory"""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f'cogs.{cog_name}')
                logger.info(f'Loaded cog: {cog_name}')
            except Exception as e:
                logger.error(f'Failed to load cog {cog_name}: {e}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.environ['TOKEN'])

if __name__ == '__main__':
    asyncio.run(main())