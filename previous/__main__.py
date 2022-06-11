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
