```py
@bot.message_command(name="Custom Name", guild_ids=[TEST_GUILD_ID_HERE])
async def my_message_command(interaction, message):
    await interaction.send(f"Here's the text in that message! {message.content}", ephemeral=True)
```