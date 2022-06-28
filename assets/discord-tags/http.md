{set("type_specified", or(eq(args.0, "dog"), eq(args.0, "cat"), eq(args.0, "duck")))}
{set("type", if(get("type_specified"), args.0, "cat"))}
{set("input", if(get("type_specified"), args.1, args.0))}
{set("input", if(gte(get("input"), 600), "404", get("input")))}
{set("site", if(eq(get("type"), "dog"), "https://http.dog/", "https://http.cat/" ))}
{set("site", if(eq(get("type"), "duck"), " https://random-d.uk/api/http/", get("site")))}
{if(get("input"), concat(get("site"), get("input"), ".jpg"), get("site"))}
