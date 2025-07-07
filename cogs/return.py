"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.3.0
"""
import discord

from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
import os
import json
import pickle

class FeedbackForm(discord.ui.Modal, title="Feeedback"):

    feedbackQuestionOne = discord.ui.TextInput(
        label="What are some things the guild does well?",
        style=discord.TextStyle.long,
        placeholder="I really enjoy the guild's atmosphere as well as the resources made available to returning players",
        required=True,
        max_length=1950,
    )
    
    feedbackQuestionTwo = discord.ui.TextInput(
        label="How does VETS struggle & what can we improve?",
        style=discord.TextStyle.long,
        placeholder="The guild could do more to help me with this and that. We should also do more improve [something]",
        required=True,
        max_length=1950,
    )
        
    feedbackQuestionThree = discord.ui.TextInput(
        label="How can we improve our engagement/activity?",
        style=discord.TextStyle.long,
        placeholder="Focus on reinviting members rejoining from inactivity kicks, have more events outside the game, ...",
        required=False,
        max_length=1950,
    )
            
    feedbackQuestionFour = discord.ui.TextInput(
        label="Any ideas for nazbot or the website?",
        style=discord.TextStyle.long,
        placeholder="The website should include a wiki module and the discord bot (nazbot) should implement anni pings.",
        required=False,
        max_length=1950,
    )
        
    feedbackQuestionFive = discord.ui.TextInput(
        label="Have any feedback/ideas for returns?",
        style=discord.TextStyle.long,
        placeholder="I enjoy events like [a], but dislike events like [b]. You might want to try making [idea] an event.",
        required=False,
        max_length=1950,
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.answer1 = str(self.feedbackQuestionOne)
        self.answer2 = str(self.feedbackQuestionTwo)
        self.answer3 = str(self.feedbackQuestionThree)
        self.answer4 = str(self.feedbackQuestionFour)
        self.answer5 = str(self.feedbackQuestionFive)
        self.stop()
        
# Here we name the cog and create a new class for the cog.
class Return(commands.Cog, name="return"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="return",
        description="Commands implemented for weekly returns.",
    )
    @commands.has_permissions(manage_messages=True)
    async def testcommand(self, context: Context) -> None:
        embed = discord.Embed(description="This feature has not yet been implemented!", color=0xBEBEFE)
        await context.send(embed=embed)
        pass

    @commands.hybrid_command(   
        name="export_feedback",
        description="Gets a list of users who submitted feedback as a return.",
    )
    @commands.has_permissions(manage_messages=True)
    async def export_rankings(self, context: Context) -> None:
        try:
            feedback_data = pickle.load(open(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/database/feedback.pickle", 'rb'))
        except (OSError, IOError) as e:
            feedback_data = set()
            pickle.dump(feedback_data, open(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/database/feedback.pickle", 'wb'))
        
        await context.send(f"The following users submitted stuff for this week's return:")
        
        for userid in feedback_data:
            await context.send(f"<@!{userid}>")
        
    @app_commands.command(
        name="feedback", description="Submit some feedback to the guild."
    )
    @commands.cooldown(1, 200, commands.BucketType.user)
    async def feedback(self, interaction: discord.Interaction) -> None:
        """
        Submit feedback to the guild.

        :param context: The hybrid command context.
        """
        feedback_form = FeedbackForm()
        await interaction.response.send_modal(feedback_form)

        await feedback_form.wait()
        interaction = feedback_form.interaction
        await interaction.response.send_message(
            embed=discord.Embed(
                description="Thank you for your feedback! It has been sent to VETS' staff!",
                color=0xBEBEFE,
            )
        )
        
        # get a list of people who have submitted the return.
        try:
            feedback_data = pickle.load(open(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/database/feedback.pickle", 'rb'))
        except (OSError, IOError) as e:
            feedback_data = set()
            pickle.dump(feedback_data, open(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/database/feedback.pickle", 'wb'))

        feedback_data.add(interaction.user.id)
        isNewUser = interaction.user.id in feedback_data
        
        pickle.dump(feedback_data, open(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/database/feedback.pickle", 'wb'))
        
        channel = interaction.client.get_channel(1391611662523564152)
        await channel.send(f"__**A user has submitted feedback to the guild!**__")
        #await channel.send(f"User's first submission? {isNewUser}")
        if feedback_form.answer1:
            await channel.send(f"Things we are doing well:\n```\n{feedback_form.answer1}\n```")
        
        if feedback_form.answer2:
            await channel.send(f"Things we should improve:\n```\n{feedback_form.answer2}\n```")
            
        if feedback_form.answer3:
            await channel.send(f"Improving engagement and activity:\n```\n{feedback_form.answer3}\n```")
        
        if feedback_form.answer4:
            await channel.send(f"Website and nazbot ideas:\n```\n{feedback_form.answer4}\n```")
        
        if feedback_form.answer5:
            await channel.send(f"Return feedback and suggestions:\n```\n{feedback_form.answer5}\n```")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Return(bot))
