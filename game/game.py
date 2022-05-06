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

    @commands.command()
    async def game(self, gameW, ctx):
        """ Play a game with bot""" 
    def gameW(comp, you):
        if comp == you:
            return None
   #If computer choose snake then - 
        elif comp == s:
            if you == w:
                return False
            elif you == g:
                return True
   
   #if computer choose water then - 
        elif comp == w:
            if you == s:
                return True
            elif you == g:
                return False

   #if computer choose gun then - 
        elif comp == g:
            if you == s:
                return False
            elif you == w:
                return True

    bot = "Choose one: Snake(s) Water(w) Gun(g)"
    random = random.randint(1,3)
    if random == 1:
        comp = 's'
    elif random == 2:
        comp = 'w'
    elif random == 3:
        comp = 'g' 

    user = input("Choose one: Snake(s) Water(w) Gun(g)")

    await ctx.send(f("Computer chose {comp}\n You chose {you}") 
    game = gameW(bot, user)
    if game == True:
        await ctx.send("You won!") 
    elif game == None:
        await ctx.send("Tie!") 
    else:
        await ctx.send("You lose!") 
    
      
def setup(bot):
    bot.add_cog(Game(bot))
