"""
Miscellaneous commands implementing assorted user-facing functionality.
"""

import discord
import aiohttp
import requests
import time

from discord.ext import commands
from discord.ext.commands import Context
from discord import Client

# Responds to any message sent in market channel with hello world.

class Market(commands.Cog, name="market"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.CHANNEL_ID = 1316957148332298260
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        
        if message.channel.id != self.CHANNEL_ID:
            return
        
        try:
            # Only send the welcome text if this author has no previous messages in the channel
            has_posted_before = False
            # Scan recent history for a prior message by this author.
            # Increase limit if you expect large message counts; keep reasonable to avoid rate limits.
            async for m in message.channel.history(limit=450, oldest_first=False):
                if m.author.id == message.author.id and m.id != message.id:
                    has_posted_before = True
                    break

            if not has_posted_before:
                await message.channel.send("""# Welcome to the #legacy-trade-market!

Several potential buyers subscribe to this channel!
```diff
- BEFORE PUBLISHING ANYTHING PLEASE NOTE: 
```
## 1. **Published messages are sent without usernames!**
You need to provide the buyer some way to contact you.
The best way to do so is to @mention yourself in the post! 

## 2. **Be brief and only post what you have!**
Item name, details, etc. are useful; conversations are not.
If a collector from another discord server is interested, they will contact you.

## 3. **Include everything in one message!**
There is a substantial rate limit on publishing wares.
Please only publish your message when you are sure it is complete!""")
        except Exception as e:
            print(f"Error sending message: {e}")
        
# Add and load cog.
async def setup(bot) -> None:
    await bot.add_cog(Market(bot))
