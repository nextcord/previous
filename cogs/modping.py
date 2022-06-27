from typing import Optional

import nextcord
from nextcord.ext import commands


class Confirm(nextcord.ui.View):
    @nextcord.ui.button(label='Confirm', style=nextcord.ButtonStyle.green, custom_id="modpingconfirm")
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("<@&891630950813925377> has been requested by " + interaction.user.mention)


class ModPing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot
        self.ui: Optional[Confirm] = None

    @nextcord.slash_command(name="emergency", description="Pings All Mods. Only use this for reporting, not for help.",
                            guild_ids=[881118111967883295])
    async def pingmods(self, inter: nextcord.Interaction):
        await inter.send("Are you sure you want to ping all mods? This is not meant to be used for help "
                         "(there is a channel for that) but for reporting scam etc. Missuse will result in a ban",
                         ephemeral=True, view=self.ui, delete_after=180)

    @commands.Cog.listener()
    async def on_ready(self):
        self.ui = Confirm(timeout=None)
        self._bot.add_view(self.ui)


def setup(bot):
    bot.add_cog(ModPing(bot))
