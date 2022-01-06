from typing import Tuple
import re

from nextcord import Message
from nextcord.ext.commands import Cog
from nextcord.ext.commands.bot import Bot
from nextcord.mentions import AllowedMentions

codeblock_regex = re.compile(r"`{3}(\w*) *\n(.*)\n`{3}", flags=re.DOTALL)
discord_to_workbin = {
    "py": "python",
    "js": "javascript",
    "text/plain": "text",
    "text/markdown": "markdown",
    "text/x-python": "python",
    "application/json": "json",
    "application/javascript": "javascript",
}
other_paste_services = [
    "pastebin.com",
]
supported_content_types: Tuple[str, ...] = (
    "text/plain",
    "text/markdown",
    "text/x-python",
    "application/json",
    "application/javascript",
)

class AutoPaste(Cog):
    def __init__(self, bot) -> None:
        self.bot: Bot = bot
    
    async def do_upload(self, content: str, language: str) -> str:
        res = await self.bot.session.post("https://paste.nextcord.dev/api/new", data=str(content))  # type: ignore
        paste_id = (await res.json())["key"]

        language = discord_to_workbin.get(language, language)
        return f"https://paste.nextcord.dev/?id={paste_id}&language={language}"

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if "pre-ignore" in message.content:
            return
        if message.content.startswith("!"):
            return

        if message.attachments and message.attachments[0].content_type:
            first_attachment = message.attachments[0]
            assert first_attachment.content_type is not None
            if first_attachment.content_type.startswith(supported_content_types):
                read_text_file = await first_attachment.read()
                if not bool(read_text_file.decode('utf-8')):
                    # file is empty
                    return

                file_content = str(read_text_file.decode('utf-8'))
                language = first_attachment.content_type.replace("; charset=utf-8", "")
                url = await self.do_upload(file_content, language)
                await message.reply(f"Please avoid files for code. Posted to {url}", allowed_mentions=AllowedMentions.none())
                return 

        regex_result = codeblock_regex.search(message.content)
        if regex_result is None:
            for paste_service in other_paste_services:
                if paste_service in message.content:
                    return await message.reply("Please avoid other paste services than https://paste.nextcord.dev.")
            return

        language = regex_result.group(1) or "python"
        code = regex_result.group(2)

        url = await self.do_upload(code, language)
        await message.reply(f"Please avoid codeblocks for code. Posted to -> {url}", allowed_mentions=AllowedMentions.none())

def setup(bot):
    bot.add_cog(AutoPaste(bot))





