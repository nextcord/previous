from __future__ import annotations

import asyncio
from datetime import timedelta
from os import environ as env

from nextcord import (
    Button,
    ClientUser,
    Color,
    Embed,
    enums,
    Forbidden,
    ForumChannel,
    HTTPException,
    Interaction,
    Member,
    Message,
    slash_command,
    SlashOption,
    Thread,
    ThreadMember,
    ui,
    utils,
)
from nextcord.ext import application_checks, commands, tasks

from .utils.common import IgnoreMe

GUILD_ID = int(temp) if (temp := env.get("GUILD_ID")) else None
HELP_CHANNEL_ID = int(temp) if (temp := env.get("HELP_CHANNEL_ID")) else None
HELP_LOG_CHANNEL_ID = int(temp) if (temp := env.get("HELP_LOG_CHANNEL_ID")) else None
HELP_NOTIFICATION_ROLE_ID = (
    int(temp) if (temp := env.get("HELP_NOTIFICATION_ROLE_ID")) else None
)
HELP_MOD_ROLE_ID = int(temp) if (temp := env.get("HELP_MOD_ROLE_ID")) else None
HELP_TAG_CLOSED_ID = int(temp) if (temp := env.get("HELP_TAG_CLOSED_ID")) else None

CUSTOM_ID_PREFIX: str = "help:"
THREAD_CLOSING_MESSAGE = (
    "If your question has not been answered or your issue not "
    "resolved, we suggest taking a look at [Python Discord's Guide to "
    "Asking Good Questions](https://www.pythondiscord.com/pages/guides/pydis-guides/asking-good-questions/) "
    "to get more effective help."
)
WAIT_FOR_TIMEOUT: int = 1800  # 30 minutes
NO_HELP_MESSAGE: str = "You are banned from creating help threads. DM Modmail if you want to appeal it."


async def close_help_thread(
    method: str, thread: Thread, closed_by: Member | ClientUser
):
    if thread.locked or thread.archived:
        return

    if not thread.last_message or not thread.last_message_id:
        _last_msg = (await thread.history(limit=1).flatten())[0]
    else:
        _last_msg = thread.get_partial_message(thread.last_message_id)

    thread_jump_url = _last_msg.jump_url

    # Send closed message to thread.
    embed_reply = Embed(
        title="This thread has now been closed.",
        description=THREAD_CLOSING_MESSAGE,
        color=Color.dark_theme(),
    )
    await thread.send(embed=embed_reply)

    if HELP_TAG_CLOSED_ID not in thread.applied_tag_ids:
        # Editing the tags causes the thread to un-archive and un-lock, so we have to do it before archive + lock.
        await thread.edit(
            applied_tags=(
                (thread.applied_tags or [])
                + [thread.parent.get_tag(HELP_TAG_CLOSED_ID)]
            )
        )

    await thread.edit(archived=True, locked=True)  # Locks the thread.

    # Send closed log to logging channel.
    embed_log = Embed(
        title=":x: Closed help thread",
        description=(
            f"{thread.mention}\n\nHelp thread created by {thread.owner.mention} has been closed by {closed_by.mention} "
            f"using **{method}**.\n\n"
            f"Thread author: `{thread.owner} ({thread.owner_id})`\n"
            f"Closed by: `{closed_by} ({closed_by.id})`"
        ),
        colour=0xDD2E44,  # Red
    )
    await thread.guild.get_channel(HELP_LOG_CHANNEL_ID).send(embed=embed_log)

    # Make some slight changes to the thread-closer embed to send to the user via DM.

    embed_reply.title = f"Your help thread in the {thread.guild.name} server has been closed."
    embed_reply.description += f"\n\nName: **{thread.name}**"
    tag_list = []
    for tag in thread.applied_tags:
        if tag.id != HELP_TAG_CLOSED_ID:
            tag_list.append(f"{tag.emoji} {tag.name}")

    if tag_list:
        embed_reply.description += f"\nTags: {', '.join(tag_list)}"

    embed_reply.description += f"\n\nYou can use [**this link**]({thread_jump_url}) to access the archived thread for future reference."
    if thread.guild.icon:
        embed_reply.set_thumbnail(url=thread.guild.icon.url)
    try:
        await thread.owner.send(embed=embed_reply)
    except (HTTPException, Forbidden):
        pass


