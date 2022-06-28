The usage of * while taking an argument

```python
@bot.command()
async def foo(ctx, *args):
    ...
# Invoking "?foo one two" will return a tuple like object
# args = ('one', 'two')

@bot.command()
async def bar(ctx, *, args):
    ...

# Invoking "?bar one two " will return all arguments as a string
# args = 'one two'
```
