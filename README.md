# Previous
The bot managing the Official [Nextcord Discord Server][NEXTCORDSERVER].

## Features
- **Autopaste:**
    Automatically paste the contents of a file or codeblock to [our paste service][PASTESERVICE]. \
    (Source: [cogs/autopaste.py][AUTOPASTEPY])

- **Automatic stars update:**
    Automatically pull the stars from the [Nextcord][NEXTCORDREPOSITORY] and [Nextcord v3][NEXTCORDREPOSITORYV3] repoitories and update the [STARS_CHANNEL_ID] channel. \
    (Source: [cogs/stars.py][STARSPY])

- **Auto thread:**
    Automatically create a thread for each message sent in the [AUTO_THREAD_CHANNEL_ID] channel. \
    (Source: [cogs/autothread.py][AUTOTHREADPY])


- **Documentation:** 
    Search through the [Discord][DISCORDDOCS] and [Python][PYTHONDOCS] & [Nextcord][NEXTCORDDOCS] documentation. \
    (Source: [cogs/discorddoc.py ][DDOCSPY] (Discord) | [cogs/docs.py][DOCSPY] (Python & Nextcord))

- **Help System:**
    A help system using buttons for the [Nextcord server][NEXTCORDSERVER]. \
    (Source: [cogs/help.py][HELPPY]))	

- **Others:**
    - Database: simple database powered by [consul.io][CONSUL].
    (Source: [cogs/database.py][DATABASEPY])
    - Bot linking: stores which users bot are added to the nextcord server by boosting.
    (Source: [cogs/botlink.py][BOTLINKPY])
    - Charinfo: command to get information about a (unicode) character.
    (Source: [cogs/etc.py][ETCPY])

## Running the bot
1. Run a [consul.io][CONSUL] instance.
2. Create or fill in the environment variables shown in the [.env.example][ENVFILE] file.
3. Run the [main.py](./main.py) file to launch the bot.

Any further help regarding setting up the bot and getting everything working is not provided.
## Contributing
Refer to [Running the bot](#running-the-bot) for the steps on how to run the bot and contribute.

## Credits
- [Rapptz](https://github.com/Rapptz)' open sourced [RoboDanny](https://github.com/Rapptz/RoboDanny) discord bot for the following commands:
    - [charinfo][ETCPY]
    - [docs][DOCSPY]


[CONSUL]: https://www.consul.io/
[NEXTCORDSERVER]: https://discord.gg/nextcord
[PASTESERVICE]: https://paste.nextcord.dev
[ENVFILE]: ./.env.example
[AUTO_THREAD_CHANNEL_ID]: ./.env.example#L10
[STARS_CHANNEL_ID]: ./.env.example#L9
[DISCORDDOCS]: https://discord.com/developers/docs/intro
[PYTHONDOCS]: https://docs.python.org/
[NEXTCORDDOCS]: https://docs.nextcord.dev/
[NEXTCORDREPOSITORY]: https://github.com/nextcord/nextcord
[NEXTCORDREPOSITORYV3]: https://github.com/nextcord/nextcord-v3
[AUTOPASTEPY]: ./cogs/autopaste.py
[AUTOTHREADPY]: ./cogs/autothread.py
[HELPPY]: ./cogs/help.py
[DDOCSPY]: ./cogs/discorddoc.py
[DOCSPY]: ./cogs/docs.py
[STARSPY]: ./cogs/stars.py
[ETCPY]: ./cogs/etc.py
[DATABASEPY]: ./cogs/database.py
[BOTLINKPY]: ./cogs/bot_linking.py