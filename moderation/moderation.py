import asyncio
import discord
import typing
from discord.ext import commands
from core import checks
from core.models import PermissionLevel
from core.utils import match_user_id
from types import SimpleNamespace
import traceback
import sys
import re

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time

class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

class SlowMode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

class Moderation(commands.Cog):
    """
    Commands to moderate your server.*
    NOTE: You will need the moderator permission
    level in order to run any of these commands.*_ _
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.api.get_plugin_partition(self)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Sets up mute role permissions for the channel."""
        muterole = await self.db.find_one({"_id": "muterole"})
        if muterole == None:
            return

        if not str(channel.guild.id) in muterole:
            return

        role = channel.guild.get_role(muterole[str(channel.guild.id)])
        if role == None:
            return
        await channel.set_permissions(role, send_messages=False)

    @commands.command(usage="<channel>")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def setlog(self, ctx, channel: discord.TextChannel = None):
        """Sets up a log channel."""
        if channel == None:
            return await ctx.send_help(ctx.command)

        try:
            await channel.send(
                embed=discord.Embed(
                    description=(
                        "This channel has been set up to log actions.\n"
                        "This means that I will send bans/warns/kicks here."
                    ),
                    color=self.bot.main_color,
                )
            )
        except discord.errors.Forbidden:
            await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to write in that channel.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions.")
            )
        else:
            await self.db.find_one_and_update(
                {"_id": "logging"},
                {"$set": {str(ctx.guild.id): channel.id}},
                upsert=True,
            )
            await ctx.send(
                embed=discord.Embed(
                    title="Success",
                    description=f"{channel.mention} has been set up as log channel.",
                    color=self.bot.main_color,
                )
            )

    @commands.command(usage="<role>")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def muterole(self, ctx, role: discord.Role = None):
        """Sets up the muted role."""
        if role is None:
            if (await self.db.find_one({"_id": "muterole"})) is not None:
                if (
                    ctx.guild.get_role(
                        (await self.db.find_one({"_id": "muterole"}))[str(ctx.guild.id)]
                    )
                    != None
                ):
                    return await ctx.send(
                        embed=discord.Embed(
                            title="Error",
                            description="Muted role is already set up.",
                            color=discord.Color.red(),
                        ).set_footer(
                            text="If you want to change role, just mention it."
                        )
                    )
            role = await ctx.guild.create_role(name="Muted")

        await self.db.find_one_and_update(
            {"_id": "muterole"}, {"$set": {str(ctx.guild.id): role.id}}, upsert=True
        )

        await ctx.send(
            embed=discord.Embed(
                title="Success",
                description=f"The muted role has been set to {role.mention}.",
                color=self.bot.main_color,
            )
        )

    @commands.command(usage="<member> [reason]")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def warn(self, ctx, member: discord.Member = None, *, reason=None):
        """
        Warns the specified member.
        """
        if member == None:
            return await ctx.send_help(ctx.command)

        if reason != None:
            if not reason.endswith("."):
                reason = reason + "."

        case = await self.get_case()

        msg = f"You have been warned in **{ctx.guild.name}**" + (
            f" for: `{reason}`" if reason else "."
        )

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Warn",
                description=f"**Offender:** {member} \n**Responsible moderator:** {ctx.author.mention}"
                + (f" \n**Reason:** {reason}" if reason else "\n**Reason:** No reason given"),
                color=discord.Color.from_rgb(255,69,0),
            ).set_footer(text=f"This is the {case} case."),
        )

        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Logged",
                    description=f"Warning has been logged for {member}. I couldn't warn them, they disabled DMs."
                + (f" \n**Reason:** {reason}" if reason else "\n**Reason:** No reason given"),
                    color=discord.Color.green(),
                ).set_footer(text=f"This is the {case} case."), delete_after=10
            )

        await ctx.message.delete() 
        await ctx.send(
            embed=discord.Embed(
                title="Warn",
                description=f"{member} has been warned."
                + (f" \n**Reason:** {reason}" if reason else "\n**Reason:** No reason given"),
                color=discord.Color.green(),
            ).set_footer(text=f"This is the {case} case."), delete_after=10
        )

    @commands.command(usage="<member> [reason]")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
        """Kicks the specified member."""
        if member == None:
            return await ctx.send_help(ctx.command)

        if reason != None:
            if not reason.endswith("."):
                reason = reason + "."

        msg = f"You have been kicked from {ctx.guild.name}" + (
            f" for: {reason}" if reason else "."
        )

        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass

        try:
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to kick them.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions.")
            )

        case = await self.get_case()

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Kick",
                description=f"{member} has been kicked by {ctx.author.mention}"
                + (f" for: {reason}" if reason else "."),
                color=self.bot.main_color,
            ).set_footer(text=f"This is the {case} case."),
        )

        await ctx.send(
            embed=discord.Embed(
                title="Success",
                description=f"{member} has been kicked.",
                color=self.bot.main_color,
            ).set_footer(text=f"This is the {case} case.")
        )

    @commands.command(usage="<member> [reason]")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        """Bans the specified member."""
        if member == None:
            return await ctx.send_help(ctx.command)

        if reason != None:
            if not reason.endswith("."):
                reason = reason + "."

        msg = f"You have been banned from {ctx.guild.name}" + (
            f" for: {reason}" if reason else "."
        )

        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Logged",
                    description=f"User {member} has been banned. I couldn't DM them, they disabled DMs."
                + (f" \n**Reason:** {reason}" if reason else "\n**Reason:** No reason given"),
                    color=discord.Color.green(),
                ).set_footer(text=f"This is the {case} case."), delete_after=10
            )

        try:
            await member.ban(reason=reason, delete_message_days=0)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to ban them.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions.")
            )

        case = await self.get_case()

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Ban",
                description=f"{member} has been banned by {ctx.author.mention}"
                + (f" for: {reason}" if reason else "."),
                color=self.bot.main_color,
            ).set_footer(text=f"This is the {case} case."),
        )

        await ctx.send(
            embed=discord.Embed(
                title="Success",
                description=f"{member} has been banned.",
                color=self.bot.main_color,
            ).set_footer(text=f"This is the {case} case.")
        )

    @commands.command(usage="<member> [reason]")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def unban(self, ctx, user: discord.User = None, *, reason=None):
        """Unbans the specified member."""
        if user == None:
            return await ctx.send_help(ctx.command)
        guild = ctx.guild

        if reason != None:
            if not reason.endswith("."):
                reason = reason + "." 

        try:
            await guild.unban(user=user, reason=reason)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to unban them.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions.")
            )

        case = await self.get_case()

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Unban",
                description=f"{user} has been unbanned by {ctx.author.mention}"
                + (f" for: {reason}" if reason else "."),
                color=self.bot.main_color,
            ).set_footer(text=f"This is the {case} case."),
        )

        await ctx.send(
            embed=discord.Embed(
                title="Success",
                description=f"{user} has been unbanned.",
                color=self.bot.main_color,
            ).set_footer(text=f"This is the {case} case.")
        )
 
    @commands.command(usage="<member> <duration> [reason]")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def mute(self, ctx, member: discord.Member = None, time:TimeConverter = None, *, reason=None):
        """Mutes the specified member, format should be in 1d, 10m, 10s."""
        if member == None:
            return await ctx.send_help(ctx.command)
        role = await self.db.find_one({"_id": "muterole"})
        no_role = False
        if role == None:
            no_role = True
        elif str(ctx.guild.id) in role:
            role = ctx.guild.get_role(role[str(ctx.guild.id)])
            if role == None:
                no_role = True

        if reason != None:
            if not reason.endswith("."):
                reason = reason

        if no_role:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description=(
                        "You must set up a muted role first.\n"
                        f"To set one, run `{ctx.prefix}muterole (@role)`."
                    ),
                    color=discord.Color.red(),
                )
            )

        msg = f"You have been muted from **{ctx.guild.name}** for **{time}seconds**" + (
            f" due to: {reason}" if reason else "."
        )

        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass

        try:
            await member.add_roles(role, reason=reason)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to mute them.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions."), delete_after=30
            )

        case = await self.get_case()

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Mute case",
                description=f"**Offender:** {member} \n**Duration:** {time}seconds \n**Responsible moderator:** {ctx.author.mention} "
                + (f" \n**Reason:** {reason}" if reason else "\n**Reason:** No reason given."),
                color=discord.Color.from_rgb(255,69,0),
            ).set_footer(text=f"This is the {case} case."),
        )
  
        await ctx.message.delete()
        await ctx.send(
            embed=discord.Embed(
                title="Success",
                description=f"{member} has been muted for {time}seconds.",
                color=discord.Color.blue(),
            ).set_footer(text=f"This is the {case} case."), delete_after=10
        )
 
        msg = f"You have been unmuted from {ctx.guild.name} after {time}seconds" + (
            f" with mute cause: {reason}" if reason else "."
        )

        if time:
            await asyncio.sleep(time)
            await member.remove_roles(role)
            await member.send(msg)
            print(6)

        case = await self.get_case()

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Unmute",
                description=f"**Offender:** {member} \n**Responsible moderator:** {ctx.author.mention} "
                + (f" \n**Reason:** Automatic unmute from mute made {time}seconds ago"),
                color=discord.Color.green(),
            ).set_footer(text=f"This is the {case} case."),
        )

    @commands.command(usage="<member> [reason]")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def unmute(self, ctx, member: discord.Member = None, *, reason=None):
        """Unmutes the specified member."""
        if member == None:
            return await ctx.send_help(ctx.command)
        role = await self.db.find_one({"_id": "muterole"})
        no_role = False
        if role == None:
            no_role = True
        elif str(ctx.guild.id) in role:
            role = ctx.guild.get_role(role[str(ctx.guild.id)])
            if role == None:
                no_role = True

        if reason != None:
            if not reason.endswith("."):
                reason = reason + "."

        if no_role:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description=(
                        "You don't have a muted role set up.\n"
                        f"You will have to unmute them manually."
                    ),
                    color=discord.Color.red(),
                )
            )

        msg = f"You have been unmuted from **{ctx.guild.name}**" + (
            f"\n**Reason**: *{reason}*" if reason else "*No reason was given"
        )

        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass

        try:
            await member.remove_roles(role, reason=reason)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to unmute them.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions."), delete_after=10
            )

        case = await self.get_case()

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Unmute",
                description=f"**Offender:** {member} \n**Responsible Moderator:** {ctx.author.mention}"
                + (f" \n**Reason:** {reason}" if reason else "\n**Reason:** No reason given"),
                color=discord.Color.green(),
            ).set_footer(text=f"This is the {case} case."),
        )

        await ctx.send(
            embed=discord.Embed(
                title="Success",
                description=f"{member} has been unmuted.",
                color=discord.Color.green(),
            ).set_footer(text=f"This is the {case} case."), delete_after=10
        )            

    @commands.command(usage="<member> [nickname]")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def nick(self, ctx, member: discord.Member = None, *, nick):
        """Change the nickname of specified user."""
        if member == None:
            return await ctx.send_help(ctx.command)
        try:
            await ctx.message.delete()
            await member.edit(nick=nick)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to change their nickname.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions."), delete_after=30
            )

        case = await self.get_case()

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Nickname Changed",
                description=f"**Offender:** {member} \n**New Nickname:** {nick} \n**Responsible moderator:** {ctx.author.mention}.",
                color=discord.Color.green(),
            ).set_footer(text=f"This is the {case} case."),
        )

        await ctx.send(
            embed=discord.Embed(
                title="**Success**",
                description=f"Successfully changed {member.mention}'s nickname.\n**New Nickname:** {nick}",
                color=discord.Color.green(),
            ).set_footer(text=f"This is the {case} case."), delete_after=30
        )  

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def slowmode(self, ctx, time, channel: discord.TextChannel = None):
        """Set a slowmode to a channel
        It is not possible to set a slowmode longer than 6 hours
        """
        if not channel:
            channel = discord.TextChannel = None

        units = {
            "d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1
        }
        seconds = 0
        match = re.findall("([0-9]+[smhd])", time)
        if not match:
            embed = discord.Embed(description="⚠ I dont understand your time format!",color = 0xff0000)
            return await ctx.send(embed=embed)
        for item in match:
            seconds += int(item[:-1]) * units[item[-1]]
        if seconds > 21600:
            embed = discord.Embed(description="⚠ You can't slowmode a channel for longer than 6 hours!", color=0xff0000)
            return await ctx.send(embed=embed)
        try:
            await channel.edit(slowmode_delay=seconds)
        except discord.errors.Forbidden:
            embed = discord.Embed(description="⚠ I don't have permission to do this!", color=0xff0000, delete_after = 30)
            return await ctx.send(embed=embed)
        embed=discord.Embed(description=f"{ctx.author.mention} set a slowmode delay of `{time}` in {channel.mention}", color=0x06c9ff, delete_after=30)
        embed.set_author(name="Slow Mode")
        await ctx.send(embed=embed)

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def slowmode_off(self, ctx, channel: discord.TextChannel = None):
        """Turn off the slowmode in a channel"""
        if not channel:
            channel = ctx.channel
        seconds_off = 0
        await channel.edit(slowmode_delay=seconds_off)
        embed=discord.Embed(description=f"{ctx.author.mention} turned off the slowmode in {channel.mention}", color=0x06c9ff)
        embed.set_author(name="Slow Mode")
        await ctx.send(embed=embed)          
          
    @commands.command(usage="<amount>")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def purge(self, ctx, amount: int = 1):
        """Purge the specified amount of messages."""
        max = 2000
        if amount > max:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"You can only purge up to 2000 messages.",
                    color=discord.Color.red(),
                ).set_footer(text=f"Use {ctx.prefix}nuke to purge the entire chat.")
            )

        try:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to purge messages.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions.")
            )

        case = await self.get_case()
        messages = "messages" if amount > 1 else "message"
        have = "have" if amount > 1 else "has"

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Purge",
                description=f"{amount} {messages} {have} been purged by {ctx.author.mention}.",
                color=self.bot.main_color,
            ).set_footer(text=f"This is the {case} case."),
       )

    async def get_case(self):
        """Gives the case number."""
        num = await self.db.find_one({"_id": "cases"})
        if num == None:
            num = 0
        elif "amount" in num:
            num = num["amount"]
            num = int(num)
        else:
            num = 0
        num += 1
        await self.db.find_one_and_update(
            {"_id": "cases"}, {"$set": {"amount": num}}, upsert=True
        )
        suffix = ["th", "st", "nd", "rd", "th"][min(num % 10, 4)]
        if 11 <= (num % 100) <= 13:
            suffix = "th"
        return f"{num}{suffix}"

    async def log(self, guild: discord.Guild, embed: discord.Embed):
        """Sends logs to the log channel."""
        channel = await self.db.find_one({"_id": "logging"})
        if channel == None:
            return
        if not str(guild.id) in channel:
            return
        channel = self.bot.get_channel(channel[str(guild.id)])
        if channel == None:
            return
        return await channel.send(embed=embed)               

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def role(self, ctx, member: discord.Member=None, role: discord.Role):
        """Assign a role to a member."""
        if member is None:
            member = ctx.guild.get_member(match_user_id(ctx.channel.topic))
            if member is None:
                raise commands.MissingRequiredArgument(SimpleNamespace(name="role"))
       
        await member.add_roles(role)
        except discord.errors.Forbidden:
            return await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="I don't have enough permissions to change their roles.",
                    color=discord.Color.red(),
                ).set_footer(text="Please fix the permissions."), delete_after=10
            )

        case = await self.get_case()

        await self.log(
            guild=ctx.guild,
            embed=discord.Embed(
                title="Role Added",
                description=f"**Offender:** {member} \n**New Role:** {role} \n**Responsible moderator:** {ctx.author.mention}.",
                color=discord.Color.green(),
            ).set_footer(text=f"This is the {case} case."),
        )

        await ctx.send(
            embed=discord.Embed(
                title="**Success**",
                description=f"Successfully changed {member.mention}'s roles. \n**New Role added:** {role}",
                color=discord.Color.green(),
            ).set_footer(text=f"This is the {case} case."), delete_after=60
       

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def unrole(self, ctx, role: discord.Role, member: discord.Member=None):
        """Remove a role from a member."""
        if member is None:
            member = ctx.guild.get_member(match_user_id(ctx.channel.topic))
            if member is None:
                raise commands.MissingRequiredArgument(SimpleNamespace(name="unrole"))
            
        await member.remove_roles(role)
        await ctx.send(f"Successfully removed the role from {member.name}!")

    @commands.command(aliases=["makerole"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def createrole(self, ctx, name: str, color: str):
        """create a role."""
        color = "#" + color.strip("#")
        
        valid = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color)
        if not valid:
            embed = discord.Embed(title="Failure", color=self.bot.main_color,
                description="Please enter a **valid [hex code](https://htmlcolorcodes.com/color-picker)**")
            return await ctx.send(embed=embed)

        await ctx.guild.create_role(name=name, color=discord.Color(int(color.replace("#", "0x"), 0)))
        await ctx.send("Successfully created the role!")

def setup(bot):
    bot.add_cog(Moderation(bot))
