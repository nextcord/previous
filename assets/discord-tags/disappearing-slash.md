**Are your slash commands disappearing?**
This isn't a nextcord bug. A common fix to this problem is regenerating your bot token *(`!!token`)* and restarting your code. 

Why this works? There is a chance that another machine is running code with your bot token and this instance is what discord sees *(having no application commands)* and ends up removing all registered commands from your main instance.

Didn't fix the issue? Ask us in <#881965127031722004>