from typing import ClassVar

from nextcord import Message, TextChannel

from nextcord.ext.commands import Bot, Cog
from nextcord.ext.tasks import loop


class H(Cog):
    """Run a task loop to update a channel with the current h's said in the server."""
    
    H_CHANNEL_ID: ClassVar[int] = 123

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.to_add: int = 0

    @Cog.listener("on_message")
    async def listen_to_h_messages(self, message: Message) -> None:
        """Listens for messages containing 'h' and adds 1 to the counter"""
        if message.content.lower() == "h":
            self.to_add += 1

    @loop(minutes=6)
    async def update_h(self) -> None:
        """Loop to check and update counter"""
        previous_count: int = int(self.channel.name.split(": ")[1]) 
        new_count: int = previous_count + self.to_add
        self.to_add = 0
        # update channel name if it has changed
        if new_count != previous_count:
            await self.channel.edit(name=f"h: {new_count}")

    @update_h.before_loop
    async def before_update_h(self) -> None:
        """Before the loop starts, get the channel"""
        await self.bot.wait_until_ready()
        self.channel: TextChannel = self.bot.get_channel(self.H_CHANNEL_ID)  # type: ignore


def setup(bot: Bot) -> None:
    bot.add_cog(H(bot))