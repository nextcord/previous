{set("base", "https://github.com/nextcord/nextcord/tree/stable/examples/")}

{set("category", if(or(eq(args.0, "views"), eq(args.0, "slash"), eq(args.0, "modals")), args.0, ""))}
{set("category", if(eq(args.0, "application_commands"), "slash", get("category")))}

{if(get("category"), tag(get("category"), args.1), concat("<", if(args.0, concat(get("base"), args.0, ".py"), get("base")), ">"))}
