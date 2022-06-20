from os import getenv
from typing import TYPE_CHECKING, Literal

import nextcord
from nextcord import abc
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Context
from nextcord.mentions import AllowedMentions

if TYPE_CHECKING:
    from previous.__main__ import Previous


LOG_CHANNEL_ID = int(getenv("BOT_LINKING_LOG_CHANNEL_ID", 0))
GUILD_ID = int(getenv("GUILD_ID", 0))
BOOSTER_ROLE_ID = int(getenv("BOOSTER_ROLE_ID", 0))


class BotLinking(commands.Cog):
    def __init__(self, bot: Previous):
        self.bot = bot
        # self.prune_loop.start()
        # FIXME: comment for testing, temporary - will allow better config

    @commands.group()
    async def link(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @link.command()
    @commands.has_permissions(administrator=True)
    async def add(
        self,
        ctx,
        status: Literal["booster", "admin", "special"],
        bot: nextcord.User,
        owner: nextcord.User,
    ):
        if not bot.bot or owner.bot:
            await ctx.send("You fucked up the order. Good job.")
            return

        await self.bot.db.set(
            f"bots/{bot.id}", {"owner_id": owner.id, "status": status}
        )

        await ctx.send(f"Successfully linked <@{bot.id}> to <@{owner.id}>.")

    @link.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, bot: nextcord.Object):
        current = await self.bot.db.get(f"bots/{bot.id}")

        if not current:
            await ctx.send(f"This bot is not linked to anyone.")
            return

        await self.bot.db.delete(f"bots/{bot.id}")

        await ctx.send(f"Successfully unlinked <@{bot.id}>.")

    @link.command()
    @commands.has_permissions(administrator=True)
    async def list(self, ctx):
        bots = await self.bot.db.list("bots/")

        if bots is None:
            await ctx.send("No bots linked.")
            return

        text = ""

        for bot_id, metadata in bots.items():
            bot_id = bot_id.removeprefix("bots/")
            text += f"<@{bot_id}> linked to <@{metadata['owner_id']}> ({metadata['status']})\n"

        await ctx.send(text, allowed_mentions=AllowedMentions(users=[]))

    @link.command()
    @commands.has_permissions(administrator=True)
    async def prune(self, ctx):
        await self.prune_bots()
        await ctx.send("ok")

    @tasks.loop(seconds=30)
    async def prune_loop(self):
        try:
            await self.prune_bots()
        except RuntimeError as e:
            print(f"ERROR IN PRUNE_BOTS: {type(e)}: {e}\n{e.__traceback__}")

    async def prune_bots(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(GUILD_ID)

        if guild is None:
            raise RuntimeError("Guild not found.")

        log_channel = guild.get_channel(LOG_CHANNEL_ID)

        if log_channel is None:
            raise RuntimeError("Log channel not found")

        if not isinstance(log_channel, abc.Messageable):
            raise RuntimeError(
                f"Log channel must be a messaeable, not {type(log_channel).__name__}"
            )

        for user in guild.members:
            if not user.bot:
                continue

            metadata = await self.bot.db.get(f"bots/{user.id}")
            if not metadata:
                # Bot is not linked, kick it
                try:
                    await user.kick(reason="Unlinked bot")
                except nextcord.Forbidden:
                    await log_channel.send(
                        f"Failed to kick {user.mention} (bot not linked)"
                    )
                    continue
                await log_channel.send(
                    f"Unlinked bot {user.mention} found, bot has been kicked. Please use previous' link command."
                )
                continue
            if metadata["status"] == "booster":
                owner = guild.get_member(metadata["owner_id"])
                if owner is None:
                    # Owner not in server?
                    try:
                        await user.kick(reason="Owner not in server")
                    except nextcord.Forbidden:
                        await log_channel.send(
                            f"Failed to kick {user.mention} (owner not in server)"
                        )
                        continue
                    await log_channel.send(
                        f"Owner <@{metadata['owner_id']}> not in server, {user.mention} has been kicked."
                    )
                    continue
                if owner.get_role(BOOSTER_ROLE_ID) is None:
                    # Owner unboosted
                    try:
                        await user.kick(reason="Owner unboosted")
                    except nextcord.Forbidden:
                        await log_channel.send(
                            f"Failed to kick {user.mention} (owner unboosted)"
                        )
                        continue
                    await log_channel.send(
                        f"Owner <@{metadata['owner_id']}> unboosted, {user.mention} has been kicked."
                    )

                    try:
                        await owner.send(
                            f"As a result of you unboosting nextcord, your bot {user.mention} has been kicked. Please re-boost to get your bot added back."
                        )
                    except nextcord.Forbidden:  # 400 error lol?  # hi epic this is a 403
                        pass


def setup(bot: Previous):
    bot.add_cog(BotLinking(bot))
