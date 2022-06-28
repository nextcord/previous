{set("inview", if(args.1, args.1, args.0))}

You can pass **any no. of parameters in __init__** while subclassing the View. Similarly, you can also pass a parameter for {get("inview")} like in the example and use it anywhere in your view.**

Example:
```py
class MyView(nextcord.ui.View):
    def __init__(self, {get("inview")}, *, timeout = 180.0):
        super().__init__(timeout=timeout)
        self.{get("inview")} = {get("inview")} # You can use `self.{get("inview")}` anywhere in the class

@bot.command()
async def button(ctx):
    await ctx.send(content='{args.0} in View Example', view = MyView({args.0}))
```
