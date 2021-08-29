import os
from os import environ as env
from re import compile

import aiohttp
from nextcord.ext import commands
from nextcord.ext.commnds import errors

bot = commands.Bot("=")
bot.load_extension("jishaku")

issue_regex = compile(r"##(\d+)")
discord_regex = compile(r"#!(\d+)")

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, errors.MissingRequiredArgument):
        await ctx.channel.send("You are missing a required argument.")
        return
    if isinstance(error, errors.CommandNotFound):
        await ctx.channel.send("This command does not exist.")
        return
    if isinstance(error, errors.TooManyArguments):
	await ctx.channel.send("You are giving too many arguments!")
	return
    if isinstance(error,errors.BadArgument):
	await ctx.channel.send("The library ran into an error attempting to parse your argument.")
	return
    await ctx.channel.send("This command raised an exception: " + str(error))



@bot.listen()
async def on_message(message):
    if (result := issue_regex.search(message.content)):
        issue_id = result.groups()[0]
        await message.channel.send(f"https://github.com/nextcord/nextcord/issues/{issue_id}")
    if (result := discord_regex.search(message.content)):
        issue_id = result.groups()[0]
        await message.channel.send(f"https://github.com/rapptz/discord.py/issues/{issue_id}")

@bot.command()
async def todo(ctx):
    await ctx.send("https://github.com/nextcord/nextcord/projects/1 and going through all the issues")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}") 
    else:
        if os.path.isfile(filename):
            print(f"Unable to load {filename[:-3]}") 

async def startup():
	bot.session = aiohttp.ClientSession()

bot.loop.create_task(startup())
bot.run(env["TOKEN"])
