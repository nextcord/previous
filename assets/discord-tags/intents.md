`on_member_*` events not working? not getting data you think you should get? You need Intents!
As of 2020-10-28, discord requires users declare what sort of information (i.e. events) they will require for their bot to operate.
This is done in the form of intents.
You can read more about intents here: https://discordpy.readthedocs.io/en/latest/intents.html

By default some intents such as members and presences are disabled as they are what is referred to as privileged.  Meaning you'll need to take some extra steps to support them.
Read up on privileged intents here: https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents
**Note: You will NEED to apply for intents after your bot is in 100 guilds. You CAN apply once it is 75 guilds**

https://media.discordapp.net/attachments/903141653655728141/926743635830112306/intents_new.png?width=1283&height=676
