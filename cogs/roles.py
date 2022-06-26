from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING

from nextcord import Interaction, Member, Object, SelectOption, slash_command
from nextcord.ext.commands import Cog
from nextcord.ui import Select, View
from nextcord.utils import get

if TYPE_CHECKING:
    from nextcord.abc import Snowflake


GUILD_ID = int(getenv("GUILD_ID", 0))
UPDATES_ROLE_ID = int(getenv("UPDATES_ROLE_ID", 0))
NEWS_ROLE_ID = int(getenv("NEWS_ROLE_ID", 0))

ROLE_VALUES: dict[str, int] = {
    "updates": UPDATES_ROLE_ID,
    "news": NEWS_ROLE_ID,
}


class RolesView(View):
    def __init__(self, *, user: Member | None):
        super().__init__(timeout=None)

        self.add_item(RolesSelect(user=user))


class RolesSelect(Select["RolesView"]):
    def __init__(self, *, user: Member | None):
        # this is being invoked to add persistency
        # we only care about custom_id for the store
        # we cannot use guild.me as the bot is not ready so a guild is not available
        if user is None:
            return super().__init__(custom_id="roles:select")

        super().__init__(
            custom_id="roles:select",
            placeholder="Select your new roles",
            min_values=0,
            max_values=2,
            options=[
                SelectOption(
                    label=name.capitalize(),
                    value=name,
                    default=user.get_role(role_id) is not None,
                )
                for name, role_id in ROLE_VALUES.items()
            ],
        )

    async def callback(self, interaction: Interaction):
        assert isinstance(interaction.user, Member)

        roles: list[Snowflake] = interaction.user.roles  # type: ignore
        # since list is invariant, it cannot be a union
        # but apparently Role does not implement Snowflake, this may need a fix

        for role, role_id in ROLE_VALUES.items():
            if interaction.user.get_role(role_id) is None and role in self.values:
                # user does not have the role but wants it
                roles.append(Object(role_id))
                option = get(self.options, value=role)
                if option is not None:
                    option.default = True
            elif (
                interaction.user.get_role(role_id) is not None
                and role not in self.values
            ):
                # user has the role but does not want it
                role_ids = [r.id for r in roles]
                roles.pop(role_ids.index(role_id))
                option = get(self.options, value=role)
                if option is not None:
                    option.default = False

        await interaction.user.edit(roles=roles)

        new_roles = [value.capitalize() for value in self.values]

        await interaction.edit(
            content=f"You now have {''.join(new_roles) or 'no roles'}", view=self.view
        )


class Roles(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.create_views())

    async def create_views(self):
        if getattr(self.bot, "role_view_set", False) is False:
            self.bot.add_view(RolesView(user=None))
            # the view will accept None and only give us a select with a custom_id

            self.bot.role_view_set = True

    @slash_command(guild_ids=[GUILD_ID])
    async def roles(self, interaction: Interaction):
        assert isinstance(interaction.user, Member)
        # this shoud never assert as it cannot be used in guilds
        # it serves as a way to let the type checker know this is a member

        await interaction.send(
            "Select your new roles", view=RolesView(user=interaction.user)
        )


def setup(bot):
    bot.add_cog(Roles(bot))
