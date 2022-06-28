**So you enabled the `message_content` intent but commands are still not working?**
Common reasons for that are the following:

**1.** You did __not__ read the tag above and instead copy-pasted the code or didn't look at it.
Please actually read the code and comments with it to solve this.
**2.** You misspelled the **i**ntent**s=** kwarg in `commands.Bot()`.
**3.** You assumed the `messages` intent is the same thing.
It's not, `messages` intent is to get messages at all and is enabled by default, `message_content` controls the following fields on the Message object: `.content, .embeds, .attachments, .components`.
