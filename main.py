from nextcord.ext import commands
from os import environ as env
from re import compile
from threading import Thread

bot = commands.Bot("=")

issue_regex = compile(r"##(\d+)")

@bot.listen()
async def on_message(message):
    if (result := issue_regex.search(message.content)):
        issue_id = result.groups()[0]
        await message.channel.send(f"https://github.com/nextcord/nextcord/issues/{issue_id}")
       

@bot.command(help="TODO")
async def todo(ctx):
    await ctx.send("https://github.com/nextcord/nextcord/projects/1 and going through all the issues")
    
@bot.command(help="Returns the ping of this bot", brief = "Returns the ping of this bot")
async def ping(ctx):
    await ctx.send(f"Pong! My ping is {round(bot.latency*1000000)/1000000} microseconds.")
    
    

bot.run(env["TOKEN"])
