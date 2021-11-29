import asyncio
import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel


class Moderation(commands.Cog):
    """
    Commands to moderate your server.*
    NOTE: You will need the moderator permission
    level in order to run any of these commands.*_ _
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.api.get_plugin_partition(self)

    async def cog_command_error(self, ctx, error):
        """Checks errors"""
        error = getattr(error, "original", error)
        if isinstance(error, commands.CheckFailure):
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="You don't have enough permissions to run this command!",
                    color=discord.Color.red(),
                ).set_footer(text="Are you a moderator?")
            )
        raise error

    
    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def afk(ctx, mins):
    current_nick = ctx.author.nick
    await ctx.send(f"{ctx.author.mention} has gone afk for {mins} minutes.")
    await ctx.author.edit(nick=f"{ctx.author.name} [AFK]")

    counter = 0
    while counter <= int(mins):
        counter += 1
        await asyncio.sleep(60)

        if counter == int(mins):
            await ctx.author.edit(nick=current_nick)
            await ctx.send(f"{ctx.author.mention} is no longer AFK")
            break
