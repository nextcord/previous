from nextcord.ext import commands

AUTO_THREAD_CHANNEL = 937840096021979236

class AutoThread(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == AUTO_THREAD_CHANNEL:
            await message.create_thread("Discussion")


def setup(bot):
    bot.add_cog(AutoThread(bot))
