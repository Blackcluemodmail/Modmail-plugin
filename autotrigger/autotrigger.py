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
import asyncio

class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @client.event()
    async def hi(ctx, message):
        await ctx.send("Hello, this is a DM!")

    @client.event() 
    async def on_message(ctx, message):
        if message.content == "hi":
            await ctx.send("Hello, this is a DM!")

def setup(bot):
    bot.add_cog(MuteCog(bot))
