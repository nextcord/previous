from __future__ import annotations

from typing import TYPE_CHECKING

from nextcord.ext.commands import (
    Cog,
    Context,
    CommandNotFound,
    TooManyArguments,
    BadArgument,
    MissingRequiredArgument,
    MissingRole,
)
from nextcord import NotFound
from nextcord.ext.application_checks import ApplicationMissingRole

if TYPE_CHECKING:
    from nextcord import Interaction

    from ..__main__ import MyBot


class Errors(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception):
        error = getattr(error, "original", error)

        if isinstance(error, CommandNotFound):
            return

        elif isinstance(error, TooManyArguments):
            await ctx.send("You are giving too many arguments!")
        elif isinstance(error, BadArgument):
            await ctx.send(
                "The library ran into an error attempting to parse your argument."
            )
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send("You're missing a required argument.")
        # kinda annoying and useless error.
        elif isinstance(error, NotFound) and "Unknown interaction" in str(error):
            return
        elif isinstance(error, MissingRole):
            role = ctx.guild.get_role(int(error.missing_role))  # type: ignore
            await ctx.send(f'"{role.name}" is required to use this command.')  # type: ignore
        else:
            await ctx.send(
                f"This command raised an exception: `{type(error)}:{str(error)}`"
            )

    @Cog.listener()
    async def on_application_command_error(
        self, interaction: Interaction, error: Exception
    ):
        if isinstance(error, ApplicationMissingRole):
            role = interaction.guild.get_role(int(error.missing_role))  # type: ignore
            await interaction.send(f"{role.mention} role is required to use this command.", ephemeral=True)  # type: ignore
            return
        else:
            await interaction.send(
                f"This command raised an exception: `{type(error)}:{str(error)}`",
                ephemeral=True,
            )


def setup(bot: MyBot):
    bot.add_cog(Errors(bot))
