from pydantic import BaseModel
from typing import Optional, Dict


class LegacyRankColour(BaseModel):
    main: str
    sub: str


class Guild(BaseModel):
    name: str
    prefix: str
    rank: str
    rankStars: str


class Dungeons(BaseModel):
    total: int
    list: Dict[str, int]


class Raids(BaseModel):
    total: int
    list: Dict[str, int]


class PVP(BaseModel):
    kills: int
    deaths: int


class GlobalData(BaseModel):
    wars: int
    totalLevels: Optional[int] = None
    killedMobs: Optional[int] = None
    chestsFound: int
    dungeons: Dungeons
    raids: Raids
    completedQuests: int
    pvp: PVP
    contentCompletion: Optional[int] = None


class WynncraftPlayer(BaseModel):
    username: str
    online: bool
    server: str
    activeCharacter: Optional[str] = None
    nickname: Optional[str] = None
    uuid: str
    rank: str
    rankBadge: str
    legacyRankColour: LegacyRankColour
    shortenedRank: Optional[str] = None
    supportRank: str
    veteran: Optional[bool] = None
    firstJoin: str
    lastJoin: str
    playtime: float
    guild: Guild
    globalData: GlobalData
    forumLink: Optional[int] = None
    ranking: Dict[str, int]
    previousRanking: Dict[str, int]
    publicProfile: Optional[bool] = None
    onlineStatus: Optional[bool] = None
