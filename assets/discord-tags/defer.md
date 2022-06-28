Discord expects you to respond in 3 seconds, you can extend that by deferring and then sending followup in the next 15 minutes.

`await interaction.response.defer()`
This will show the "... bot is thinking" message to the user

**Note:** this will be public by default, though you can make it hidden as you do on any other response.

Sums up to the following:
```py
# function definition
await interaction.response.defer()
# do whatever
await interaction.followup.send(...)
```