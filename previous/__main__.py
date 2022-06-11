from os import getenv, listdir
from os.path import isfile

from aiohttp import ClientSession

from nextcord import Intents
from nextcord.ext.commands import Bot


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


for filename in listdir("./previous/cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"previous.cogs.{filename[:-3]}")
    elif isfile(filename):
        print(f"Unable to load {filename[:-3]}")


bot.load_extension("jishaku")
bot.run(getenv("TOKEN"))
