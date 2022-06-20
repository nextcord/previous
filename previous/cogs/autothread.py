from os import getenv
from typing import TYPE_CHECKING

from nextcord.ext import commands

if TYPE_CHECKING:
    from nextcord import Message
    from previous.__main__ import Previous


AUTO_THREAD_CHANNEL_ID = getenv("AUTO_THREAD_CHANNEL_ID", 0)


class AutoThread(commands.Cog):
    def __init__(self, bot: Previous):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.channel.id == AUTO_THREAD_CHANNEL_ID:
            await message.create_thread(name="Discussion")


def setup(bot: Previous):
    bot.add_cog(AutoThread(bot))
