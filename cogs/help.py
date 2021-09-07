from nextcord import ui, ButtonStyle, ChannelType, Interaction, MessageType
from nextcord.ext import commands
import nextcord


class HelpView(nextcord.ui.View):
    
    @nextcord.ui.button(label='Nextcord Help?', style=nextcord.ButtonStyle.green)
    async def nextcord_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        view = Confirmation('Nextcord')
        await interaction.response.send_message('Are you really sure you want to make a help thread?', view=view, ephemeral=True)
        
    
    @nextcord.ui.button(label='Discord.py libs Help?', style=nextcord.ButtonStyle.blurple)
    async def dpy(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        view = Confirmation('D.py')
        await interaction.response.send_message('Are you really sure you want to make a help thread?.', view=view, ephemeral=True)
        
    
    @nextcord.ui.button(label='Python Help?', style=nextcord.ButtonStyle.red)
    async def python(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        view = Confirmation('Python')
        await interaction.response.send_message('Are you really sure you want to make a help thread?', view=view, ephemeral=True)
        
   
class Confirmation(nextcord.ui.View): 
    
    def __init__(self, channel_name):
        super().__init__()
        self.name = channel_name       
        
    @nextcord.ui.button(label='Yes', style=nextcord.ButtonStyle.success)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.create_help_thread(name=self.name, interaction=interaction)
        await interaction.response.send_message('Created the thread', ephemeral=True)
        self.stop() 
        
    @nextcord.ui.button(label='No', style=nextcord.ButtonStyle.danger)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop() 
    
    
    async def create_help_thread(self, name, interaction):
        thread = await interaction.channel.create_thread(name=f"{name} help ({interaction.user})", type=ChannelType.public_thread)
        await thread.add_user(interaction.user)
        log_channel = nextcord.utils.get(interaction.guild.channels, name='help_logs')
        await log_channel.send(f"Help thread for {name} created by {interaction.user.mention}: {thread.mention}!")
        await thread.send(f"<@&882192899519954944> Help needed!\nAlright now that we are all here to help, what do you need help with {interaction.user.mention}?")
        
        
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

    @commands.command()
    async def close(self, ctx):
        history = ctx.channel.history(oldest_first=True, limit=1)
        history_flat = await history.flatten()
        log_channel = nextcord.utils.get(ctx.guild.channels, name='help_logs')
        help_role = nextcord.utils.find(lambda r: r.name == 'My help is bad', ctx.message.guild.roles)
        if help_role in ctx.author.roles or history_flat[0].mentions[0].id == ctx.author.id:
            if isinstance(ctx.channel, nextcord.Thread) and ctx.channel.parent_id == self.help_channel:
                await ctx.send("This thread has now been closed. Please create another thread if you wish to ask another question.")
                await ctx.channel.edit(locked=True, archived=True)
                await log_channel.send(f"Help thread {ctx.channel.name} (created by {history_flat[0].mentions[0].name}) has been closed.")


def setup(bot):
    bot.add_cog(HelpCog(bot))
