**How to show emotions for robots:**
Custom emotes are represented internally in the following format:
`<:name:id>`
Where the name is the name of the custom emote, and the ID is the id of the custom emote. 
For example, `<:dispoon:882224126679453748>` is the name:id for <:dispoon:882224126679453748> 

When sending *standard* unicode/discord emojis, you just send the unicode character. This is handled differently from language to language, but in python, you can send  `N`, the codepoint, `uFFFF`, or just the unicode char itself: `🇦` You can get info on this by using the `=charinfo` command

You can quickly obtain the `<:name:id>` format by putting a backslash in front of the custom emoji when you put it in your client. 
Example: `\\:dispoon:` would give you the `<:name:id>` format.

When **adding reactions**, you can either send the unicode for standard emojis, or send `<:name:id>`.

**Animated emojis** are the same as above but have an `a` before the name- ie: `<a:name:id>`

**Extra:** The name isn't the important part, you can even do `<:_:id>`