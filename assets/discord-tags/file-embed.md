```py

f = nextcord.File("some_file_path", filename="image.png")
e = nextcord.Embed()
e.set_image(url="attachment://image.png")
await messagable.send(file=f, embed=e)
```

Note that the filename in the File constructor and the filename in the URL must match, and must be alphanumeric.
