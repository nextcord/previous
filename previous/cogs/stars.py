from __future__ import annotations

import aiohttp
from os import getenv
from nextcord.ext import commands
from nextcord.ext.tasks import loop

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from previous.__main__ import Previous


class GitHubStars(commands.Cog):
    """Run a task loop to update a channel with the current stars for nextcord/nextcord and nextcord/nextcord-v3"""

    STARS_CHANNEL_ID = int(getenv("STARS_CHANNEL_ID", 0))

    def __init__(self, bot: Previous):
        self.__bot = bot
        self.update_stars.start()

    async def get_stars(self, repo: str) -> int:
        """Get number of GitHub stars for a given repo in the form 'owner/repository'"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.github.com/repos/{repo}") as resp:
                data = await resp.json()
                return int(data["stargazers_count"])

    @loop(minutes=30)
    async def update_stars(self):
        """Loop to check and update stars"""
        nextcord_stars = await self.get_stars("nextcord/nextcord")
        nextcord_v3_stars = await self.get_stars("nextcord/nextcord-v3")
        channel_name = f"v2 {nextcord_stars}🌟| v3 {nextcord_v3_stars}🌟"

        # update channel name if it has changed
        if self.__channel.name != channel_name:  # type: ignore
            await self.__channel.edit(name=channel_name)  # type: ignore

    @update_stars.before_loop
    async def before_update_stars(self):
        """Before the loop starts, get the channel"""
        await self.__bot.wait_until_ready()
        c = self.__bot.get_channel(self.STARS_CHANNEL_ID)
        assert c is not None
        self.__channel = c

    def cog_unload(self):
        self.update_stars.cancel()


def setup(bot: Previous):
    bot.add_cog(GitHubStars(bot))
