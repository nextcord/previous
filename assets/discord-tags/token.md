{set("format", "https:\//imgur.com/7WdehGn")}
{set("regex", "`r\"([a-z0-9_-]{23,28})\\.([a-z0-9_-]{6,7})\\.([a-z0-9_-]{27,})\"`")}

{if(get(args.0), get(args.0), "Specify one of `!!token format` or `!!token regex`")}
