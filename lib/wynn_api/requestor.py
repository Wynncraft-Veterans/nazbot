import asyncio
import collections
import time
from typing import Any, Optional
import aiohttp
from aiohttp import ClientResponse


class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Requestor(metaclass=SingletonMeta):
    def __init__(self):
        self.deque: collections.deque[float] = collections.deque()
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def _clean_deque(self):
        now = time.time()

        while self.deque and (now - self.deque[0]) > 60:
            self.deque.popleft()
    
    async def _rate_limit(self):
        await self._clean_deque()
        
        now = time.time()
        
        if len(self.deque) >= 110:
            sleep_time = 60 - (now - self.deque[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                await self._clean_deque()
        
        self.deque.append(now)
    
    async def get(self, url: str, **kwargs: Any) -> ClientResponse:
        await self._rate_limit()
        session = await self._get_session()
        return await session.get(url, **kwargs)
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()