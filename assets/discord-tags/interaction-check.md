```py
# define our view class
class MyView(nextcord.ui.View):
    # `__init__` is called when we initialise an object
    def __init__(self, ctx, **kwargs):  # pass our `Context` object and anything else we want to propegate to the `ui.View`'s `__init__`
        super().__init__(**kwargs)  # call `View.__init__` to create a proper view
        self.ctx = ctx  # set the `ctx` attribute to use later

    # this is called before every interaction, it has to return a bool (like command checks) on if the clicker may use the component
    async def interaction_check(self, interaction):  # we get an interaction for info
       return self.ctx.author == interaction.user  # `True` if the user is the same as ctx.author, `False` otherwise
       # do ***anything you like here*** like send an ephemeral error message or anything else

...

# create the view object (in a command usually)
view = MyView(ctx)  # pass the `Context` object for info on the target user
```
Docs: https://docs.nextcord.dev/en/stable/api.html#nextcord.ui.View.interaction_check
