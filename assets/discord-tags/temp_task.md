**To unmute/tempmute or unban/tempban people, I'd recommend using bot loop!**

> And here's why...

1️⃣ Using a sleep function inside of the mute/ban-command would not persist between bot restarts
➜ *You might want to load unmutes/unbans when the bot is ready again*
2️⃣ A tasks.loop() decorator would eat CPU when checking if the user is ready to unmute.
➜ *You might want to unban or unmute people at the exact time*

> And here is one example for how to do that! ||Example: tempban-command||

• First, you are going to create the tempban-command normally.

```py
@bot.command()
@commands.has_permissions(ban_members = True)
async def tempban(ctx: commands.Context, member: nextcord.Member, seconds: int) -> None:
    await member.ban()

    # here's where you store the unban-timestamp into a database
    # -> this would work using datetime.datetime.timestamp(datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))

    bot.loop.call_later(seconds, asyncio.create_task, member.unban())```

• That's also how you would call the function on bot startup:

```py
import datetime
for entry in data: # where entry[0] is the guild_id, entry[1] the member_id and entry[2] the timestamp
    guild = bot.get_guild(entry[0])
    member = guild.get_member(entry[1])
    seconds = (datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(entry[2])).total_seconds()
    bot.loop.call_later(seconds, asyncio.create_task, member.unban())```

When you are working with tempmute, you'll have to replace `await member.ban()` with adding the mute-role and `await member.unban()` with removing the mute role.

Docs for `asyncio.loop.call_later`:
🔗 <https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.call_later>

**~ KingMigDOR#0001**
