{set("base", "https://github.com/nextcord/nextcord/tree/stable/examples/application_commands/")}

{concat("<", if(args.0, concat(get("base"), args.0, ".py"), get("base")), ">")}
