import asyncio
from datetime import datetime, timedelta, timezone
import logging
import discord
from discord.ext import commands, tasks
from lib.lib import unwrap
from lib.wynn_api.guild import get_guild
from lib.wynn_api.player import get_player_main_stats
from orm import MinecraftAccount
logger = logging.getLogger('discord.cogs.activity')
from prisma import Prisma
from bot import Bot
import dateparser



class Activity(commands.Cog):
    bot: Bot
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.check_guild.start()
        logger.info("Activity cog initialized")

    @tasks.loop(minutes=11)
    async def check_guild(self):
        logger.info("Doing check_guild task")
        guild = await get_guild("Returners")
        members = [*guild.members.all_members()]
        online = [m for m in members if m.online]
        offline = [m for m in members if not m.online]
        logger.info("checking online members")
        for member in online:
            await MinecraftAccount.update_or_create(
                uuid=member.uuid,
                defaults={
                    "guild": guild.name,
                    "username": member.username,
                    "last_online": datetime.now()
                }
            )
            _ = await self.bot.db.minecraftaccount.upsert(
                where={
                    "uuid": member.uuid
                },
                data={
                    "create": {
                        "guild": guild.name,
                        "uuid": member.uuid,
                        "username": member.username,
                        "lastOnline": datetime.now()
                    },
                    "update": {
                        "guild": guild.name,
                        "username": member.username,
                        "lastOnline": datetime.now()
                    }
                }
            )
        for member in offline:
            _ = await self.bot.db.minecraftaccount.upsert(
                where={
                    "uuid": member.uuid
                },
                data={
                    "create": {
                        "guild": guild.name,
                        "uuid": member.uuid,
                        "username": member.username,
                        "lastOnline": datetime.fromtimestamp(0)
                    },
                    "update": {
                        "guild": guild.name,
                        "username": member.username,
                    }
                }
            )
        logger.info("members to check")
        members_to_check = await self.bot.db.minecraftaccount.find_many(
            where={
                "OR": [
                    {
                        "lastOnline": {
                            "lt": datetime.now() - timedelta(weeks=1)
                        },
                        "uuid": {
                            "in": [m.uuid for m in offline]
                        }
                    },
                    {
                        "lastOnline": {
                            "lt": datetime.now() - timedelta(weeks=1)
                        },
                        "uuid": {
                            "not_in": [m.uuid for m in members]
                        }
                    }
                ]
            }
        )
        logger.info(f"checking members {len(members_to_check)=}")
        for member in members_to_check:
            logger.info(f"{member.username=} {member.uuid=}")
            player = await get_player_main_stats(member.uuid)
            guild_name = player.guild.name if player.guild else None
            await self.bot.db.minecraftaccount.upsert(
                where={
                    "uuid": player.uuid
                },
                data={
                    "create": {
                        "guild": guild_name,
                        "lastOnline": player.lastJoin,
                        "username": player.username,
                        "uuid": player.uuid
                    },
                    "update": {
                        "guild": guild_name,
                        "username": player.username,
                        "lastOnline": player.lastJoin,
                    },
                }
            )

        alerts = []
        now = datetime.now(timezone.utc)
        if len(online) <= self.bot.config.GUILD_DEAD_WHEN and now - self.bot.nosql.LAST_DEAD_ALERT <= self.bot.config.GUILD_DEAD_ALERT_DELTA:
            self.bot.nosql.LAST_DEAD_ALERT = now
            alerts.append(self._low_count_alert())
        
        if guild.members.total >= self.bot.config.GUILD_FULL_WHEN and now - self.bot.nosql.LAST_CAP_ALERT<= self.bot.config.GUILD_FULL_ALERT_DELTA:
            self.bot.nosql.LAST_CAP_ALERT = now
            alerts.append(self._guild_full_alert())

        logger.info(f"{len(online)=}")

        await asyncio.gather(*alerts)

    
    async def _low_count_alert(self):
        logger.warning("Low player count!")
        channel = self.bot.get_channel(self.bot.config.GUILD_DEAD_ALERT_CHANNEL)
        assert isinstance(channel, discord.TextChannel)
        await channel.send(f"<@&{self.bot.config.GUILD_DEAD_ALERT_ROLE}> ur wynn guild is ded")

    async def _guild_full_alert(self):
        logger.warning("Guild is full!")
        channel = self.bot.get_channel(self.bot.config.GUILD_FULL_ALERT_CHANNEL)
        assert isinstance(channel, discord.TextChannel)
        await channel.send(f"<@&{self.bot.config.GUILD_FULL_ALERT_ROLE}> ur wynn guild is full")

    @commands.hybrid_command(name='force_check')
    @commands.has_permissions(administrator=True)
    async def force_check(self, _ctx: commands.Context):
        await self.check_guild()
    
    @commands.hybrid_command(name='purgelist')
    async def purgelist(self, ctx: commands.Context):
        absent_guild_members = await self.bot.db.minecraftaccount.find_many(
            where={
                "guild": "Returners",
                "lastOnline": {
                    "lt": datetime.now() - timedelta(weeks=2)
                }
            },
            order={
                "lastOnline": "desc"
            }
        )

        if not absent_guild_members:
            await ctx.send("No members have been away for more than 2 weeks.")
            return
        logger.info([m.lastOnline.tzinfo for m in absent_guild_members])
        logger.info(datetime.now().tzinfo)
        await ctx.send("\n".join(
            f"- `{m.username}` has been away for {(datetime.now(timezone.utc) - m.lastOnline).days} days."
            for m in absent_guild_members
        ))

    @commands.hybrid_command(name='shout')
    async def shout(self, ctx: commands.Context):
        await self.bot.db.shout.create(
            data={
                "shouter": {
                    "connect_or_create": {
                        "where": {
                            "discUUID": str(ctx.author.id)
                        },
                        "create": {
                            "discUUID": str(ctx.author.id)
                        }
                    }
                }
            }
        )
        await ctx.send(f"Thank you for helping the guild, {ctx.author.mention}!\nYour shout has been recorded.")
        
    @commands.hybrid_command(name='last_shout')
    async def last_shout(self, ctx: commands.Context):
        shouts = await self.bot.db.shout.find_many(
            take=3,
            order={
                "createdAt": "desc"
            },
            include={
                "shouter": True
            }
        )
        lines = []
        for shout in shouts:
            delta = datetime.now(timezone.utc) - shout.createdAt
            user = await self.bot.fetch_user(int(unwrap(shout.shouter).discUUID))
            lines.append(f"{user.mention} - {delta.seconds//3600} hours and {(delta.seconds//60)%60} minutes ago")
            
        if lines:
            await ctx.send('\n'.join(lines), silent=True)
        else:
            await ctx.send("There have been no recorded shouts.")

    @commands.hybrid_command(name='shouterboard')
    async def shouterboard(self, ctx: commands.Context):
        shout_counter = await self.bot.db.shout.group_by(
            by=["discordAccountId"],
            count=True
        )
        c = shout_counter
        logger.info(shout_counter)
        # counter = sorted(c, key=lambda k_v: k_v[1])



async def setup(bot: Bot):
    await bot.add_cog(Activity(bot))
    logger.info("Activity cog loaded successfully")