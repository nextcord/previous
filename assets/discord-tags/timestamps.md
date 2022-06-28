`<t:1630145328:t>` <t:1630145328:t>
`<t:1630145328:T>` <t:1630145328:T>
`<t:1630145328:d>` <t:1630145328:d>
`<t:1630145328:D>` <t:1630145328:D>
`<t:1630145328:f>` <t:1630145328:f>
`<t:1630145328:F>` <t:1630145328:F>
`<t:1630145328:R>` <t:1630145328:R>

See `nextcord.utils.format_dt` to easily generate one with nextcord with a `datetime.datetime`:
<https://nextcord.readthedocs.io/en/latest/api.html#nextcord.utils.format_dt>

You can generate a timestamp or convert one back here: <https://www.unixtimestamp.com> or `round(datetime.datetime.timestamp())` in Python. E.g. `round(ctx.guild.created_at.timestamp())` in this server will return `1630145328`
