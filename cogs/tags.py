import aiohttp

from nextcord.ext import commands

class Tags(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def tag(self, ctx, *, name: str):
        """Grabs the Markdown file for a tag."""
        branch_name = "master" # TODO: Dynamically grab current branch name via git
        markdown_link = f"https://raw.githubusercontent.com/nextcord/previous/{branch_name}/assets/{name}.md"

        async with self.bot.session.get(markdown_link) as resp:
            # Exists
            if resp.status == 200:
                return await ctx.send(markdown_link)
            # Not Found
            elif resp.status == 404:
                return await ctx.send("Tag with that name does not exist.")
            # Some other error
            else:
                return await ctx.send(f"Unable to grab a tag with that name. Got HTTP code {resp.status}.")