__Slash debugging__
1. If it is a global command, wait a bit after the last restart
2. Have you reloaded your discord client?
3. Does the guild have the application commands scope?
4. Do you load cogs after bot.run is called (for example in on_ready)
5. Do you override `on_connect`?
6. Does the command appear in the integration tab (server settings > integration > your bot) ?
7. Does the command work on mobile ?