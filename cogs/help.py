from nextcord import ButtonStyle, ChannelType, \
    Interaction, MessageType, Thread, TextChannel, \
    Role, Message, Embed, Colour, HTTPException
from nextcord.ext import commands
from nextcord.ui import View, button, Button
from nextcord.utils import get, find
import re

NO_HELP_COGS = ()

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)

    # Nextcord library help
    @button(label="Nextcord help", style=ButtonStyle.red, custom_id="help:nextcord")
    async def nextcord_help(self, _button: Button, interaction: Interaction):
        await self.create_help_thread("Nextcord", interaction)

    # Discord.py library help
    @button(label="D.py libs help", style=ButtonStyle.gray, custom_id="help:dpylibs")
    async def nextcord_lib_help(self, _button: Button, interaction: Interaction):
        await self.create_help_thread("Discord.py libraries", interaction)

    # Python
    @button(label="Python help", style=ButtonStyle.green, custom_id="help:python")
    async def python_help(self, _button: Button, interaction: Interaction):
        await self.create_help_thread("Python", interaction)

    async def create_help_thread(self, name: str, interaction: Interaction):
        thread: Thread = await interaction.channel.create_thread(name=f"{name} help ({interaction.user})",
                                                                 type=ChannelType.public_thread)
        await interaction.response.send_message("Created!", ephemeral=True)
        await thread.add_user(interaction.user)
        log_channel: TextChannel = get(interaction.guild.channels, name='help_logs')
        await log_channel.send(f"Help thread for {name} created by {interaction.user.mention}: {thread.mention}!")
        await thread.send(
            f"<@&882192899519954944> Help needed!\nAlright now that we are all here to help, what do you need help with {interaction.user.mention}?")


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.name = "Help"
        self.description = "Commands to get help in this server."
        self.help_channel: int = 881965127031722004
        self.bot.loop.create_task(self.create_view())

    async def create_view(self):
        if getattr(self.bot, "help_view_set", False) is False:
            self.bot.help_view_set = True
            self.bot.add_view(HelpView())

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id == self.help_channel and message.type == MessageType.thread_created:
            await message.delete(delay=5)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def help_menu(self, ctx: commands.Context):
        await ctx.send("Click a button to create a help thread!", view=HelpView())

    @commands.command(name="Close", aliases=['cs'])
    async def close(self, ctx: commands.Context):
        history = ctx.channel.history(oldest_first=True, limit=1)
        if isinstance(ctx.channel, Thread) and ctx.channel.parent_id == self.help_channel:
            history_flat = await history.flatten()
            log_channel: TextChannel = get(ctx.guild.channels, name='help_logs')
            help_role: Role = find(lambda role: role.name == 'My help is bad', ctx.message.guild.roles)
            if help_role in ctx.author.roles or history_flat[0].mentions[0].id == ctx.author.id:
                await ctx.send(
                    "This thread has now been closed. Please create another thread if you wish to ask another question.")
                await ctx.channel.edit(locked=True, archived=True)
                await log_channel.send(
                    f"Help thread {ctx.channel.name} (created by {history_flat[0].mentions[0].name}) has been closed.")

    @commands.command(name='Help', aliases=['hp'],
             help="Displays the commands of me.",
             usage="help|hp (command|command alias|category|category alias)")
    async def help(self, ctx: Context, *, arg: Optional[str]):
        bot: Bot = self.bot
        icon = ctx.author.avatar.url
        help_col = Colour.random()
        try:
            if not arg:
                help = Embed(title='Category Listing',
                             description='Use `=help <category>` to get a list of commands in them!',
                             colour=help_col).set_footer(icon_url=icon,
                                                         text="Note: The 2-4 letter words in brackets are short forms of the categories. You can do =help <short form> if you wish.")
                for cog in bot.cogs.values():
                    if cog.name.lower() not in NO_HELP_COGS:
                        help.add_field(
                            value=f'[`Hover for description`](https://discord.gg/ZebatWssCB "{cog.description}")',
                            name=f'{cog.name}')
                await ctx.reply(embed=help)
            else:
                found = False
                for cog in bot.cogs.values():
                    if re.search(fr"({arg.lower()})", cog.name.lower()) and cog.name.lower() not in NO_HELP_COGS:
                        formatted_cog_name = re.sub(r"\(.+\)", "", cog.name)
                        help = Embed(title=f'{formatted_cog_name} - `Command Listing`',
                                     description=f"Use `=help <command>` for more details on a specific command\n{cog.description}\n",
                                     colour=help_col)
                        for _commands in cog.get_commands():
                            if not _commands.hidden:
                                help.add_field(name=_commands.name,
                                               value=f'[`Hover for description`](https://discord.gg/zt6j4h7ep3 "{_commands.help}")',
                                               inline=True)
                        found = True
                if not found:
                    for _command in bot.commands:
                        for alias in _command.aliases:
                            if arg.lower() in (_command.name.lower(), alias.lower()):
                                help = Embed(title=_command.name.title(),
                                             description=f"`{_command.help}`", colour=help_col)
                                help.add_field(name='Syntax:', value=f"`{_command.usage}`")
                                help.add_field(name='Aliases:', value=f"`{', '.join(_command.aliases)}`")
                                help.add_field(name='Cooldown period:',
                                               value=f"`{_command._buckets._cooldown.per}` seconds") if _command._buckets._cooldown else None
                                help.set_footer(text=
                                                """
<> - required, () - optional, | - or    
Note: You do not need to actually put <> and () around the inputs they are for understanding purposes only
\n""", icon_url=icon)
                                found = True
                if not found:
                    help = Embed(title='Error!', description=f'How do you even use "{arg}"?',
                                 color=Colour.red())
                await ctx.reply(embed=help)
        except HTTPException:
            pass


def setup(bot: commands.Bot):
    bot.add_cog(HelpCog(bot))
