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
    async def on_message(self, message):
        if "how to join smp" in message.content:
            await message.channel.send('{ctx.author.mention} check <#944498884351246336>', delete_after=5)
        if message.content.startswith('!goodbye') :
            await message.channel.send('Goodbye!')

def setup(bot):
    bot.add_cog(AutoTrigger(bot))
