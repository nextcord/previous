To respond more than once, you should use `interaction.send` and **not** `interaction.response.send_message`.

Discord only lets you "respond" to an interaction once. After using any method of `interaction.response`, you must use `interaction.followup.send` to send a message instead.

`interaction.send` is a shortcut to use `interaction.response.send_message` if you have not responded, or `interaction.followup.send` if you have.

```py
await interaction.response.defer()  # Optional, if you want to take more than 3 seconds to respond
...
await interaction.send("Message")
...
await interaction.send("Another message")
```

Docs: https://docs.nextcord.dev/en/latest/api.html#nextcord.Interaction.send
