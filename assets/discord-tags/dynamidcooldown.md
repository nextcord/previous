```py
def bypass_for_owner(message):
    # Bypasses cooldown, no cooldown for this specific user
    if message.author.id == owner_id:
        return None
    # Otherwise cooldown of 1 per 1 second
    return commands.Cooldown(1,1)

@commands.dynamic_cooldown(bypass_for_owner)
@bot.command()
async def cmd(ctx):
    await ctx.send("test")
```

Docs: <https://nextcord.readthedocs.io/en/latest/ext/commands/api.html#nextcord.ext.commands.dynamic_cooldown>
