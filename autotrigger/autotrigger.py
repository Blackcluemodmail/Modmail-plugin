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
        if '667378631336525824' == message.content:
            await message.channel.send("`CloudyOrk is AFK: kuchzada hi mobile chala liya aaj, purso ata hu ab")
        if 'CloudyOrk' == message.content():
            await message.channel.send("`CloudyOrk is AFK: kuchzada hi mobile chala liya aaj, purso ata hu ab")


def setup(bot):
    bot.add_cog(AutoTrigger(bot))
