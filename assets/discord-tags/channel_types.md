**Want users to select a channel of a specific type?** Use the `channel_types` kwarg in `SlashOption` like so,
```py
# we'll need these...
from nextcord import ChannelType, SlashOption
from nextcord.abc import GuildChannel 

# base param
channel: GuildChannel # typehinting as GuildChannel is required for any of this work
# now let's assign a SlashOption to it and specify the channel_types kwarg...
channel: GuildChannel = SlashOption(channel_types=[...])
# channel_types takes a list, a list of ChannelType's
# for example, if you only want users to choose a voice channel, you can use the following:
channel: GuildChannel = SlashOption(channel_types=[ChannelType.voice])
# all text channels?
channel: GuildChannel = SlashOption(channel_types=[ChannelType.text, ChannelType.public_thread])
# ChannelType.public_thread is inclused because that is also a type of text channel
# but you aren't forced to put that in

# extra: a description is required per option but the lib got you covered, 
# you can however still specify one if you want, like so,
# channel: GuildChannel = SlashOption(description="Choose a channel.", channel_types=[...])
```
See all channel types here: <https://nextcord.readthedocs.io/en/latest/api.html#nextcord.ChannelType>
