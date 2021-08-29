from nextcord.ext import commands
from os import environ as env
from re import compile
from threading import Thread

bot = commands.Bot("=")

issue_regex = compile(r"##(\d+)")

@bot.event()
async def on_slash_command_error(ctx,error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.channel.send("You are missing a required argument.")
        return
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.channel.send("This command does not exist!")
        return
    await ctx.channel.send("An exception occurred: " + str(error))
@bot.listen()
async def on_message(message):
    if (result := issue_regex.search(message.content)):
        issue_id = result.groups()[0]
        await message.channel.send(f"https://github.com/nextcord/nextcord/issues/{issue_id}")
       

@bot.command()
async def todo(ctx):
    await ctx.send("https://github.com/nextcord/nextcord/projects/1 and going through all the issues")
    
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! My ping is {round(bot.latency*1000)/1000}ms.")
    
    

bot.run(env["TOKEN"])
