import datetime
from typing import Dict, Optional
from asyncio import TimeoutError
from datetime import timedelta
from re import match

import nextcord
from nextcord.ext import commands, tasks
from nextcord import (
    Button,
    ButtonStyle,
    ChannelType,
    Colour,
    Embed,
    Forbidden,
    HTTPException,
    Interaction,
    Member,
    MessageType,
    Thread,
    ThreadMember,
    Message,
    ui,
    utils,
    AllowedMentions
)

from .utils.split_txtfile import split_txtfile
from .utils.stats import StatsClient

HELP_CHANNEL_ID: int = 881965127031722004
HELP_LOGS_CHANNEL_ID: int = 883035085434142781
HELPER_ROLE_ID: int = 882192899519954944
HELP_MOD_ID: int = 896860382226956329
GUILD_ID: int = 881118111967883295
CUSTOM_ID_PREFIX: str = "help:"
NAME_TOPIC_REGEX: str = r"(^.*?) \((.*?[0-9]{4})\)$"
WAIT_FOR_TIMEOUT: int = 1800 # 30 minutes

timeout_message: str = "You are currently timed out, please wait until it ends before trying again"
closing_message = ("If your question has not been answered or your issue not "
                   "resolved, we suggest taking a look at [Python Discord's Guide to "
                   "Asking Good Questions](https://www.pythondiscord.com/pages/guides/pydis-guides/asking-good-questions/) "
                   "to get more effective help.")

stats_client: StatsClient = StatsClient(None)


async def get_thread_author(channel: Thread) -> Member:
    history = channel.history(oldest_first = True, limit = 1)
    history_flat = await history.flatten()
    user = history_flat[0].mentions[0]
    return user


async def close_help_thread(method: str, thread_channel, thread_author):
    """Closes a help thread. Is called from either the close button or the
    =close command.
    """

    # no need to do any of this if the thread is already closed.
    if (thread_channel.locked or thread_channel.archived):
        return

    if not thread_channel.last_message or not thread_channel.last_message_id:
        _last_msg = (await thread_channel.history(limit = 1).flatten())[0]
    else:
        _last_msg = thread_channel.get_partial_message(thread_channel.last_message_id)

    thread_jump_url = _last_msg.jump_url

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
    embed_reply.description += f"\n\nYou can use [**this link**]({thread_jump_url}) to access the archived thread for future reference"
    if thread_channel.guild.icon:
        embed_reply.set_thumbnail(url=thread_channel.guild.icon.url)
    try:
        await thread_author.send(embed=embed_reply)
    except (HTTPException, Forbidden):
        pass

