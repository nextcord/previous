import nextcord
from algoliasearch.search_client import SearchClient
from nextcord.ext import commands


class DiscordHelp(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        ## Fill out from trying a search on the ddevs portal
        app_id = "BH4D9OD16A"
        api_key = "f37d91bd900bbb124c8210cca9efcc01"
        self.search_client = SearchClient.create(app_id, api_key)
        self.index = self.search_client.init_index("discord")

    @commands.command(help="discord api docs")
    async def ddoc(self, ctx, *, search_term):
        results = await self.index.search_async(search_term)
        description = ""
        hits = []
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

    def get_level_str(self, levels):
        last = ""
        for level in levels.values():
            if level is not None:
                last = level
        return last


def setup(bot):
    bot.add_cog(DiscordHelp(bot))
