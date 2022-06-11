from os import getenv
from re import compile

import os
import nextcord
from aiohttp import ClientSession

from nextcord import Intents, Interaction
from nextcord.ext.commands import Bot
from nextcord.ext.commands import errors
from nextcord.ext.application_checks import errors as application_errors


class MyBot(Bot):
    session: ClientSession

    async def startup(self):
        self.session = ClientSession()

    def run(self, *args, **kwargs) -> None:
        self.loop.create_task(self.startup())

        super().run(*args, **kwargs)


bot = MyBot("=", intents=Intents(messages=True, guilds=True, members=True))

issue_regex = compile(r"##(\d+)")
discord_regex = compile(r"#!(\d+)")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, errors.CommandNotFound):
        return
    elif isinstance(error, errors.TooManyArguments):
        await ctx.send("You are giving too many arguments!")
        return
    elif isinstance(error, errors.BadArgument):
        await ctx.send(
            "The library ran into an error attempting to parse your argument."
        )
        return
    elif isinstance(error, errors.MissingRequiredArgument):
        await ctx.send("You're missing a required argument.")
    # kinda annoying and useless error.
    elif isinstance(error, nextcord.NotFound) and "Unknown interaction" in str(error):
        return
    elif isinstance(error, errors.MissingRole):
        role = ctx.guild.get_role(int(error.missing_role))  # type: ignore
        await ctx.send(f'"{role.name}" is required to use this command.')  # type: ignore
        return
    else:
        await ctx.send(
            f"This command raised an exception: `{type(error)}:{str(error)}`"
        )


@bot.event
async def on_application_command_error(
    interaction: Interaction, error: Exception
) -> None:
    if isinstance(error, application_errors.ApplicationMissingRole):
        role = interaction.guild.get_role(int(error.missing_role))  # type: ignore
        await interaction.send(f"{role.mention} role is required to use this command.", ephemeral=True)  # type: ignore
        return
    else:
        await interaction.send(
            f"This command raised an exception: `{type(error)}:{str(error)}`",
            ephemeral=True,
        )


@bot.listen()
async def on_message(message):
    if result := issue_regex.search(message.content):
        issue_id = result.groups()[0]
        await message.channel.send(
            f"https://github.com/nextcord/nextcord/issues/{issue_id}"
        )
    if result := discord_regex.search(message.content):
        issue_id = result.groups()[0]
        await message.channel.send(
            f"https://github.com/rapptz/discord.py/issues/{issue_id}"
        )


@bot.command()
async def todo(ctx):
    await ctx.send(
        "https://github.com/nextcord/nextcord/projects/1 and going through all the issues"
    )


for filename in os.listdir("./previous/cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"previous.cogs.{filename[:-3]}")
    elif os.path.isfile(filename):
        print(f"Unable to load {filename[:-3]}")


bot.load_extension("jishaku")
bot.run(getenv("TOKEN"))
