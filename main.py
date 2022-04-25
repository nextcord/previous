import os
from os import environ as env
from re import compile

import aiohttp
import nextcord
from nextcord import Intents
from nextcord.ext import commands
from nextcord.ext.commands import errors

bot = commands.Bot("=", intents=Intents(messages=True, guilds=True, members=True))
bot.load_extension("jishaku")

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
    elif isinstance(error, errors.NotOwner):
        return
    else:
        await ctx.send(
            f"This command raised an exception: `{type(error)}:{str(error)}`"
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


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")
    elif os.path.isfile(filename):
        print(f"Unable to load {filename[:-3]}")


async def startup():
    bot.session = aiohttp.ClientSession()


bot.loop.create_task(startup())
bot.run(env["TOKEN"])
