```py
bot.dispatch("my_event", a, b, c)
```
 is heard by 
```py
a, b, c = await bot.wait_for("my_event")
```
 and
```py
@bot.event  # you can also use bot.listen() or Cog.listener()
async def on_my_event(a, b, c):
    ...
```
