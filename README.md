# Previous
The bot for ~~annoying nextcord members~~ managing some of nextcord's unique tasks.

# Running the bot
You need a [consul](https://consul.io) instance running.

## Env vars
```sh
GUILD_ID=... # The guild id the bot uses. This is the nextcord server.
BOOSTER_ROLE_ID=... # The booster role. Currently used for booster bots

HELP_LOG_CHANNEL_ID=... # The log channel the help cog uses
HELP_NOTIFICATION_ROLE_ID=... # The role that gets pinged in every help thread.
HELP_MOD_ROLE_ID=... # The role that is allowed to moderate help channels

BOT_LINKING_LOG_CHANNEL_ID=... # Logs for actions by the bot linking cog
```