class ThreadCloseView(ui.View):
    def __init__(self, *, bot: commands.Bot | None = None):
        super().__init__(timeout=None)
        self._bot = bot

    @ui.button(
        label="Close",
        style=enums.ButtonStyle.red,
        custom_id=f"{CUSTOM_ID_PREFIX}thread_close",
    )
    async def thread_close_button(self, button: Button, interaction: Interaction):
        button.disabled = True
        ret_msg: Message | None = await interaction.response.edit_message(view=self)
        if isinstance(interaction.channel, Thread):
            await close_help_thread("BUTTON", interaction.channel, interaction.user)
        else:
            await interaction.send("This is intended to be in a help thread, this is a bug in Previous!", ephemeral=True)

        if self._bot and ret_msg:
            # print(f"Existing views: {self._bot._connection._view_store._views}")
            # print(f"Removing view {self}, {ret_msg.id}")
            # TODO: For some reason, message-specific views are getting added when the button is clicked, and I don't
            #  know why or how. Maybe this is normal, but I know little about how views work. This seems like a really
            #  bad memory leak for bigger bots.
            self._bot.remove_view(self, ret_msg.id)
            # print(f"View Dump: \n   {'\n   '.join([f'{key}: {id(value)} {value}' for key, value in self._bot._connection._view_store._views.items()])}")

    async def interaction_check(self, interaction: Interaction) -> bool:
        # because we aren't assigning the persistent view to a message_id.
        # print("Hit Interaction check.")
        if (
            not isinstance(interaction.channel, Thread)
            or interaction.channel.parent_id != HELP_CHANNEL_ID
        ):
            # print("Not in help thread")
            await interaction.send("This is intended to be in a help thread, this is a bug in Previous!", ephemeral=True)
            return False

        if interaction.channel.archived or interaction.channel.locked:  # type: ignore
            # print("Already closed.")
            return False

        if (
            interaction.user.id == interaction.channel.owner_id
            or interaction.user.get_role(HELP_MOD_ROLE_ID)
        ):
            # print("Passed.")
            return True
        else:
            # print("Not allowed to close thread.")
            await interaction.send(
                "You are not allowed to close this thread.", ephemeral=True
            )
            return False


def in_help_thread():
    async def predicate(interaction: Interaction):
        if HELP_CHANNEL_ID:
            if not isinstance(interaction.channel, Thread):
                await interaction.send(
                    "This command is only usable in help threads.", ephemeral=True
                )
                raise IgnoreMe()
            elif interaction.channel.parent_id != HELP_CHANNEL_ID:
                await interaction.send(
                    "This command is only usable in help threads.", ephemeral=True
                )
                raise IgnoreMe()
            else:
                return True
        else:
            await interaction.send(
                "The help channel ID isn't set but you're here, this is a bug with the bot!",
                ephemeral=True,
            )
            return False

    return application_checks.check(predicate)


class HelpForumCog(commands.Cog):
    def __init__(self, bot: commands.Bot, topic_choices: dict[str, tuple[str, int]]):
        self.bot = bot
        self.topic_choices = topic_choices

        self._view: ui.View = None

        self.change_thread_topic.options["tag"].choices = {
            f"{key} {value[0]}": key for key, value in self.topic_choices.items()
        }
        self.bot.loop.create_task(self.create_views())

    async def create_views(self):
        if getattr(self.bot, "help_view_set", False) is False:
            self.bot.help_view_set = True
            self._view = ThreadCloseView(bot=self.bot)
            self.bot.add_view(self._view)
            # print(f"Added view {self._view}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Help Forum Cog ready!")

    # @commands.Cog.listener()
    # async def on_interaction(self, interaction: Interaction):
    #     # print(interaction.type)
    #     # print(interaction.data)
    #     # print(self.bot.views())
    #     # rint(self.bot.views()[0].is_finished())
    #     # print(self.bot.views()[0].children)
    #     # print(self.bot.views()[0].children[0].custom_id)
    #     print(interaction.data)
    #     print(interaction.id)
    #     print(self.bot._connection._view_store._views)
    #     print(f"OWN VIEW: {self._view}, {self._view.is_finished()} ID {self._view.id}")
    #     print(f"CHILDREN {[child for child in self._view.children]}")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if (
            isinstance(message.channel, Thread)
            and message.channel.parent_id == HELP_CHANNEL_ID
            and message.type is enums.MessageType.pins_add
        ):
            await message.delete(delay=10)

    @commands.Cog.listener()
    async def on_thread_create(self, thread: Thread):
        if thread.parent_id == HELP_CHANNEL_ID:
            # Send help log
            tags_string = (
                ", ".join(
                    [f"{tag.emoji.name} {tag.name}" for tag in thread.applied_tags]
                )
                or "None"
            )
            embed_log = Embed(
                title="✅ Help thread created",
                url=thread.jump_url,
                description=(
                    f"{thread.mention}\n\n"
                    f"Tags: {tags_string}\n"
                    f"Created by: `{thread.owner} ({thread.owner_id})`"
                ),
            )
            await thread.guild.get_channel(HELP_LOG_CHANNEL_ID).send(embed=embed_log)
            embed_thread = Embed(
                # title="Close Thread",
                color=Color.green(),
                description=(
                    f"You can close the thread with this button or the "
                    f"{self.close_thread.get_mention(thread.guild) or self.close_thread.get_mention()} "
                    f"command."
                ),
            )

            close_button_view = ThreadCloseView()

            # This prevents the view from being added to the synced message views and eating the interactions.
            close_button_view.prevent_update = False

            msg = await thread.send(embed=embed_thread, view=close_button_view)
            # it's a persistent view, we only need the button.
            close_button_view.stop()
            # print(f"Freshly created view ID: {id(close_button_view)} | {msg.id}")
            await msg.pin(reason="First message in help thread with the close button.")

            await thread.send(f"<@&{HELP_NOTIFICATION_ROLE_ID}>", delete_after=5)


    @commands.Cog.listener()
    async def on_thread_member_remove(self, member: ThreadMember):
        if member.thread.parent_id != HELP_CHANNEL_ID or member.thread.archived:
            return

        if member.id != member.thread.owner_id:
            return

        await close_help_thread("EVENT [thread_member_remove]", member.thread, self.bot.user)

    @slash_command(name="close", guild_ids=[GUILD_ID] or None)
    @in_help_thread()
    async def close_thread(self, interaction: Interaction):
        # This command in the server should have the following channel overrides:
        #     All Channels - False
        #     <Target forum channel> - True

        thread: Thread = interaction.channel  # type: ignore  # The check requires this to be a thread.
        if thread.owner_id == interaction.user.id or interaction.user.get_role(HELP_MOD_ROLE_ID):
            await interaction.send("Closing.", ephemeral=True)
            await close_help_thread("COMMAND", thread, interaction.user)
        else:
            await interaction.send(
                "You do not have authorization to close this thread.",
                ephemeral=True,
            )

    @slash_command(name="topic", guild_ids=[GUILD_ID] or None)
    @in_help_thread()
    async def change_thread_topic(
        self,
        interaction: Interaction,
        name: str | None = SlashOption(description="The thread's topic."),
        tag: str
        | None = SlashOption(
            description="The emoji to use for the topic.",
            choices={},
        ),
    ):
        """Sets the topic of a help thread."""
        # This command in the server should have the following channel overrides:
        #     All Channels - False
        #     <Target forum channel> - True

        thread: Thread = interaction.channel  # type: ignore  # The check requires this to be a thread.
        if thread.owner_id == interaction.user.id:
            output_msg = []
            kwargs = {}
            if name and thread.name != name:
                kwargs["name"] = name
                output_msg.append("changed the thread name")
            if tag:
                old_tag_ids = thread.applied_tag_ids
                tag_name, tag_id = self.topic_choices[tag]
                # "Toggle" the tag.
                if tag_id in old_tag_ids:
                    new_tags = []
                    for old_tag in thread.applied_tags:
                        if old_tag.id != tag_id:
                            new_tags.append(old_tag)

                    kwargs["applied_tags"] = new_tags
                    output_msg.append(f'removed the "{tag_name}" tag')
                else:
                    kwargs["applied_tags"] = thread.applied_tags + [
                        thread.parent.get_tag(tag_id)
                    ]
                    output_msg.append(f'added the "{tag_name}" tag')

            if kwargs:
                # Okay-ish-ly "fancy" thread editing.
                await thread.edit(**kwargs)
                # Stupidly "fancy" output message mixing.
                await interaction.send(
                    f'{" and ".join(output_msg).capitalize()}.', ephemeral=True
                )
            else:
                await interaction.send("Changed nothing.")
        else:
            await interaction.send(
                "You do not have authorization to change this threads topic.",
                ephemeral=True,
            )


