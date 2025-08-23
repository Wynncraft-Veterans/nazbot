import asyncio
from lib.wynn_api.requestor import Requestor
from lib.wynn_api.player_models import WynncraftPlayer

requestor = Requestor()

async def get_player_main_stats(username_or_uuid: str) -> WynncraftPlayer:
    response = await requestor.get(f"https://api.wynncraft.com/v3/player/{username_or_uuid}")
    player = WynncraftPlayer(**await response.json())
    return player
