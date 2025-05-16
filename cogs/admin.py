"""
Commands used to manage the guild itself.
"""
import discord

from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta, timezone
import time
import requests

# Cog naming and creation.
class Admin(commands.Cog, name="admin"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Commands in cog.

    @commands.hybrid_command(
        name="purgelist",
        description="Gets a list of people likely to get purged for inactivity.",
    )
    @commands.has_permissions(manage_messages=True)
    async def purgecommand(self, context: Context) -> None:
        """
        This command fetches the guild's members, fetches their last seen date, and compiles a list of everyone who hasn't played in a while.
        """
        # Message feedback system
        embed = discord.Embed(
            title = "VETS Guild Purge List",
            description = "Starting purge list compilation program.",
            color = discord.Color.orange()
        )
        statusMessage = await context.send(embed=embed)
        
        async def sendReply(messagePayload):
            embed = discord.Embed(
                title = "VETS Guild Purge List",
                description = messagePayload,
                color = discord.Color.orange()
            )
            print(messagePayload)
            await statusMessage.edit(embed=embed)
            return

        # Function to iterate through json
        def iterate(filter, data):
            if isinstance(data, list):
                for item in data:
                    yield from iterate(filter, item)
            elif isinstance(data, dict):
                for key, item in data.items():
                    if key == filter:
                        yield item
                    else:
                        yield from iterate(filter, item)

        # A system to fetch shit from APIs.
        async def fetchAPI(linkToAPI):
            response = requests.get(linkToAPI)
            while response.status_code == 429:
                await sendReply("We're getting ratelimited by an API. Trying again in a few seconds")
                time.sleep(2.5)
                response = requests.get(linkToAPI)
            return response.json()
        
        # Fetch a list of the guild's members' UUIDs.
        async def fetchGuildList():
            await sendReply("Fetching the guild's data from Wynn's API.")
            guildObject = await fetchAPI('https://api.wynncraft.com/v3/guild/prefix/VETS')

            await sendReply("Extracting the guild's members' UUIDs")
            guildUUIDsObject = list(iterate("uuid", guildObject))
            guildUUIDs = guildUUIDsObject[1:]

            return guildUUIDs
        
        # Fetch a list of members' dates last seen
        async def generateKickList():
            guildUUIDs = await fetchGuildList()
            await sendReply("Attaching date field to members' UUIDs.")
            guildDatesList = dict.fromkeys(guildUUIDs, datetime.fromisoformat('2012-01-01T00:01:00.000Z'))

            await sendReply("From the guild's data, extracting members' dates last seen. [0%]")

            processedItems = 0
            for uuid in guildDatesList:
                processedItems += 1
                await sendReply("From the guild's data, extracting members' dates last seen. [" + str(round(100 * processedItems / len(guildDatesList))) + "%]")

                playerObject = await fetchAPI('https://api.wynncraft.com/v3/player/' + uuid)
                seenDate = datetime.fromisoformat(playerObject['lastJoin'])
                guildDatesList[uuid] = seenDate

            await sendReply("Filtering kickable date deltas and resolving to usernames")

            kicklist = ""
            processedItems = 0
            kickDate = datetime.now(timezone.utc) - timedelta(days=14)

            for uuid in guildDatesList:
                processedItems += 1
                await sendReply("Filtering kickable date deltas and resolving to usernames. [" + str(round(100 * processedItems / len(guildDatesList))) + "%]")

                seenDate = guildDatesList[uuid]

                if seenDate < kickDate:
                    timeSpentAway = datetime.now(timezone.utc) - seenDate
                    playerUsernameObject = await fetchAPI('https://api.minecraftservices.com/minecraft/profile/lookup/' + uuid)
                    playerUsername = playerUsernameObject['name']

                    kicklist += "- `" + playerUsername + "` has been away for " + str(timeSpentAway.days) + " days.\n"

            return kicklist

        kickList = await generateKickList()
        embed = discord.Embed(
            title = "VETS Guild Purge List",
            description = kickList,
            color = discord.Color.red()
        )

        await statusMessage.edit(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Admin(bot))
