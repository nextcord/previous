```py
# Our view instance
view = MyView()

# channel.send message 
view.message = await channel.send(..., view=view)

# Interaction message
await interaction.response.send_message(..., view=view)
view.message = await interaction.original_message()
```
After that you can use `self.message` in `on_timeout` (*or somewhere else you don't have access to `interaction.message`*) to edit it.

**Interaction.original_message:**
https://docs.nextcord.dev/en/stable/api.html#nextcord.Interaction.original_message
