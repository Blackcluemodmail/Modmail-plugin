import discord

client = discord.Client()

class Autotrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @client.event
    async def on_message(message):
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

def setup(bot):
    bot.add_cog(Autotrigger(bot))
