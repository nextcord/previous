from typing import List, Optional
import re

from nextcord import Message, Thread
from nextcord.enums import ButtonStyle
from nextcord.errors import HTTPException, NotFound
from nextcord.ext.commands import Cog
from nextcord.ext.commands.bot import Bot
from nextcord.interactions import Interaction
from nextcord.member import Member
from nextcord.mentions import AllowedMentions
from nextcord.ui import button, View

from .help import HELP_CHANNEL_ID

codeblock_regex = re.compile(r"`{3}(\w*) *\n(.*)\n`{3}", flags=re.DOTALL)

discord_to_workbin = {
    "py": "python",
    "js": "javascript"
}
other_paste_services = [
    "pastebin.com",
    "sourceb.in",
    "srcb.in"
]
supported_content_types: List[str] = [
    "text/plain",
    "text/markdown",
    "text/x-python",
    "application/json",
    "application/javascript",
]
content_type_to_lang = {
    "text/plain": "text",
    "text/markdown": "markdown",
    "text/x-python": "python",
    "application/json": "json",
    "application/javascript": "javascript"
}


class DeleteMessage(View):
    def __init__(self, message_author: Member):
        self.message: Optional[Message] = None
        self.message_author = message_author
        super().__init__(timeout=300)  # 300 seconds == 5 minutes

    @button(emoji="❌", style=ButtonStyle.secondary, custom_id="delete_autopaste")
    async def delete_autopaste(self, _, interaction: Interaction) -> None:
        try:
            await interaction.message.delete()  # type: ignore
        except (HTTPException, NotFound):
            pass

        await self.on_timeout()

    async def on_timeout(self) -> None:
        self.stop()
        try:
            await self.message.edit(view=None)  # type: ignore
        except (AttributeError, HTTPException, NotFound):
            pass

    async def interaction_check(self, interaction: Interaction) -> bool:
        if not interaction.user or not interaction.channel or not isinstance(interaction.user, Member):
            await self.on_timeout()
            return False

        if interaction.user.id == self.message_author.id or \
            interaction.channel.permissions_for(interaction.user).manage_messages:  # type: ignore
            return True

        return False


class AutoPaste(Cog):
    def __init__(self, bot) -> None:
        self.bot: Bot = bot
    
    async def do_upload(self, content: str, language: str) -> str:
        res = await self.bot.session.post("https://paste.nextcord.dev/api/new", data=str(content))  # type: ignore
        paste_id = (await res.json())["key"]
        return f"https://paste.nextcord.dev/?id={paste_id}&language={language}"

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if "pre-ignore" in message.content:
            return
        if message.content.startswith("!"):
            return

        delete_view: DeleteMessage = DeleteMessage(message.author)  # type: ignore

        # Files
        if message.attachments:
            first_attachment = message.attachments[0]
            if not first_attachment.content_type:
                return
            
            content_type = first_attachment.content_type.split(";")[0].strip()
            if content_type not in supported_content_types:
                return

            file_bytes = await first_attachment.read()
            if not bool(file_bytes.decode('utf-8')):
                # file is empty
                return

            file_content = str(file_bytes.decode('utf-8'))

            language = content_type_to_lang.get(content_type, "text")
            if isinstance(message.channel, Thread) and message.channel.parent_id == HELP_CHANNEL_ID and content_type == "text/plain":
                language = "python"

            url = await self.do_upload(file_content, language)
            delete_view.message=await message.reply(f"Please avoid files for code. Posted to {url}", allowed_mentions=AllowedMentions.none(), view=delete_view)
            return

        # Codeblocks
        regex_result = codeblock_regex.search(message.content)
        if regex_result is None:
            # Check for bad paste services
            for paste_service in other_paste_services:
                if paste_service in message.content:
                    delete_view.message=await message.reply("Please avoid other paste services than https://paste.nextcord.dev.", view=delete_view)
                    return
            return

        language = regex_result.group(1) or "python"
        language = discord_to_workbin.get(language, language)
        code = regex_result.group(2)

        url = await self.do_upload(code, language)
        delete_view.message=await message.reply(f"Please avoid codeblocks for code. Posted to -> {url}", allowed_mentions=AllowedMentions.none(), view=delete_view)

def setup(bot):
    bot.add_cog(AutoPaste(bot))





