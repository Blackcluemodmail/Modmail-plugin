import discord
import typing
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from core import checks
from core.utils import match_user_id
import traceback
import sys
import re
import asyncio

client = discord.Client()

class Autotrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @client.event
    async def on_message(message):
        if message.content == "hello":
            await message.channel.send('Hello!')

def setup(bot):
    bot.add_cog(Autotrigger(bot))
