from nextcord import ui, ButtonStyle, ChannelType, Interaction, MessageType
from nextcord.ext import commands
import nextcord


class HelpView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    # Nextcord help
    @ui.button(label="Nextcord help", style=ButtonStyle.red, custom_id="help:nextcord")
    async def nextcord_help(self, _, interaction: Interaction):
        await self.create_help_thread("Nextcord", interaction)
    @ui.button(label="D.py libs help", style=ButtonStyle.gray, custom_id="help:dpylibs")
    async def nextcord_lib_help(self, _, interaction: Interaction):
        await self.create_help_thread("Discord.py libraries", interaction)
    
    # Python
    @ui.button(label="Python help", style=ButtonStyle.green, custom_id="help:python")
    async def python_help(self, _, interaction: Interaction):
        await self.create_help_thread("Python", interaction)
    async def create_help_thread(self, name, interaction):
        thread = await interaction.channel.create_thread(name=f"{name} help ({interaction.user})", type=ChannelType.public_thread)
        await interaction.response.send_message("Created!", ephemeral=True)
        await thread.add_user(interaction.user)
        for user in interaction.guild.members:
            if 882192899519954944 in [role.id for role in user.roles]:
                await thread.add_user(user)
        await thread.send(f"Alright now that we are all here to help, what do you need help with {interaction.user.mention}?")

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_channel = 881965127031722004
        self.bot.loop.create_task(self.create_view())

    async def create_view(self):
        if getattr(self.bot, "help_view_set", False) is False:
            self.bot.help_view_set = True
            self.bot.add_view(HelpView())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.help_channel and message.type == MessageType.thread_created:
            await message.delete(delay=5)


    @commands.command()
    @commands.is_owner()
    async def help_menu(self, ctx):
        await ctx.send("Click a button to create a help thread!", view=HelpView())

def setup(bot):
    bot.add_cog(HelpCog(bot))
