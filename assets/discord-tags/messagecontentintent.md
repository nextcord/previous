**Why is message.content None or empty?** <https://docs.nextcord.dev/en/latest/intents.html#what-happened-to-my-prefix-commands>
Discord recently introduced another intent to ~~annoy everyone~~ limit the usage of message contents for bots. You now need to enable this intent to get the following from a message: `.content, .embeds, .attachments, .components`.

*How to enable it?*
It's like how you enable the members or presences intents.
**You need to enable it on the portal!** and in code:
```py
from nextcord import Intents

# Using Intents.all()
# you don't need worry about this.

# Using Intent.default()
# this can also be your existing instance of Intents.
my_intents = Intents.default()
my_intents.message_content = True

# Never specified intents
# we recommend constructing an Intents object with the intents you need.
# Something like this:
# my_intents = Intents(messages=True, message_content=True, guilds=True)
# that will enable the message intent and guilds because that is required for ext/text/prefix commands.

# passing it
bot = commands.Bot(..., intents=my_intents)
```
*I don't want to enable it!*
k. You don't need to, you can still get the stuff if your bot is mentioned or in dms.

*but I use slash commands?*
Good choice! You do not need this intent for slash commands, it is __required__ for ext/text/prefix commands.

*I can't enable it on the portal!*
Don't worry! Since the intent is not enforced yet (it will be on September 1st) we added a temporary method to change the api version to where you don't need to explicitly enable it.
This should be above everything in your main file (like bot.py)
```py
import nextcord
nextcord.http._modify_api_version(9)
```