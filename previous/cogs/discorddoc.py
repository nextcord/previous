from __future__ import annotations

from typing import TYPE_CHECKING, Any

import nextcord
from algoliasearch.search_client import SearchClient
from nextcord.ext import commands
from nextcord.ext.commands import Context

if TYPE_CHECKING:
    from previous.__main__ import Previous


class DiscordHelp(commands.Cog):
    def __init__(self, bot: Previous):
        self.bot = bot
        ## Fill out from trying a search on the ddevs portal
        app_id = "BH4D9OD16A"
        api_key = "f37d91bd900bbb124c8210cca9efcc01"
        self.search_client = SearchClient.create(app_id, api_key)
        self.index = self.search_client.init_index("discord")

    @commands.command(help="Search the Discord API Docs")
    async def ddoc(self, ctx: Context, *, search_term: str):
        results: dict[str, Any] = await self.index.search_async(search_term)  # type: ignore
        description = ""
        hits: list[str] = []
        for hit in results["hits"]:
            title = self.get_level_str(hit["hierarchy"])

            if title in hits:
                continue

            hits.append(title)
            url = hit["url"].replace(
                "https://discord.com/developers/docs", "https://discord.dev"
            )
            description += f"[{title}]({url})\n"

            if len(hits) == 10:
                break

        embed = nextcord.Embed(
            title="Your help has arrived!",
            description=description,
            color=nextcord.Color.random(),
        )
        await ctx.send(embed=embed)

    def get_level_str(self, levels: dict[str, str]) -> str:
        return next((x for x in levels.values() if x is not None), "")


def setup(bot: Previous):
    bot.add_cog(DiscordHelp(bot))
