import discord
import typing
from discord.ext import commands

bot = commands.Bot('.')

from discord.ext.commands import has_permissions, MissingPermissions
from core import checks
from core.utils import match_user_id
import traceback
import sys
import re
import asyncio

class AutoTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cogs.listener()
    async def on_message(message):
        if message.content.startswith("helo"):
            await ctx.send("hey") 

def setup(bot):
    bot.add_cog(AutoTrigger(bot))
