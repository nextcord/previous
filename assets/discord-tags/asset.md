Asset, the class behind all images in the library has been rewritten in 2.0 to make more sense.

In this example we are using **User/Member.avatar** but it's *exactly* the same for the following:
- `User/Member.banner/default_avatar/display_avatar/guild_avatar`
- `Guild.icon/splash/discovery_splash`
- `(Partial)AppInfo.icon/cover_image`
- `Team.icon`
- `AuditLogDiff.icon`
- `GuildChannel.icon`

Now to the changes.. previously you could get the Asset from `User.avatar_url` and the hash from `User.avatar` and change the format & size with `User.avatar_url_as` well now there is only one.. `User.avatar` that now returns an instance of Asset (or None) which has the following attributes:

- `.url` - Get the full URL.
- `.key` - Get the hash.

*the following return a new instance of Asset:*
- `.with_format(format)` - Change the format.
- `.with_static_format(format)` - Change the static format only.
- `.with_size(size)` - Change the size.
- `.replace(format, static_format, size)` - Change multiple thing at once.

**Notes** (only for User/Member.avatar)
Previously `User.avatar_url` always returned something like if user didn't have a custom avatar, it would return the default one but now it doesn't do that so you need to check if it returned None and do something or... use .display_avatar this is a helper property that always returns the avatar you see *displayed* in chat.

Example
```python
@bot.command
async def avatar(ctx, member: nextcord.Member):
    # before 2.0 / Nextcord
    av = member.avatar_url_as(format="png")

    # 2.0 / Nextcord
    av = member.display_avatar.url
    # don't like png? Change it!
    av = member.display_avatar.with_static_format("jpg").url
    # ^ using .with_static_format because we still want the keep animated avatars as .gif
    # .with_format would change everything to .jpg 
    await ctx.send(av)
```

Oh also the default format is `png` (if not animated else `gif`) instead of `webp` now.
