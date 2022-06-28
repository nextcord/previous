get_x and utils.get both return None if they can't find anything matching. 
Common causes include:
• Not subscribed to the relevant intent. See `!!intents`
• Wrong key
    ◦ Remember, IDs are ints, not strings
    ◦ If you're trying to copy an emoji ID, right-clicking the emoji in a message will copy message ID
• Bot not logged in, and trying to grab objects from cache
• Bot cannot "see" the object. 
    ◦ It has to be on the server, share a server with the member, etc
    ◦ If you're sharded on separate processes, each process will only have objects for that shard. 
• Objects retuned by fetch_x will not have a populated cache.
