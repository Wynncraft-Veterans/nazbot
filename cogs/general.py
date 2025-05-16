"""
Miscellaneous commands implementing assorted user-facing functionality.
"""

import discord
import aiohttp
import requests
import time

from discord.ext import commands
from discord.ext.commands import Context

# Stuff for the profer finder
class ProfSelection(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="armouring", description="Helmets and/or chestplates.", emoji="🪖"
            ),
            discord.SelectOption(
                label="tailoring", description="Leggings and/or boots.", emoji="👞"
            ),
            discord.SelectOption(
                label="jeweling", description="Bracelets, rings, and/or necklaces.", emoji="💍"
            ),
            discord.SelectOption(
                label="weaponsmithing", description="Spears an/or daggers.", emoji="🗡️"
            ),
            discord.SelectOption(
                label="woodworking", description="Wands, bows, and/or reliks.", emoji="🏹"
            ),
            discord.SelectOption(
                label="alchemism", description="Potions.", emoji="⚗️"
            ),
            discord.SelectOption(
                label="scribing", description="Scrolls.", emoji="📜"
            ),
            discord.SelectOption(
                label="cooking", description="Food.", emoji="🍗"
            ),
        ]
        super().__init__(
            placeholder="What do you need your profer to make?",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        # Send initial message
        embed = discord.Embed(
            title = "Profer list",
            description = "Compiling a list of profers able to craft your item.",
            color = discord.Color.blurple()
        )       
        await interaction.response.edit_message(embed=embed,content=None,view=None)

        theMessage = await interaction.followup.send(embed=embed)

        # A system to edit the working message.
        async def sendReply(messagePayload):
            embed = discord.Embed(
                title = "Profer list",
                description = messagePayload,
                color = discord.Color.blurple()
            )
            print(messagePayload)
            await theMessage.edit(embed=embed)

        # A system to fetch shit from APIs.
        async def fetchAPI(linkToAPI):
            response = requests.get(linkToAPI)
            while response.status_code == 429:
                await sendReply("We're getting ratelimited by an API. Trying again in a few seconds")
                time.sleep(2.5)
                response = requests.get(linkToAPI)
            return response.json()
        
        # A function to transform a guild object into uuids, with a few problems solved by parseGuildObject.
        def iterate(filter,object):
            if isinstance(object, list):
                for item in object:
                    yield from iterate(filter,item)
            elif isinstance(object, dict):
                for key, item in object.items():
                    if key == filter:
                        yield item
                    else:
                        yield from iterate(filter,item)

        # Transforms the API's guild tag response into a list of member uuids with blank online and prof fields.
        def prepareMemberList(guildObject):
            parsedObject = list(iterate("uuid",guildObject))
            memberList = parsedObject[1:]

            memberDefaults = {'online' : False, 'profLevel' : 0}
            preparedMemberList =  dict.fromkeys(memberList, memberDefaults)
            return preparedMemberList
        
        # Given a uuid, figure out the highest prof level and online status
        async def fetchUserInfo(profession, UUID):
            playerObject = await fetchAPI("https://api.wynncraft.com/v3/player/" + UUID + "?fullResult")
            professionObject = list(iterate(profession, playerObject))
            professionLevels = list(iterate("level", professionObject))
            professionLevel = max(professionLevels)

            onlineStatusList = list(iterate("online", playerObject))
            onlineStatus = onlineStatusList[0]

            extractedInfo = {'online' : onlineStatus, 'profLevel' : professionLevel}
            return extractedInfo
        
        # Given a profession, generate the list of all guild members and populate it.
        async def populateProferData(profession):
            await sendReply(f"Fetching a list of the guild's members from the API")
            guildObject =  await fetchAPI('https://api.wynncraft.com/v3/guild/prefix/VETS')
            memberUUIDsList = prepareMemberList(guildObject)

            await sendReply(f"Pinging the API for info on every member of the guild. [0%]")
            processedItems = 0
            for uuid in memberUUIDsList:
                processedItems += 1
                await sendReply("Pinging the API for info on every member of the guild. [" + str(round(100 * processedItems / len(memberUUIDsList))) + "%]")
                memberUUIDsList[uuid] = await fetchUserInfo(profession, uuid)

            await sendReply(f"Resolving UUIDs of relevant members. [0%]")
            voidProfers = {}
            dernicProfers = {}
            processedItems = 0
            for uuid in memberUUIDsList:
                processedItems +=1
                await sendReply("Resolving UUIDs of relevant members. [" + str(round(100 * processedItems / len(memberUUIDsList))) + "%]")
                memberData = memberUUIDsList[uuid]
                if 100 <= memberData["profLevel"] <= 102:
                    playerUsernameObject = await fetchAPI('https://api.minecraftservices.com/minecraft/profile/lookup/' + uuid)
                    playerUsername = playerUsernameObject['name']
                    playerStatus = memberData["online"]
                    voidProfers[playerUsername] = playerStatus
                elif 103 <= memberData["profLevel"]:
                    playerUsernameObject = await fetchAPI('https://api.minecraftservices.com/minecraft/profile/lookup/' + uuid)
                    playerUsername = playerUsernameObject['name']
                    playerStatus = memberData["online"]
                    dernicProfers[playerUsername] = playerStatus

            onlineVoidProfers = [username for (username,status) in voidProfers.items() if status]
            offlineVoidProfers = voidProfers.keys() - onlineVoidProfers
            onlineDernicProfers = [username for (username,status) in dernicProfers.items() if status]
            offlineDernicProfers = dernicProfers.keys() - onlineDernicProfers

            resultMessage = ""
            if onlineVoidProfers or onlineDernicProfers:
                resultMessage += "```Online members:```\n"
                if onlineDernicProfers:
                    resultMessage += "**Able to do dernic " + profession + " crafts:**\n"
                    for username in onlineDernicProfers:
                        resultMessage += "- `" + username + "`\n"
                if onlineVoidProfers:
                    resultMessage += "\n**Able to do non-dernic " + profession + " crafts:**\n"
                    for username in onlineVoidProfers:
                        resultMessage += "- `" + username + "`\n"

            if offlineVoidProfers or offlineDernicProfers:
                resultMessage += "```Offline members:```\n"
                if offlineDernicProfers:
                    resultMessage += "**Able to do dernic " + profession + " crafts:**\n"
                    for username in offlineDernicProfers:
                        resultMessage += "- `" + username + "`\n"
                if offlineVoidProfers:
                    resultMessage += "\n**Able to do non-dernic " + profession + " crafts:**\n"
                    for username in offlineVoidProfers:
                        resultMessage += "- `" + username + "`\n"

            return resultMessage
            
        profession = str(self.values[0])
        await sendReply("Please wait as we generate a list of guild members with high " + profession + " levels")
        
        proferData = await populateProferData(profession)

        await sendReply(proferData)
        
class ProfSelectorView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(ProfSelection())

# Cog creation and naming
class General(commands.Cog, name="general"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Commands in cog

    @commands.hybrid_command(name="randomfact", description="Get a random fact.")
    async def randomfact(self, context: Context) -> None:
        """
        Get a random fact.

        :param context: The hybrid command context.
        """
        # Template for web requests.
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://uselessfacts.jsph.pl/random.json?language=en"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(description=data["text"], color=0xD75BF4)
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(
        name="findprofer", description="Find guild members able to craft your item."
    )
    @commands.cooldown(1,120)
    async def proferfinder(self, context: Context) -> None:
        """
        Find guild members able to craft your item.

        :param context: The hybrid command context.
        """
        view = ProfSelectorView()
        profFinderMessage = await context.send("Please make your choice", view=view)

# Add and load cog.
async def setup(bot) -> None:
    await bot.add_cog(General(bot))
