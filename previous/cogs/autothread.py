from os import environ as env
from nextcord.ext import commands
from nextcord import Message

AUTO_THREAD_CHANNEL_ID = int(env["AUTO_THREAD_CHANNEL_ID"])


class AutoThread(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if message.channel.id == AUTO_THREAD_CHANNEL_ID:
            await message.create_thread(name="Discussion")


def setup(bot: commands.Bot):
    bot.add_cog(AutoThread(bot))
