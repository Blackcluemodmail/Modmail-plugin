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

class Autotrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hi(ctx):
        await ctx.send("Hello, this is a DM!")

    @commands.command() 
    async def on_message(message):
        if message.content == "hi":
            await ctx.send("Hello, this is a DM!")

def setup(bot):
    bot.add_cog(Autotrigger(bot))
