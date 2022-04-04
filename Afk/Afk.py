import asyncio
import discord
import typing
from datetime import datetime
from discord.ext import commands
from core import checks
from core.models import PermissionLevel
from core.utils import match_user_id
from types import SimpleNamespace
import traceback
import sys
import re

    class Moderation(commands.Cog):
    """
    Commands to moderate your server.*
    NOTE: You will need the moderator permission
    level in order to run any of these commands.*_ _
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.api.get_plugin_partition(self)


    @commands.command()
    async def afk(ctx, *, reason=None):

        if reason != None:
            if not reason.endswith("."):
                reason = reason + "."

        current_nick = ctx.author

        try:
            await ctx.author.edit(nick=f"[AFK] {ctx.author.name}")
        except discord.errors.Forbidden:
            return await ctx.send(f"{ctx.author.mention}"
        + (f" I have set your AFK: {reason}" if reason else "AFK"),

        counter = 0
        while counter <= int(mins):
           counter += 1
           await asyncio.sleep(60)

           if counter == int(mins):

               try:
                  await ctx.author.edit(nick=current_nick)
               except discord.errors.Forbidden:
                  return await ctx.send(f"Welcome back {ctx.author.mention}, I have removed your AFK")
            
def setup(bot):
    bot.add_cog(Moderation(bot))
