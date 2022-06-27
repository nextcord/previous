from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING

from nextcord import Interaction, Member, Object, SelectOption, slash_command
from nextcord.ext.commands import Cog
from nextcord.ui import Select, View
from nextcord.utils import get

if TYPE_CHECKING:
    from nextcord.abc import Snowflake

GUILD_ID = int(getenv("GUILD_ID"))
ASSIGNABLE_ROLE_IDS = {int(r) for r in getenv("ASSIGNABLE_ROLE_IDS").split(",")}


class RolesView(View):
    def __init__(self, *, member: Member):
        super().__init__(timeout=None)

        self.add_item(RolesSelect(member=member))


class RolesSelect(Select["RolesView"]):
    def __init__(self, *, member: Member):
        super().__init__(
            placeholder="Select your new roles",
            min_values=0,
            max_values=len(ASSIGNABLE_ROLE_IDS),
            options=[
                SelectOption(
                    label=member.guild.get_role(role_id).name,  # type: ignore
                    value=str(role_id),
                    default=member.get_role(role_id) is not None,
                )
                for role_id in ASSIGNABLE_ROLE_IDS
            ],
        )

    async def callback(self, interaction: Interaction):
        assert isinstance(interaction.user, Member)

        roles: list[Snowflake] = interaction.user.roles  # type: ignore
        # since list is invariant, it cannot be a union
        # but apparently Role does not implement Snowflake, this may need a fix

        for role_id in ASSIGNABLE_ROLE_IDS:
            if (
                interaction.user.get_role(role_id) is None
                and str(role_id) in self.values
            ):
                # user does not have the role but wants it
                roles.append(Object(role_id))
                option = get(self.options, value=str(role_id))
                if option is not None:
                    option.default = True
            elif (
                interaction.user.get_role(role_id) is not None
                and str(role_id) not in self.values
            ):
                # user has the role but does not want it
                role_ids = [r.id for r in roles]
                roles.pop(role_ids.index(role_id))
                option = get(self.options, value=str(role_id))
                if option is not None:
                    option.default = False

        await interaction.user.edit(roles=roles)

        new_roles = [
            interaction.guild.get_role(int(value)).name  # type: ignore
            for value in self.values
        ]

        await interaction.edit(
            content=f"You now have {', '.join(new_roles) or 'no roles'}", view=self.view
        )


class Roles(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[GUILD_ID], description="Self assign roles")
    async def roles(self, interaction: Interaction):
        assert isinstance(interaction.user, Member)
        # this shoud never assert as it cannot be used in guilds
        # it serves as a way to let the type checker know this is a member

        await interaction.send(
            "Select your new roles",
            view=RolesView(member=interaction.user),
            ephemeral=True,
        )


def setup(bot):
    bot.add_cog(Roles(bot))
