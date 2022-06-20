from os import environ as env
from typing import TYPE_CHECKING

from nextcord import Message
from nextcord.ext import commands

if TYPE_CHECKING:
    from previous.__main__ import Previous

AUTO_THREAD_CHANNEL_ID = int(env["AUTO_THREAD_CHANNEL_ID"])


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
