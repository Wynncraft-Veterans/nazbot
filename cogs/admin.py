"""
Commands used to manage the guild itself.
"""
import discord

from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta, timezone
import time
import requests

# Here we name the cog and create a new class for the cog.
class Admin(commands.Cog, name="admin"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="purgelist",
        description="Gets a list of people likely to get purged for inactivity.",
    )
    @commands.has_permissions(manage_messages=True)
    async def testcommand(self, context: Context) -> None:
        """
        This command fetches the guild's members, fetches their last seen date, and compiles a list of everyone who hasn't played in a while.
        """
        # Function to iterate through json
        def iterate(data):
            if isinstance(data, list):
                for item in data:
                    yield from iterate(item)
            elif isinstance(data, dict):
                for key, item in data.items():
                    if key == 'uuid':
                        yield item
                    else:
                        yield from iterate(item)

        def fetchLastSeen(uuid):
            response = requests.get('https://api.wynncraft.com/v3/player/' + uuid)
            time.sleep(0.5)
            return response.json()
        
        embed = discord.Embed(
            title = "VETS Guild Purge List",
            description = "Starting purge list compilation program.",
            color = discord.Color.orange()
        )
        statusMessage = await context.send(embed=embed)
        
        def messageFormatter(messagePayload):
            embed = discord.Embed(
                title = "VETS Guild Purge List",
                description = messagePayload,
                color = discord.Color.orange()
            )
            print(messagePayload)
            return embed
        
        await statusMessage.edit(embed=messageFormatter("Fetching the guild's data from Wynn's API."))
        response = requests.get('https://api.wynncraft.com/v3/guild/prefix/VETS')
        guildObject = response.json()

        await statusMessage.edit(embed=messageFormatter("Extracting the guild's members' UUIDs."))
        parsed = list(iterate(guildObject))
        guildMembers = parsed[1:]

        await statusMessage.edit(embed=messageFormatter("Attaching date field to members' UUIDs."))
        seenDates = dict.fromkeys(guildMembers, datetime.fromisoformat('2012-01-01T00:01:00.000Z'))

        await statusMessage.edit(embed=messageFormatter("From the guild's data, extracting members' dates last seen."))
        await statusMessage.edit(embed=messageFormatter("Please wait. This can take up to 2 minutes."))

        processedItems = 0
        for member in guildMembers:
            processedItems += 1
            await statusMessage.edit(embed=messageFormatter("Please wait. This can take up to 2 minutes [" + str(round(100 * processedItems / len(guildMembers))) + "%]"))

            playerObject = fetchLastSeen(member)
            seenDate = datetime.fromisoformat(playerObject['lastJoin'])

            seenDates[member] = seenDate


        await statusMessage.edit(embed=messageFormatter("Filtering guild member list to kickable date deltas."))
        await statusMessage.edit(embed=messageFormatter("Resolving kickable player UUIDs to usernames."))
        await statusMessage.edit(embed=messageFormatter("Please wait. This may take up to 15 seconds."))
        kickList = ""
        for member in guildMembers:
            kickDate = datetime.now(timezone.utc) - timedelta(days=14)
            seenDate = seenDates[member]
            if seenDate < kickDate:
                timeSpentAway = datetime.now(timezone.utc) - seenDate

                mojangQuery = requests.get('https://api.minecraftservices.com/minecraft/profile/lookup/' + member)
                playerUsernameObject = mojangQuery.json()
                playerUsername = playerUsernameObject['name']
                kickList += "- `" + playerUsername + "` has been away for " + str(timeSpentAway.days) + " days.\n"

        embed = discord.Embed(
            title = "VETS Guild Purge List",
            description = kickList,
            color = discord.Color.red()
        )

        await statusMessage.edit(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Admin(bot))
