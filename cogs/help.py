from asyncio import TimeoutError
from datetime import timedelta
from os import environ as env
from re import match
from typing import Dict, Union

from nextcord import (
    Button,
    ButtonStyle,
    ChannelType,
    ClientUser,
    Colour,
    Embed,
    Forbidden,
    HTTPException,
    Interaction,
    Member,
    Message,
    MessageType,
    Thread,
    ThreadMember,
    ui,
    utils,
)
from nextcord.ext import commands, tasks

from .utils.split_txtfile import split_txtfile

HELP_CHANNEL_ID: int = int(env["HELP_CHANNEL_ID"])
HELP_LOGS_CHANNEL_ID: int = int(env["HELP_LOG_CHANNEL_ID"])
HELPER_ROLE_ID: int = int(env["HELP_NOTIFICATION_ROLE_ID"])
HELP_MOD_ID: int = int(env["HELP_MOD_ROLE_ID"])
NO_HELP_ID: int = int(env["NO_HELP_ROLE_ID"])
GUILD_ID: int = int(env["GUILD_ID"])
CUSTOM_ID_PREFIX: str = "help:"
NAME_TOPIC_REGEX: str = r"^(?P<topic>.*?) \((?P<author>[^)]*[^(]*)\)$"
WAIT_FOR_TIMEOUT: int = 1800  # 30 minutes
NO_HELP_MESSAGE: str = "You are banned from creating help threads."

closing_message = (
    "If your question has not been answered or your issue not "
    "resolved, we suggest taking a look at [Python Discord's Guide to "
    "Asking Good Questions](https://www.pythondiscord.com/pages/guides/pydis-guides/asking-good-questions/) "
    "to get more effective help."
)


async def get_thread_author(channel: Thread) -> Member:
    history = channel.history(oldest_first=True, limit=1)
    history_flat = await history.flatten()
    user = history_flat[0].mentions[0]
    return user


async def close_help_thread(
    method: str,
    thread_channel: Thread,
    thread_author: Member,
    closed_by: Union[Member, ClientUser],
):
    """Closes a help thread. Is called from either the close button or the
    =close command.
    """

    # no need to do any of this if the thread is already closed.
    if thread_channel.locked or thread_channel.archived:
        return

    if not thread_channel.last_message or not thread_channel.last_message_id:
        _last_msg = (await thread_channel.history(limit=1).flatten())[0]
    else:
        _last_msg = thread_channel.get_partial_message(thread_channel.last_message_id)

    thread_jump_url = _last_msg.jump_url
    topic = match(NAME_TOPIC_REGEX, thread_channel.name).group("topic")  # type: ignore

    embed_reply = Embed(
        title="This thread has now been closed",
        description=closing_message,
        colour=Colour.dark_theme(),
    )

    await thread_channel.send(
        embed=embed_reply
    )  # Send the closing message to the help thread
    await thread_channel.edit(locked=True, archived=True)  # Lock thread
    # Send log
    embed_log = Embed(
        title=":x: Closed help thread",
        url=thread_channel.jump_url,
        description=(
            f"{thread_channel.mention}\n\nHelp thread created by {thread_author.mention} has been closed by {closed_by.mention} "
            f"using **{method}**.\n\n"
            f"Thread author: `{thread_author} ({thread_author.id})`\n"
            f"Closed by: `{closed_by} ({closed_by.id})`"
        ),
        colour=0xDD2E44,  # Red
    )
    await thread_channel.guild.get_channel(HELP_LOGS_CHANNEL_ID).send(embed=embed_log)
    # Make some slight changes to the previous thread-closer embed
    # to send to the user via DM.
    embed_reply.title = "Your help thread in the Nextcord server has been closed."
    embed_reply.description += f"\n\nTopic: **{topic}**\n\nYou can use [**this link**]({thread_jump_url}) to access the archived thread for future reference."
    if thread_channel.guild.icon:
        embed_reply.set_thumbnail(url=thread_channel.guild.icon.url)
    try:
        await thread_author.send(embed=embed_reply)
    except (HTTPException, Forbidden):
        pass


