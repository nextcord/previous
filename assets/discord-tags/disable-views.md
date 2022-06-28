If you are using a subclassed view and have an interaction object:
```py
# we iterate over every item in the view
for child in self.children:  # self.children includes buttons and selects
    # we then set the current item to disabled
    child.disabled = True  # the disabled attribute makes the button greyed out and unusable

# we then have to tell discord about our edits
await interaction.edit(view=self)  # self would be the view if we are in the view class, in selects use `self.view` or wherever your view object is located
```
- Don't have an interaction or message? See `!!view.message`