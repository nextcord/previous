There is now a special extension for just creating background loops:
```py
from nextcord.ext import tasks

@tasks.loop(seconds=5)
async def my_loop():
    print("Hello World")

my_loop.start()
```
The time until which the above loop will run is dependent upon human psychology, laws of energy and cosmos.
That is:
• You get bored of it
• The power goes down and your script stops working
• The universe explodes

Read more about it here: https://nextcord.readthedocs.io/en/latest/ext/tasks/
