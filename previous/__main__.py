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

    def on_application_command_error(self, *_):
        # we have a listener cog, use this to ignore consle errors
        ...


bot = MyBot("=", intents=Intents(messages=True, guilds=True, members=True))


for filename in os.listdir("./previous/cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"previous.cogs.{filename[:-3]}")
    elif os.path.isfile(filename):
        print(f"Unable to load {filename[:-3]}")


bot.load_extension("jishaku")
bot.run(getenv("TOKEN"))
