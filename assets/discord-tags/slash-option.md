**Want to add a description to your command ~~arguments~~ options?** Or another name than it's defined as?
```py
from nextcord import Member, Interaction

# base function
async def hello(
    interaction: Interaction, # ignore this one 
    custom_text: str,
    member: Member
):
    ...
```
Let's add a description to both options (custom_text, member)
```py
from nextcord import SlashOption

async def hello(
    interaction: Interaction, # ignore this one
    custom_text: str = SlashOption(
        description="What should it say?"
    ),
    member: Member = SlashOption(
        description="Who should it mention?"
    )
):
    ....
```
There is also a `name` keyword argument, let's use it on the custom_text option:
```py
custom_text: str = SlashOption(
    name="text",
    description="What should it say?"
)
```
Now it will show `text` to the user instead of `custom_text`, we still access the input from `custom_text`.


**Note:** a description is required per option, at discord side, but the lib sets it to "No description provided" for you.

**Limits:**
name: max 32 characters and must be all lowercased
choices: max 25 choices
description: max 100 characters
