import re
import aiohttp
from aiohttp.client import ClientSession
import nextcord
from nextcord.ext.commands import Cog
from nextcord.ext.commands.bot import Bot
from nextcord.mentions import AllowedMentions

codeblock_regex = re.compile(r"`{3}(\w*) *\n(.*)\n`{3}", flags=re.DOTALL)

discord_to_workbin = {
    "py": "python",
    "js": "javascript"
}
other_paste_services = [
    "pastebin.com",
    "mystb.in",
    "hastebin.com",
    "hst.sh"
]

class AutoPaste(Cog):
    def __init__(self, bot) -> None:
        self.bot: Bot = bot
    @Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author == 825470953365700708:
            # Do not delete messages from h3
            return

        regex_result = codeblock_regex.match(message.content)

        if regex_result is None:
            for paste_service in other_paste_services:
                if paste_service in message.content:
                    await message.delete()
                    return await message.channel.send("Please avoid other paste services than https://paste.nextcord.dev.")
            return
        language = regex_result.group(1) or "python"

        language = discord_to_workbin.get(language, language)

        code = regex_result.group(2)
        
        r = await self.bot.session.post("https://paste.nextcord.dev/api/new", data=code)
        res = await r.json()
        paste_id = res["key"]

        await message.channel.send(f"Please avoid codeblocks for code. Posted to -> https://paste.nextcord.dev/?id={paste_id}&language={language}", allowed_mentions=AllowedMentions(everyone=False, roles=[], users=[]))
        await message.delete()

def setup(bot):
    bot.add_cog(AutoPaste(bot))





