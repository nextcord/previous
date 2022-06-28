**Why does on_message make my commands stop working?**
https://discordpy.readthedocs.io/en/latest/faq.html#why-does-on-message-make-my-commands-stop-working
Overriding the default provided on_message forbids any extra commands from running. To fix this, add a `bot.process_commands(message)` line at the end of your on_message.

**Or use a listener:** with a listener, you dont need to do the above.
https://nextcord.readthedocs.io/en/latest/ext/commands/api.html#nextcord.ext.commands.Bot.listen
