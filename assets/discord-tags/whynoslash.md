__Most common issues__
1. You didn't invite the bot to your guild with the application.commands oauth enabled. Go to the developer portal, make an invite with both bot and applications.commands enabled, and re-authorize your bot for your server.

2. You're using global commands and probably haven't waited (up to) an hour for them to appear.

3. Discord gets weird sometimes and doesn't refresh available commands. Try restarting your Discord client.

__Lesser common issues__
4. You're adding the cogs with slash commands in them too late inside of your bot. You either need to add them _before_ `on_connect` is called (preferably before the bot is even started), or run the global and/or guild rollout functions yourself.

5. You're overriding `on_connect`, which adds the application commands to bot/client (including ones inside cogs) and rolls out global commands. Either stop overriding it, or add `bot.add_startup_application_commands()` and `await bot.rollout_application_commands()` to it.

6. You're overriding `on_guild_available`, which rolls out commands to guilds. Either stop overriding it, or add the following codeblock to it:
```py
try:
    if self._rollout_all_guilds or self._connection.get_guild_application_commands(guild.id, rollout=True):
    await guild.rollout_application_commands()
except Forbidden as e:
    pass
```
