{set("base", "https://github.com/nextcord/nextcord/tree/stable/examples/views/")}
{set("file", "https://github.com/nextcord/nextcord/blob/stable/examples/views/")}

{concat("<", if(args.0, concat(get("file"), args.0, ".py"), get("base")), ">")}
