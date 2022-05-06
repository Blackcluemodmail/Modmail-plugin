import os
import random
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

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command
