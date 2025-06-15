"""
A chess tracking system
Based on kenneth-hendrix/PingPongBot
"""
import discord

from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import json
import requests
import os
import io

# Here we name the cog and create a new class for the cog.

intents = discord.Intents.default()


client = discord.Client(intents=intents)
bot = app_commands.CommandTree(client)
token = os.getenv('TOKEN')
guildID = int(os.getenv('GUILD_ID'))

try:
    with open(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/database/elo_data.json", 'r') as f:
        elo_data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    elo_data = {}
        
class Return(commands.Cog, name="chess"):

    def __init__(self, bot) -> None:
        self.bot = bot

    def save_elo_data(self):
        with open(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/database/elo_data.json", 'w') as f:
            json.dump(elo_data, f, indent=4)

    async def update_elo_ratings(self, winner_id, loser_id):
        winner_elo = elo_data.get(str(winner_id), 1000)
        loser_elo = elo_data.get(str(loser_id), 1000)

        k_factor = 32
        expected_win = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
        expected_lose = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))

        winner_elo = round(winner_elo + k_factor * (1 - expected_win))
        loser_elo = round(loser_elo + k_factor * (0 - expected_lose))

        elo_data[str(winner_id)] = winner_elo
        elo_data[str(loser_id)] = loser_elo

        self.save_elo_data()

    def fetch_user(self, userid):
        url = f'https://discord.com/api/v9/users/{userid}'
        headers = {
            'Authorization': f'Bot {token}'
        }

        response = requests.get(url, headers=headers)

        if not response.ok:
            raise ValueError(f"Error status code: {response.status_code}")
        resp = response.json()
        if (resp['global_name']):
            return resp['global_name']
        return resp['username']
    
    @commands.hybrid_command(
        name="bottom_rankings",
        description="Gets the the rankings of the bottom 10 cursed chess players.",
    )
    async def display_bottom_rankings(self, context: Context) -> None:
        sorted_players = sorted(elo_data.items(), key=lambda x: x[1])

        rank_text = "\n".join(f"{i+1}. {self.fetch_user(player)} - {elo}" for i,
                              (player, elo) in enumerate(sorted_players[:10]))
        await context.send(f"**Bottom 10 Rankings:**\n{rank_text}")

    @commands.hybrid_command(
        name="match",
        description="Record a match result.",
    )
    @commands.has_permissions(manage_messages=True)
    async def record_match(self, context: Context, winner: discord.User, loser: discord.User) -> None:
        await self.update_elo_ratings(winner.id, loser.id)
        await context.send(f"Match confirmed: {winner.mention} vs {loser.mention} - {winner.display_name} won!", ephemeral=False)

    @commands.hybrid_command(
        name="rankings",
        description="Gets the ranking of the current top 10 cursed chess players.",
    )
    async def display_rankings(self, context: Context) -> None:
        sorted_players = sorted(
            elo_data.items(), key=lambda x: x[1], reverse=True)

        rank_text = "\n".join(f"{i+1}. {self.fetch_user(player)} - {elo}" for i,
                              (player, elo) in enumerate(sorted_players[:10]))
        await context.send(f"**Top 10 Rankings:**\n{rank_text}")
        
    @commands.hybrid_command(
        name="export_rankings",
        description="Gets the ranking of the current top 10 cursed chess players.",
    )
    async def export_rankings(self, context: Context, inFile: bool = False) -> None:
        sorted_players = sorted(elo_data.items(), key=lambda x: x[1], reverse=True)
        rank_text = "\n".join(f"{i+1},{self.fetch_user(player)},{elo}" for i,
                                (player, elo) in enumerate(sorted_players))
            
        if inFile:
            await context.send("Exported csv", file=discord.File(io.StringIO(rank_text), filename="chess_export.csv"))
        else:
            await context.send(f"**Data Export**\n```less\n{rank_text}```")

    @commands.hybrid_command(
        name="myelo",
        description="Gets a readout of your own cursed chess elo.",
    )
    async def display_my_elo(self, context: Context) -> None:
        user_elo = elo_data.get(str(context.author.id), "Not found")
        await context.send(f"{context.author.mention}, your current Elo rating is: {user_elo}")

    @commands.hybrid_command(
        name="elo",
        description="Gets the cursed chess ranking of the mentioned user.",
    )
    @commands.has_permissions(manage_messages=True)
    async def display_elo(self, context: Context, user: discord.User) -> None:
        user_elo = elo_data.get(str(user.id), "Not found")
        await context.send(f"{user.global_name}'s current Elo rating is: {user_elo}")

    # Load Cog
async def setup(bot) -> None:
    await bot.add_cog(Return(bot))
