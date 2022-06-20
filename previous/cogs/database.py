from __future__ import annotations

from base64 import b64decode
from json import loads
from os import environ as env
from typing import TYPE_CHECKING

from nextcord.ext import commands


if TYPE_CHECKING:
    from previous.__main__ import Previous


class Database(commands.Cog):
    def __init__(self, bot: Previous):
        self.bot = bot
        self.api_base: str = env["CONSUL_ADDR"]
        self.consul_token: str = env["CONSUL_TOKEN"]

    async def get(self, key: str) -> dict | None:
        r = await self.bot.session.get(
            f"{self.api_base}/v1/kv/previous/{key}",
            headers={"X-Consul-Token": self.consul_token},
        )

        if r.status == 404:
            return None

        data = await r.json()
        value = data[0]["Value"]

        return loads(b64decode(value).decode("utf-8"))

    async def set(self, key: str, value: dict) -> None:
        r = await self.bot.session.put(
            f"{self.api_base}/v1/kv/previous/{key}",
            headers={"X-Consul-Token": self.consul_token},
            json=value,
        )
        r.raise_for_status()

    async def delete(self, key: str) -> None:
        r = await self.bot.session.delete(
            f"{self.api_base}/v1/kv/previous/{key}",
            headers={"X-Consul-Token": self.consul_token},
        )
        r.raise_for_status()

    async def list(self, prefix: str) -> dict | None:
        r = await self.bot.session.get(
            f"{self.api_base}/v1/kv/previous/{prefix}",
            headers={"X-Consul-Token": self.consul_token},
            params={"recurse": "true"},
        )

        if r.status == 404:
            return None

        r.raise_for_status()

        data = await r.json()
        return {
            item["Key"].removeprefix("previous/"): loads(
                b64decode(item["Value"]).decode("utf-8")
            )
            for item in data
        }


def setup(bot: Previous):
    bot.add_cog(Database(bot))
