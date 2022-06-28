Slash and application commands use checks from `nextcord.ext.application_checks` and not `nextcord.ext.commands`

```py
from nextcord.ext import application_checks

@bot.slash_command()
@application_checks.has_permissions(manage_messages=True)
async def test(interaction: Interaction):
    await interaction.response.send_message('You can manage messages.')
```

See the docs here:
https://docs.nextcord.dev/en/stable/ext/application_checks/index.html#module-nextcord.ext.application_checks
