from nextcord.ext import commands
from os import environ as env
from re import compile

bot = commands.Bot("=")

issue_regex = compile(r"##(\d+)")

@bot.listen()
async def on_message(message):
    if (result := issue_regex.search(message.content)):
        issue_id = result.groups()[0]
        await message.channel.send(f"https://github.com/nextcord/nextcord/issues/{issue_id}")

@bot.command()
async def todo(ctx):
    await ctx.send("https://github.com/nextcord/nextcord/projects/1 and going through all the issues")

bot.run(env["TOKEN"])