def setup(bot: commands.Bot):
    env_var_messages = []
    if HELP_CHANNEL_ID is None:
        env_var_messages.append('"HELP_CHANNEL_ID"')

    if HELP_LOG_CHANNEL_ID is None:
        env_var_messages.append('"HELP_LOG_CHANNEL_ID"')

    if HELP_NOTIFICATION_ROLE_ID is None:
        env_var_messages.append('"HELP_NOTIFICATION_ROLE_ID"')

    if HELP_MOD_ROLE_ID is None:
        env_var_messages.append('"HELP_MOD_ROLE_ID"')

    if HELP_TAG_CLOSED_ID is None:
        env_var_messages.append('"HELP_TAG_CLOSED_ID"')

    if env_var_messages:
        raise ValueError(
            f"The following environmental variables must be set for this extension: {', '.join(env_var_messages)}"
        )

    # We want the topic slash command to have choices, and not autocomplete. This is a problem for 3 reasons:
    #  1. We also want the choices to be dynamic to the moderator-only tags added to the forum channel
    #  2. Depending on when during startup the choices are set (race condition), the topic command may get deleted and
    #      re-upserted, which would trash the permission config. Unacceptable.
    #  3. Auth isn't set until bot.run() is ran because that's when it's given the token.
    #
    #  The best solution it seems is to set the default HTTP auth and fetch the channel data before the bot starts,
    #  avoiding the race condition entirely.
    # TODO: This requires the HTTP Re-Core PR, which will hopefully be added in 3.0.
    bot.http.set_default_auth(f"Bot {env['TOKEN']}")
    channel = bot.loop.run_until_complete(bot.fetch_channel(HELP_CHANNEL_ID))
    if isinstance(channel, ForumChannel):
        tags = {}
        for tag in channel.available_tags:
            if tag.moderated and tag.id != HELP_TAG_CLOSED_ID and tag.emoji:
                tags[tag.emoji.name] = (tag.name, tag.id)

    else:
        raise ValueError(
            f"The channel ID provided ({HELP_CHANNEL_ID}) is not a forum channel."
        )
    # TODO: Add help thread ban support.
    bot.add_cog(HelpForumCog(bot, tags))
