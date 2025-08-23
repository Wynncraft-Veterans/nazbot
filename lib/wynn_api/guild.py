import asyncio
from lib.wynn_api.requestor import Requestor
from lib.wynn_api.guild_models import Guild

requestor = Requestor()

async def get_guild(guild_name: str) -> Guild:
    response = await requestor.get(f"https://api.wynncraft.com/v3/guild/{guild_name}?identifier=username")
    guild = Guild(**await response.json())
    return guild
