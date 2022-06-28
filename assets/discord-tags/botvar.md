{set("var", if(args.0, args.0, "variable"))}
Need to keep track of a variable between functions? No problem!

⚠️ Careful what you name it though, else you might overwrite something ⚠️ 

Just add it to your `commands.Bot` or `discord.Client` instance like so:
```py
bot = commands.Bot(...)
bot.{get("var")} = 0

async def foo():
    bot.{get("var")} += 1

# In a cog
@commands.command()
async def counter(self,ctx):
    await ctx.send("Current Counter is at {}".format(ctx.bot.{get("var")}))
```


This also allows you to access this from other cogs/extensions/functions. Anywhere you have access to the bot instance

- credit Mellow#0025