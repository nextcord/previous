from nextcord import ui, ButtonStyle, ChannelType,\
    Interaction, MessageType, Thread, TextChannel,Role
from nextcord.ext.commands import Context, Cog, Bot,command, is_owner
from nextcord.ui import View, button, Button
from nextcord.utils import get, find


class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)

    # Nextcord help
    @button(label="Nextcord help", style=ButtonStyle.red, custom_id="help:nextcord")
    async def nextcord_help(self, _button: Button, interaction: Interaction):
        await self.create_help_thread("Nextcord", interaction)

    @button(label="D.py libs help", style=ButtonStyle.gray, custom_id="help:dpylibs")
    async def nextcord_lib_help(self, _button: Button, interaction: Interaction):
        await self.create_help_thread("Discord.py libraries", interaction)
    
    # Python
    @button(label="Python help", style=ButtonStyle.green, custom_id="help:python")
    async def python_help(self, _button: Button, interaction: Interaction):
        await self.create_help_thread("Python", interaction)

    async def create_help_thread(self, name: str, interaction: Interaction):
        thread: Thread = await interaction.channel.create_thread(name=f"{name} help ({interaction.user})", type=ChannelType.public_thread)
        await interaction.response.send_message("Created!", ephemeral=True)
        await thread.add_user(interaction.user)
        log_channel: TextChannel = get(interaction.guild.channels, name='help_logs')
        await log_channel.send(f"Help thread for {name} created by {interaction.user.mention}: {thread.mention}!")
        await thread.send(f"<@&882192899519954944> Help needed!\nAlright now that we are all here to help, what do you need help with {interaction.user.mention}?")

class HelpCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.help_channel: int = 881965127031722004
        self.bot.loop.create_task(self.create_view())

    async def create_view(self):
        if getattr(self.bot, "help_view_set", False) is False:
            self.bot.help_view_set = True
            self.bot.add_view(HelpView())

    @Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.help_channel and message.type == MessageType.thread_created:
            await message.delete(delay=5)

    @command()
    @is_owner()
    async def help_menu(self, ctx: Context):
        await ctx.send("Click a button to create a help thread!", view=HelpView())

    @command()
    async def close(self, ctx: Context):
        history = ctx.channel.history(oldest_first=True, limit=1)
        if isinstance(ctx.channel, Thread) and ctx.channel.parent_id == self.help_channel:
            history_flat = await history.flatten()
            log_channel: TextChannel = get(ctx.guild.channels, name='help_logs')
            help_role: Role = find(lambda role: role.name == 'My help is bad', ctx.message.guild.roles)
            if help_role in ctx.author.roles or history_flat[0].mentions[0].id == ctx.author.id:
                await ctx.send("This thread has now been closed. Please create another thread if you wish to ask another question.")
                await ctx.channel.edit(locked=True, archived=True)
                await log_channel.send(f"Help thread {ctx.channel.name} (created by {history_flat[0].mentions[0].name}) has been closed.")


def setup(bot: Bot):
    bot.add_cog(HelpCog(bot))
