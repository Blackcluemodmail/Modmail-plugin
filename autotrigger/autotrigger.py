import discord

bot = commands.Bot('.')

import typing
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from core import checks
from core.utils import match_user_id
import traceback
import sys
import re
import asyncio

class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.event
    async def on_message(msg):
        print("in on_message #1")
        await bot.process_commands(msg)  # so `Command` instances will still get called


    @bot.listen()
    async def on_message(msg):
        print("in on_message #2")

def setup(bot):
    bot.add_cog(MuteCog(bot))
