from typing import Dict, NamedTuple, Optional

from .utils.split_txtfile import split_txtfile

from nextcord.ext import commands
from nextcord.abc import GuildChannel
from nextcord import (
    Button,
    ButtonStyle,
    ChannelType,
    Colour,
    Embed,
    Forbidden,
    Guild,
    HTTPException,
    Interaction,
    Member,
    MessageType,
    Thread,
    ThreadMember,
    ui
)

HELP_CHANNEL_ID: int = 881965127031722004
HELP_LOGS_CHANNEL_ID: int = 883035085434142781
HELPER_ROLE_ID: int = 882192899519954944
HELP_MOD_ID: int = 896860382226956329
CUSTOM_ID_PREFIX: str = "help:"

closing_message = ("If your question has not been answered or your issue not "
                   "resolved, we suggest taking a look at [Python's Guide to "
                   "Asking Good Questions](https://www.pythondiscord.com/pages/guides/pydis-guides/asking-good-questions/) "
                   "to get more effective help.")


async def get_thread_author(channel: Thread) -> Member:
    history = channel.history(oldest_first = True, limit = 1)
    history_flat = await history.flatten()
    user = history_flat[0].mentions[0]
    return user


async def close_help_thread(method: str, thread_channel, thread_author):
    """Closes a help thread. Is called from either the close button or the
    =close command.
    """
    if not thread_channel.last_message or not thread_channel.last_message_id:
        _last_msg = ((await thread_channel.history(limit = 1)).flatten())[0]
    else:
        _last_msg = thread_channel.get_partial_message(thread_channel.last_message_id)

    thread_jump_url = _last_msg.jump_url

    dm_embed_thumbnail = thread_channel.guild.icon.url
    embed_reply = Embed(title="This thread has now been closed",
                        description=closing_message,
                        colour=Colour.dark_theme())

    await thread_channel.send(embed=embed_reply)  # Send the closing message to the help thread
    await thread_channel.edit(locked = True, archived = True)  # Lock thread
    await thread_channel.guild.get_channel(HELP_LOGS_CHANNEL_ID).send(  # Send log
        content = f"Help thread {thread_channel.name} (created by {thread_author.name}) has been closed."
    )
    # Make some slight changes to the previous thread-closer embed
    # to send to the user via DM.
    embed_reply.title = "Your help thread in the Nextcord server has been closed."
    embed_reply.description += (f"\n\nYou can use [**this link**]({thread_jump_url}) to "
                                "access the archived thread for future reference")
    embed_reply.set_thumbnail(url=dm_embed_thumbnail)
    try:
        await thread_author.send(embed=embed_reply)
    except (HTTPException, Forbidden):
        pass

class HelpButton(ui.Button["HelpView"]):
    def __init__(self, help_type: str, *, style: ButtonStyle, custom_id: str):
        super().__init__(label = f"{help_type} help", style = style, custom_id = f"{CUSTOM_ID_PREFIX}{custom_id}")
        self._help_type = help_type

    async def create_help_thread(self, interaction: Interaction) -> None:
        channel_type = ChannelType.private_thread if interaction.guild.premium_tier >= 2 else ChannelType.public_thread
        thread = await interaction.channel.create_thread(
            name = f"{self._help_type} help ({interaction.user})",
            type = channel_type
        )

        await interaction.guild.get_channel(HELP_LOGS_CHANNEL_ID).send(
            content = f"Help thread for {self._help_type} created by {interaction.user.mention}: {thread.mention}!"
        )
        close_button_view = ThreadCloseView()
        close_button_view._thread_author = interaction.user

        type_to_colour: Dict[str, Colour] = {
            "Nextcord": Colour.red(),
            "Python": Colour.green()
        }

        em = Embed(
            title = f"{self._help_type} Help needed!",
            description = f"Alright now that we are all here to help, what do you need help with?",
            colour = type_to_colour.get(self._help_type, Colour.blurple())
        )
        em.set_footer(text = "You and the helpers can close this thread with the button")

        msg = await thread.send(
            content = f"<@&{HELPER_ROLE_ID}> | {interaction.user.mention}",
            embed = em,
            view = ThreadCloseView()
        )
        await msg.pin(reason = "First message in help thread with the close button.")

    async def callback(self, interaction: Interaction):
        confirm_view = ConfirmView()

        def disable_all_buttons():
            for _item in confirm_view.children:
                _item.disabled = True

        confirm_content = "Are you really sure you want to make a help thread?"
        await interaction.response.send_message(content = confirm_content, ephemeral = True, view = confirm_view)
        await confirm_view.wait()
        if confirm_view.value is False or confirm_view.value is None:
            disable_all_buttons()
            content = "Ok, cancelled." if confirm_view.value is False else f"~~{confirm_content}~~ I guess not..."
            await interaction.edit_original_message(content = content, view = confirm_view)
        else:
            disable_all_buttons()
            await interaction.edit_original_message(content = "Created!", view = confirm_view)
            await self.create_help_thread(interaction)