class TopicDropdown(nextcord.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = [
            nextcord.SelectOption(
                label='Python help',
                description='Questions related to Python, but not Nextcord.',
            ),
            nextcord.SelectOption(
                label='Nextcord',
                description='Questions which are related to Nextcord and '
                            'do not fit into other more specific categories.'
            ),
            nextcord.SelectOption(
                label="Text commands",
                description="Questions related to nextcord.ext.commands"
            ),
            nextcord.SelectOption(
                label="Slash commands",
                description="Questions related to slash commands, application commands, etc"
            ),
            nextcord.SelectOption(
                label="Migrating",
                description="Any questions relating to migrating from discord.py to Nextcord"
            ),
            nextcord.SelectOption(
                label="Hosting",
                description="Any questions related to hosting your bot"
            ),
            nextcord.SelectOption(
                label="Databases",
                description="Any questions related to using a database with Python"
            ),
            nextcord.SelectOption(
                label='Misc',
                description="Doesn't fit into any other categories listed."
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(f'Your favourite colour is {self.values[0]}')


class TopicView(nextcord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.dropdown = TopicDropdown()
        self.add_item(self.dropdown)



class HelpButton(ui.Button["HelpView"]):
    def __init__(self, help_type: str, *, style: ButtonStyle, custom_id: str, row: Optional[int]=None):
        super().__init__(
            label = f"{help_type} help",
            style = style,
            custom_id = f"{CUSTOM_ID_PREFIX}{custom_id}",
            row=row,
        )
        self._help_type: str = help_type

    async def create_help_thread(self, interaction: Interaction) -> Thread:
        thread = await interaction.channel.create_thread(
            name=f"{self._help_type} help ({interaction.user})",
            type=ChannelType.public_thread,
        )
        await stats_client.init_thread(thread_id=thread.id, help_type=self._help_type)

        await interaction.guild.get_channel(HELP_LOGS_CHANNEL_ID).send(
            content = f"Help thread for {self._help_type} created by {interaction.user.mention}: {thread.mention}!",
            allowed_mentions = AllowedMentions(users=False)
        )

        em = Embed(
            title = f"{self._help_type} Help thread",
            colour = Colour.blurple(),
            description = (
                "Please explain your issue in detail, helpers will respond as soon as possible."
                "\n\n**Please include the following in your initial message:**"
                "\n- Relevant code\n- Error (if present)\n- Expected behavior"
                f"\n\nRefer for more to our help guildlines in <#{HELP_CHANNEL_ID}>"
            )
        )
        em.set_footer(text = "You can close this thread with the button or =close command.")

        close_button_view = ThreadCloseView()

        msg = await thread.send(
            content = interaction.user.mention,
            embed = em,
            view = close_button_view
        )
        # it's a persistent view, we only need the button.
        close_button_view.stop()
        await msg.pin(reason = "First message in help thread with the close button.")
        return thread

    async def __launch_wait_for_message(self, thread: Thread, interaction: Interaction) -> None:
        assert self.view is not None
        
        def is_allowed(message: Message) -> bool:
            return message.author.id == interaction.user.id and message.channel.id == thread.id and not thread.archived  # type: ignore

        try:
            m: Message = await self.view.bot.wait_for("message", timeout=WAIT_FOR_TIMEOUT, check=is_allowed)
        except TimeoutError:
            await close_help_thread("TIMEOUT [launch_wait_for_message]", thread, interaction.user)
            await stats_client.delete_init(thread_id=thread.id)
            return
        else:
            # Get help channel thread first
            topic_view = TopicView()
            await thread.send(
                f"Please pick the topic which best suits your needs, {interaction.user.mention}",
                view=topic_view
            )
            await topic_view.wait()
            selected_item = topic_view.dropdown.values[0]

            await thread.edit(
                name=f"{selected_item} help ({interaction.user})",
            )

            # Drag everyone else in
            await thread.send(f"<@&{HELPER_ROLE_ID}>", delete_after=5)

            is_helper = bool(m.author.get_role(HELPER_ROLE_ID))
            await stats_client.create_thread(
                thread_id=thread.id,
                opened_by=thread.owner_id,
                initial_author_id=interaction.user.id,
                initial_message_id=m.id,
                initial_time_sent=m.created_at,
                time_opened=thread.created_at,
                initial_message_is_helper=is_helper,
                generic_topic=selected_item
            )
            return

    async def callback(self, interaction: Interaction):
        confirm_view = ConfirmView()

        def disable_all_buttons():
            for _item in confirm_view.children:
                _item.disabled = True

        confirm_content = f"Are you really sure you want to make a {self._help_type} help thread?"
        await interaction.send(content = confirm_content, ephemeral = True, view = confirm_view)
        await confirm_view.wait()
        if confirm_view.value is False or confirm_view.value is None:
            disable_all_buttons()
            content = "Ok, cancelled." if confirm_view.value is False else f"~~{confirm_content}~~ I guess not..."
            await interaction.edit_original_message(content = content, view = confirm_view)
        else:
            disable_all_buttons()
            await interaction.edit_original_message(content = "Created!", view = confirm_view)
            created_thread = await self.create_help_thread(interaction)
            await self.__launch_wait_for_message(created_thread, interaction)


class HelpView(ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout = None)
        self.bot: commands.Bot = bot

        # First row, or 'main' items
        self.add_item(
            HelpButton(
                "Open help thread",
                style=ButtonStyle.blurple,
                custom_id="new_help_thread"
            )
        )

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.timeout is not None:
            await interaction.send(timeout_message, ephemeral=True)
            return False

        return await super().interaction_check(interaction)

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

    @ui.button(label = "Close", style = ButtonStyle.red, custom_id = f"{CUSTOM_ID_PREFIX}thread_close")  # type: ignore
    async def thread_close_button(self, button: Button, interaction: Interaction):
        button.disabled = True
        await interaction.response.edit_message(view = self)
        thread_author = await get_thread_author(interaction.channel)  # type: ignore
        await close_help_thread("BUTTON", interaction.channel, thread_author)
        await stats_client.update_thread(
            thread_id=interaction.channel.id,
            time_closed=datetime.datetime.utcnow(),
            closed_by=interaction.user.id
        )

    async def interaction_check(self, interaction: Interaction) -> bool:

        # because we aren't assigning the persistent view to a message_id.
        if not isinstance(interaction.channel, Thread) or interaction.channel.parent_id != HELP_CHANNEL_ID:
            return False

        if (interaction.channel.archived or interaction.channel.locked):  # type: ignore
            return False

        if isinstance(interaction.user, Member) and interaction.user.timeout is not None:
            await interaction.send(timeout_message, ephemeral=True)
            return False

        thread_author = await get_thread_author(interaction.channel)  # type: ignore
        if interaction.user.id == thread_author.id or interaction.user.get_role(HELP_MOD_ID):  # type: ignore
            return True
        else:
            await interaction.send("You are not allowed to close this thread.", ephemeral=True)
            return False

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.close_empty_threads.start()
        self.bot.loop.create_task(self.create_views())

        # Funky, but saves rewriting everything.
        global stats_client
        stats_client.session = bot.session

    async def create_views(self):
        if getattr(self.bot, "help_view_set", False) is False:
            self.bot.help_view_set = True
            self.bot.add_view(HelpView(self.bot))
            self.bot.add_view(ThreadCloseView())

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id == HELP_CHANNEL_ID and message.type is MessageType.thread_created:
            await message.delete(delay = 5)

        if isinstance(message.channel, Thread) and message.channel.parent_id == HELP_CHANNEL_ID:
            if message.type is MessageType.pins_add:
                await message.delete(delay=10)

            else:
                is_helper = bool(message.author.get_role(HELPER_ROLE_ID))
                await stats_client.create_message(
                    is_helper=is_helper,
                    message_id=message.id,
                    author_id=message.author.id,
                    time_sent=message.created_at,
                    thread_id=message.channel.id,
                )

    @commands.Cog.listener()
    async def on_thread_member_remove(self, member: ThreadMember):
        thread = member.thread
        if thread.parent_id != HELP_CHANNEL_ID or thread.archived:
            return

        thread_author = await get_thread_author(thread)
        if member.id != thread_author.id:
            return

        await close_help_thread("EVENT", thread, thread_author)
        await stats_client.update_thread(
            thread_id=thread.id,
            time_closed=datetime.datetime.utcnow(),
            closed_by=member.id
        )

    @tasks.loop(hours=24)
    async def close_empty_threads(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(GUILD_ID)
        active_help_threads = [
            thread for thread in await guild.active_threads()
            if thread.parent_id == HELP_CHANNEL_ID and (not thread.locked and not thread.archived)
        ]

        thread: Thread
        for thread in active_help_threads:
            thread_created_at = utils.snowflake_time(thread.id)

            # We don't want to close it before the wait_for.
            if utils.utcnow() - timedelta(seconds=WAIT_FOR_TIMEOUT) <= thread_created_at:
                continue
            
            all_messages = [
                message for message in (await thread.history(limit=3, oldest_first=True).flatten())
                if message.type is MessageType.default
            ]
            # can happen, ignore.
            if not all_messages or not (all_messages and all_messages[0].mentions):
                continue

            thread_author = all_messages[0].mentions[0]
            if len(all_messages) >= 2:
                members = [x.id for x in await thread.fetch_members()]
                if all_messages[1].author == thread_author and members == [thread_author.id, guild.me.id]:
                    await thread.send(f"<@&{HELPER_ROLE_ID}>", delete_after=5)
                    continue
            else:
                await close_help_thread("TASK [close_empty_threads]", thread, thread_author)
                await stats_client.delete_init(thread_id=thread.id)
                continue

    @commands.command()
    @commands.is_owner()
    async def help_menu(self, ctx):
        for section in split_txtfile("helpguide.txt"):
            await ctx.send(embed=Embed(description=section, color=Colour.yellow()))

        await ctx.send(
            content = "**:white_check_mark: If you've read the guidelines above, click a button to create a help thread!**",
            view = HelpView(self.bot)
        )

    @commands.command()
    async def close(self, ctx):
        if not isinstance(ctx.channel, Thread) or ctx.channel.parent_id != HELP_CHANNEL_ID:
            return
            
        first_thread_message = (await ctx.channel.history(limit=1, oldest_first=True).flatten())[0]
        thread_author = first_thread_message.mentions[0]
        if not (ctx.author.id == thread_author.id or ctx.author.get_role(HELP_MOD_ID)):
            return await ctx.send("You are not allowed to close this thread.")

        thread_author = await get_thread_author(ctx.channel)
        await close_help_thread("COMMAND", ctx.channel, thread_author)
        await stats_client.update_thread(
            thread_id=ctx.channel.id,
            time_closed=datetime.datetime.utcnow(),
            closed_by=ctx.author.id
        )

    @commands.command()
    @commands.has_role(HELP_MOD_ID)
    async def topic(self, ctx, *, topic: str):
        if not (isinstance(ctx.channel, Thread) and ctx.channel.parent.id == HELP_CHANNEL_ID):  # type: ignore
            return await ctx.send("This command can only be used in help threads!")

        # generic_topic should be always set by help thread buttons
        await stats_client.update_thread(thread_id=ctx.channel.id, specific_topic=topic)

        author = match(NAME_TOPIC_REGEX, ctx.channel.name).group(2)  # type: ignore
        await ctx.channel.edit(name=f"{topic} ({author})")

    @commands.command()
    @commands.has_role(HELP_MOD_ID)
    async def transfer(self, ctx, *, new_author: Member):
        if not (isinstance(ctx.channel, Thread) and ctx.channel.parent_id == HELP_CHANNEL_ID):  # type: ignore
            return await ctx.send("This command can only be used in help threads!")

        topic = match(NAME_TOPIC_REGEX, ctx.channel.name).group(1)  # type: ignore
        first_thread_message = (await ctx.channel.history(limit=1, oldest_first=True).flatten())[0]
        old_author = first_thread_message.mentions[0]

        await ctx.channel.edit(name=f"{topic} ({new_author})")
        await first_thread_message.edit(content=new_author.mention)
        await ctx.guild.get_channel(HELP_LOGS_CHANNEL_ID).send(  # Send log
            content=f"Help thread {ctx.channel.mention} (created by {old_author.mention}) " \
                    f"has been transferred to {new_author.mention} by {ctx.author.mention}.",
        )

def setup(bot):
    bot.add_cog(HelpCog(bot))
