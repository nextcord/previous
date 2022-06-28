```py
# Creating a `Playing ` type activity.
playing_example = nextcord.Game(name="a game")

# Creating a `Streaming ` type activity.
streaming_example = nextcord.Streaming(name="My Stream", url=my_twitch_url)

# Creating a `Listening to ` type activity.
listening_example = nextcord.Activity(type=nextcord.ActivityType.listening, name="a song")

# Creating a `Competing in ` type activity.
competing_example = nextcord.Activity(type=nextcord.ActivityType.competing, name="a battle")

# Creating a `Watching ` type activity.
watching_example = nextcord.Activity(type=nextcord.ActivityType.watching, name="a movie")

# Any of these example can be used to set the bot's current activity, either upon Client construction or later on using the Client.change_presence method.

# e.g 1
client = nextcord.Client(activity=listening_example, ...)

# e.g 2
await client.change_presence(activity=watching_example)

# The above two examples will work the same if you are using commands.Bot instead of nextcord.Client as well.
```

ActivityType enum: <https://nextcord.readthedocs.io/en/latest/api.html#discord.ActivityType>
Activity data class: <https://nextcord.readthedocs.io/en/latest/api.html#activity>
