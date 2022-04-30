import asyncio
import discord
import typing
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from core import checks
from core.utils import match_user_id
import traceback
import sys
import re

class AutotriggerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @client.event
    async def on_message(message):
        if message.content.startswith('yoo'):
            channel = message.channel
            await channel.send('Say hello!')

 def setup(bot):
    bot.add_cog(AutotriggerCog(bot))