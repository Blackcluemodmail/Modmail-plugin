import asyncio
import discord

client = discord.Client()

import typing
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from core import checks
from core.utils import match_user_id
import traceback
import sys
import re

class Autotrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            await ctx.send('Hello!')

def setup(bot):
    bot.add_cog(Autotrigger(bot))
