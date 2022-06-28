**So you got a PrivilegedIntentsRequired error...**
This means that you enabled *one or more* of the following intents in code but not on the portal: `members`, `presences`, `message_content`.

*But I didn't enable any of them..?*
You definitely did. Here is 3 ways you could've enabled them:
**1.** ```py
my_intents = nextcord.Intents(..., members=True, ...)
# bot = commands.Bot(..., intents=my_intents)``` **2.** ```py
my_intents = nextcord.Intents.default()
my_intents.presences = True
# bot = commands.Bot(..., intents=my_intents)``` **3.** ```py
my_intent = nextcord.Intents.all() # enabled them all.
# bot = commands.Bot(..., intents=my_intents)```
*I enabled them on the portal and code but same error...?*
Please re-check the bot of who you're editing the portal of.
