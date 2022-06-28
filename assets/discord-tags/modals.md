{set("base", "https://github.com/nextcord/nextcord/tree/master/examples/modals/")}

{concat("<", if(args.0, concat(get("base"), args.0, ".py"), get("base")), ">")}
