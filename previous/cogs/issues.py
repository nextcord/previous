from __future__ import annotations

from typing import TYPE_CHECKING
from re import compile as re_compile

from nextcord.ext.commands import Cog, Context, command

if TYPE_CHECKING:
    from nextcord import Message

    from ..__main__ import Previous


class Issues(Cog):
    ISSUE_RE = re_compile(r"##(?P<issue>\d+)")
    DPY_RE = re_compile(r"#!(?P<issue>\d+)")

    def __init__(self, bot: Previous):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        if result := self.ISSUE_RE.search(message.content):
            issue_id = result.group("issue")
            await message.channel.send(
                f"https://github.com/nextcord/nextcord/issues/{issue_id}"
            )
        if result := self.DPY_RE.search(message.content):
            issue_id = result.group("issue")
            await message.channel.send(
                f"https://github.com/rapptz/discord.py/issues/{issue_id}"
            )

    @command()
    async def todo(self, ctx: Context):
        await ctx.send(
            "https://github.com/nextcord/nextcord/projects/1 "
            "and going through all the issues"
        )


def setup(bot: Previous):
    bot.add_cog(Issues(bot))