class HelpView(ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.add_item(HelpButton("Nextcord", style = ButtonStyle.red, custom_id = "nextcord"))
        self.add_item(HelpButton("Python", style = ButtonStyle.green, custom_id = "python"))


class ConfirmButton(ui.Button["ConfirmView"]):
    def __init__(self, label: str, style: ButtonStyle, *, custom_id: str):
        super().__init__(label = label, style = style, custom_id = f"{CUSTOM_ID_PREFIX}{custom_id}")

    async def callback(self, interaction: Interaction):
        self.view.value = True if self.custom_id == f"{CUSTOM_ID_PREFIX}confirm_button" else False
        self.view.stop()


class ConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout = 10.0)
        self.value = None
        self.add_item(ConfirmButton("Yes", ButtonStyle.green, custom_id = "confirm_button"))
        self.add_item(ConfirmButton("No", ButtonStyle.red, custom_id = "decline_button"))


class ThreadCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self._thread_author: Optional[Member] = None

    async def _get_thread_author(self, channel: Thread) -> None:
        self._thread_author = await get_thread_author(channel)

    @ui.button(label = "Close", style = ButtonStyle.red, custom_id = f"{CUSTOM_ID_PREFIX}thread_close")
    async def thread_close_button(self, button: Button, interaction: Interaction):
        if interaction.channel.archived:
            button.disabled = True
            await interaction.message.edit(view = self)
            return

        if not self._thread_author:
            await self._get_thread_author(interaction.channel)  # type: ignore
        
        await close_help_thread("BUTTON", interaction.channel, self._thread_author)
        button.disabled = True
        await interaction.message.edit(view = self)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if not self._thread_author:
            await self._get_thread_author(interaction.channel)  # type: ignore

        # because we aren't assigning the persistent view to a message_id.
        if not isinstance(interaction.channel, Thread) or interaction.channel.parent_id != HELP_CHANNEL_ID:
            return False

        return interaction.user.id == self._thread_author.id or interaction.user.get_role(HELP_MOD_ID)


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.create_views())

    async def create_views(self):
        if getattr(self.bot, "help_view_set", False) is False:
            self.bot.help_view_set = True
            self.bot.add_view(HelpView())
            self.bot.add_view(ThreadCloseView())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == HELP_CHANNEL_ID and message.type is MessageType.thread_created:
            await message.delete(delay = 5)
        if isinstance(message.channel, Thread) and \
                message.channel.parent_id == HELP_CHANNEL_ID and \
                message.type is MessageType.pins_add:
            await message.delete(delay = 10)

    @commands.Cog.listener()
    async def on_thread_member_remove(self, member: ThreadMember):
        thread = member.thread
        if thread.parent_id != HELP_CHANNEL_ID or thread.archived:
            return

        thread_author = await get_thread_author(thread)
        if member.id != thread_author.id:
            return

        await close_help_thread("EVENT", thread, thread_author)

    @commands.command()
    @commands.is_owner()
    async def help_menu(self, ctx):
        for section in split_txtfile("helpguide.txt"):
            await ctx.send(embed=Embed(description=section))
        await ctx.send("**:white_check_mark:  If you've read the guidelines "
                       "above, click a button to create a help thread!**",
                       view = HelpView())

    @commands.command()
    async def close(self, ctx):
        if not isinstance(ctx.channel, Thread) or ctx.channel.parent_id != HELP_CHANNEL_ID:
            return
        thread_author = await get_thread_author(ctx.channel)
        await close_help_thread("COMMAND", ctx.channel, thread_author)

    @commands.command()
    @commands.has_role(HELP_MOD_ID)
    async def topic(self, ctx, *, topic):
        if not ctx.channel.type == ChannelType.private_thread:
            return await ctx.send("This command can only be used in help threads!")
        if ctx.message.channel.parent.id != HELP_CHANNEL_ID:
            return await ctx.send("This command can only be used in help threads!")
        author = await get_thread_author(ctx.channel)
        await ctx.channel.edit(name=f"{topic} ({author})")


def setup(bot):
    bot.add_cog(HelpCog(bot))
