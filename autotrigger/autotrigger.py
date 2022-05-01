import asyncio
import discord
import typing
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from core import checks
from core.models import PermissionLevel
from core.utils import match_user_id
from types import SimpleNamespace
import traceback
import sys
import re

class AutoTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(message):
        if message.author == client.user:
            return  

        if message.content.startswith('!hi') :
            await message.channel.send('Hi!')
        if message.content.startswith('!goodbye') :
            await message.channel.send('Goodbye!')

def setup(bot):
    bot.add_cog(AutoTrigger(bot))