class HelpButton(ui.Button["HelpView"]):
    def __init__(self, help_type: str, *, style: ButtonStyle, custom_id: str):
        super().__init__(
            label=f"{help_type} help",
            style=style,
            custom_id=f"{CUSTOM_ID_PREFIX}{custom_id}",
        )
        self._help_type: str = help_type

    async def create_help_thread(self, interaction: Interaction) -> Thread:
        thread = await interaction.channel.create_thread(
            name=f"{self._help_type} help ({interaction.user})",
            type=ChannelType.public_thread,
        )

        # Send log
        embed_log = Embed(
            title=":white_check_mark: Help thread created",
            url=thread.jump_url,
            description=(
                f"{thread.mention}\n\n"
                f"Help thread for **{self._help_type}** created by {interaction.user.mention}!\n\n"
                f"Created by: `{interaction.user} ({interaction.user.id})`"
            ),
            colour=0x77B255,  # Green
        )
        await interaction.guild.get_channel(HELP_LOGS_CHANNEL_ID).send(embed=embed_log)

        type_to_colour: Dict[str, Colour] = {
            "Nextcord": Colour.blurple(),
            "Python": Colour.green(),
        }

        em = Embed(
            title=f"{self._help_type} Help thread",
            colour=type_to_colour.get(self._help_type, Colour.blurple()),
            description=(
                "Please explain your issue in detail, helpers will respond as soon as possible."
                "\n\n**Please include the following in your initial message:**"
                "\n- Relevant code\n- Error (if present)\n- Expected behavior"
                f"\n\nRefer for more to our help guildlines in <#{HELP_CHANNEL_ID}>"
            ),
        )
        em.set_footer(
            text="You can close this thread with the button or =close command."
        )

        close_button_view = ThreadCloseView()

        msg = await thread.send(
            content=interaction.user.mention, embed=em, view=close_button_view
        )
        # it's a persistent view, we only need the button.
        close_button_view.stop()
        await msg.pin(reason="First message in help thread with the close button.")
        return thread

    async def __launch_wait_for_message(
        self, thread: Thread, interaction: Interaction
    ) -> None:
        assert self.view is not None

        def is_allowed(message: Message) -> bool:
            return message.author.id == interaction.user.id and message.channel.id == thread.id and not thread.archived  # type: ignore

        try:
            await self.view.bot.wait_for(
                "message", timeout=WAIT_FOR_TIMEOUT, check=is_allowed
            )
        except TimeoutError:
            await close_help_thread(
                "TIMEOUT [launch_wait_for_message]",
                thread,
                interaction.user,
                self.view.bot.user,
            )
            return
        else:
            await thread.send(f"<@&{HELPER_ROLE_ID}>", delete_after=5)
            return

    async def callback(self, interaction: Interaction):
        confirm_view = ConfirmView()

        def disable_all_buttons():
            for _item in confirm_view.children:
                _item.disabled = True

        confirm_content = (
            f"Are you really sure you want to make a {self._help_type} help thread?"
        )
        await interaction.send(
            content=confirm_content, ephemeral=True, view=confirm_view
        )
        await confirm_view.wait()
        if confirm_view.value is False or confirm_view.value is None:
            disable_all_buttons()
            content = (
                "Ok, cancelled."
                if confirm_view.value is False
                else f"~~{confirm_content}~~ I guess not..."
            )
            await interaction.edit_original_message(content=content, view=confirm_view)
        else:
            disable_all_buttons()
            await interaction.edit_original_message(
                content="Created!", view=confirm_view
            )
            created_thread = await self.create_help_thread(interaction)
            await self.__launch_wait_for_message(created_thread, interaction)


class HelpView(ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot: commands.Bot = bot

        self.add_item(
            HelpButton("Nextcord", style=ButtonStyle.blurple, custom_id="nextcord")
        )
        self.add_item(HelpButton("Python", style=ButtonStyle.green, custom_id="python"))
    
    async def interaction_check(self, interaction: Interaction):
        if interaction.user.get_role(NO_HELP_ID) is not None:
            await interaction.send(NO_HELP_MESSAGE, ephemeral=True)
            return False

        return True


class ConfirmButton(ui.Button["ConfirmView"]):
    def __init__(self, label: str, style: ButtonStyle, *, custom_id: str):
        super().__init__(
            label=label, style=style, custom_id=f"{CUSTOM_ID_PREFIX}{custom_id}"
        )

    async def callback(self, interaction: Interaction):
        self.view.value = (
            True if self.custom_id == f"{CUSTOM_ID_PREFIX}confirm_button" else False
        )
        self.view.stop()


class ConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=10.0)
        self.value = None
        self.add_item(
            ConfirmButton("Yes", ButtonStyle.green, custom_id="confirm_button")
        )
        self.add_item(ConfirmButton("No", ButtonStyle.red, custom_id="decline_button"))


class ThreadCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Close", style=ButtonStyle.red, custom_id=f"{CUSTOM_ID_PREFIX}thread_close")  # type: ignore
    async def thread_close_button(self, button: Button, interaction: Interaction):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        thread_author = await get_thread_author(interaction.channel)  # type: ignore
        await close_help_thread(
            "BUTTON", interaction.channel, thread_author, interaction.user
        )

    async def interaction_check(self, interaction: Interaction) -> bool:

        # because we aren't assigning the persistent view to a message_id.
        if (
            not isinstance(interaction.channel, Thread)
            or interaction.channel.parent_id != HELP_CHANNEL_ID
        ):
            return False

        if interaction.channel.archived or interaction.channel.locked:  # type: ignore
            return False

        thread_author = await get_thread_author(interaction.channel)  # type: ignore
        if interaction.user.id == thread_author.id or interaction.user.get_role(HELP_MOD_ID):  # type: ignore
            return True
        else:
            await interaction.send(
                "You are not allowed to close this thread.", ephemeral=True
            )
            return False


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.close_empty_threads.start()
        self.bot.loop.create_task(self.create_views())

    async def create_views(self):
        if getattr(self.bot, "help_view_set", False) is False:
            self.bot.help_view_set = True
            self.bot.add_view(HelpView(self.bot))
            self.bot.add_view(ThreadCloseView())

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id == HELP_CHANNEL_ID
            and message.type is MessageType.thread_created
        ):
            await message.delete(delay=5)
        if (
            isinstance(message.channel, Thread)
            and message.channel.parent_id == HELP_CHANNEL_ID
            and message.type is MessageType.pins_add
        ):
            await message.delete(delay=10)

    @commands.Cog.listener()
    async def on_thread_member_remove(self, member: ThreadMember):
        thread = member.thread
        if thread.parent_id != HELP_CHANNEL_ID or thread.archived:
            return

        thread_author = await get_thread_author(thread)
        if member.id != thread_author.id:
            return

        await close_help_thread(
            "EVENT [thread_member_remove]", thread, thread_author, self.bot.user
        )

    @tasks.loop(hours=24)
    async def close_empty_threads(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(GUILD_ID)
        active_help_threads = [
            thread
            for thread in await guild.active_threads()
            if thread.parent_id == HELP_CHANNEL_ID
            and (not thread.locked and not thread.archived)
        ]

        thread: Thread
        for thread in active_help_threads:
            thread_created_at = utils.snowflake_time(thread.id)

            # We don't want to close it before the wait_for.
            if (
                utils.utcnow() - timedelta(seconds=WAIT_FOR_TIMEOUT)
                <= thread_created_at
            ):
                continue

            all_messages = [
                message
                for message in (
                    await thread.history(limit=3, oldest_first=True).flatten()
                )
                if message.type is MessageType.default
            ]
            # can happen, ignore.
            if not all_messages or not (all_messages and all_messages[0].mentions):
                continue

            thread_author = all_messages[0].mentions[0]
            if len(all_messages) >= 2:
                members = [x.id for x in await thread.fetch_members()]
                if all_messages[1].author == thread_author and members == [
                    thread_author.id,
                    guild.me.id,
                ]:
                    await thread.send(f"<@&{HELPER_ROLE_ID}>", delete_after=5)
                    continue
            else:
                await close_help_thread(
                    "TASK [close_empty_threads]", thread, thread_author, self.bot.user
                )
                continue

    @commands.command()
    @commands.is_owner()
    async def help_menu(self, ctx):
        for section in split_txtfile("helpguide.txt"):
            await ctx.send(embed=Embed(description=section, color=Colour.yellow()))

        await ctx.send(
            content="**:white_check_mark: If you've read the guidelines above, click a button to create a help thread!**",
            view=HelpView(self.bot),
        )

    @commands.command()
    async def close(self, ctx):
        if (
            not isinstance(ctx.channel, Thread)
            or ctx.channel.parent_id != HELP_CHANNEL_ID
        ):
            return

        thread_author = await get_thread_author(ctx.channel)
        if not (ctx.author.id == thread_author.id or ctx.author.get_role(HELP_MOD_ID)):
            return await ctx.send("You are not allowed to close this thread.")

        await close_help_thread("COMMAND", ctx.channel, thread_author, ctx.author)

    @commands.command()
    @commands.has_role(HELP_MOD_ID)
    async def topic(self, ctx, *, topic: str):
        if not (isinstance(ctx.channel, Thread) and ctx.channel.parent.id == HELP_CHANNEL_ID):  # type: ignore
            return await ctx.send("This command can only be used in help threads!")

        author = match(NAME_TOPIC_REGEX, ctx.channel.name).group("author")  # type: ignore
        await ctx.channel.edit(name=f"{topic} ({author})")

    @commands.command()
    @commands.has_role(HELP_MOD_ID)
    async def transfer(self, ctx, *, new_author: Member):
        if not (isinstance(ctx.channel, Thread) and ctx.channel.parent_id == HELP_CHANNEL_ID):  # type: ignore
            return await ctx.send("This command can only be used in help threads!")

        topic = match(NAME_TOPIC_REGEX, ctx.channel.name).group("topic")  # type: ignore
        first_thread_message = (
            await ctx.channel.history(limit=1, oldest_first=True).flatten()
        )[0]
        old_author = first_thread_message.mentions[0]

        await ctx.channel.edit(name=f"{topic} ({new_author})")
        await first_thread_message.edit(content=new_author.mention)
        # Send log
        embed_log = Embed(
            title=":arrow_right: Help thread transferred",
            url=ctx.channel.jump_url,
            description=(
                f"{ctx.channel.mention}\n\nHelp thread created by {old_author.mention} "
                f"has been transferred to {new_author.mention} by {ctx.author.mention}.\n\n"
                f"Thread author: `{old_author} ({old_author.id})`\n"
                f"New author: `{new_author} ({new_author.id})`\n"
                f"Transferred by: `{ctx.author} ({ctx.author.id})`"
            ),
            colour=0x3B88C3,  # Blue
        )
        await ctx.guild.get_channel(HELP_LOGS_CHANNEL_ID).send(embed=embed_log)


def setup(bot):
    bot.add_cog(HelpCog(bot))
