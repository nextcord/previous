from os import environ as env
from typing import Literal

import nextcord
from nextcord.ext import commands, tasks
from nextcord.mentions import AllowedMentions

LOG_CHANNEL_ID = int(env["BOT_LINKING_LOG_CHANNEL_ID"])
GUILD_ID = int(env["GUILD_ID"])
BOOSTER_ROLE_ID = int(env["BOOSTER_ROLE_ID"])


class BotLinking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prune_bots.start()

    @commands.group()
    async def link(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("No.")

    @link.command()
    @commands.has_permissions(administrator=True)
    async def add(
        self,
        ctx,
        status: Literal["booster", "admin", "special"],
        bot: nextcord.Member,
        owner: nextcord.Member,
    ):
        db = self.bot.get_cog("Database")

        if not bot.bot or owner.bot:
            await ctx.send("You fucked up the order. Good job.")
            return

        current = await db.get(f"bots/{bot.id}")

        if current:
            await ctx.send(f"This bot is already linked to <@{current['owner_id']}>.")
            return

        await db.set(f"bots/{bot.id}", {"owner_id": owner.id, "status": status})

        await ctx.send(f"Successfully linked <@{bot.id}> to <@{owner.id}>.")

    @link.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, bot: nextcord.Member):
        db = self.bot.get_cog("Database")

        current = await db.get(f"bots/{bot.id}")

        if not current:
            await ctx.send(f"This bot is not linked to anyone.")
            return

        await db.delete(f"bots/{bot.id}")
        await bot.kick(reason="Bot unlinked!")

        await ctx.send(f"Successfully unlinked <@{bot.id}>.")

    @link.command()
    @commands.has_permissions(administrator=True)
    async def list(self, ctx):
        db = self.bot.get_cog("Database")

        bots = await db.list("bots/")

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
        await self.prune_bots()

    async def prune_bots(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(GUILD_ID)
        log_channel = await guild.fetch_channel(LOG_CHANNEL_ID)

        db = self.bot.get_cog("Database")

        for user in guild.members:
            if not user.bot:
                continue
            metadata = await db.get(f"bots/{user.id}")
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
                    await log_channel.send(f"Owner <@{metadata['owner_id']}> not in server, {user.mention} has been kicked.")
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
                        await owner.send(f"As a result of you unboosting nextcord, your bot {user.mention} has been kicked. Please re-boost to get your bot added back.")
                    except nextcord.Forbidden: # 400 error lol?
                        pass

def setup(bot):
    bot.add_cog(BotLinking(bot))
