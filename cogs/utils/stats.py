import datetime
import logging
import os
from typing import Dict, Optional

from aiohttp import ClientSession, ClientResponse
from aiohttp.web_exceptions import HTTPException

log = logging.getLogger(__name__)


class StatsClient:
    """A simple interaction client for https://nextcord.koldfusion.xyz"""
    def __init__(self, session: ClientSession):
        self.session: ClientSession = session
        self.base_url: str = "https://nextcord.koldfusion.xyz/api/v1/"

        api_key: str = os.environ.get("STATS_API_KEY")
        if not api_key:
            log.warning(
                "STATS_API_KEY is a required environment variable."
                "Please contact Skelmis#9135 for the current one."
            )

            # This ensures it dies silently when used
            self.session = None

        self.base_headers: Dict[str, str] = {
            "X-API-KEY": api_key,
            "content-type": "application/json"
        }

    async def init_thread(
        self,
        thread_id: int,
        help_type: str
    ):
        """Init a thread, without actually creating the thread."""
        response: Optional[ClientResponse] = await self.try_post(
            self.route("thread/partial"),
            data={
                "thread_id": thread_id,
                "help_type": help_type,
            }
        )
        if not response:
            return None

        elif response.status == 201:
            return None

        _json = await response.json()
        log.info("Route failed: %s", _json["message"])

    async def delete_init(
        self,
        thread_id: int,
    ):
        """Deletes the init thread entry."""
        response: Optional[ClientResponse] = await self.try_delete(
            self.route(f"thread/partial/{thread_id}")
        )
        if not response:
            return None

        elif response.status == 200:
            return None

        _json = await response.json()
        log.info("Route failed: %s", _json["message"])

    async def create_thread(
        self,
        thread_id: int,
        *,
        opened_by: int,
        initial_author_id: int,
        initial_message_id: int,
        time_opened: datetime.datetime,  # Thread creation time
        initial_time_sent: datetime.datetime,  # When the first message got sent
        generic_topic: Optional[str] = "",
        initial_message_is_helper: bool = False,
    ) -> None:
        """Called when the first actual message is sent in a thread."""
        response: Optional[ClientResponse] = await self.try_post(
            self.route("thread"),
            data={
                "thread_id": thread_id,
                "time_opened": time_opened,
                "opened_by": opened_by,
                "generic_topic": generic_topic,
                "initial_message": {
                    "thread_id": thread_id,
                    "message_id": initial_message_id,
                    "author_id": initial_author_id,
                    "time_sent": initial_time_sent,
                    "is_helper": initial_message_is_helper
                }
            }
        )
        if not response:
            return None

        elif response.status == 201:
            return None

        _json = await response.json()
        log.info("Route failed: %s", _json["message"])

    async def create_message(
        self,
        *,
        thread_id: int,
        message_id: int,
        author_id: int,
        time_sent: datetime.datetime,
        is_helper: bool = False
    ) -> None:
        """Called when a message is sent within a thread."""
        response: Optional[ClientResponse] = await self.try_post(
            self.route(f"thread/{thread_id}/messages"),
            data={
                "thread_id": thread_id,
                "message_id": message_id,
                "author_id": author_id,
                "time_sent": time_sent,
                "is_helper": is_helper
            }
        )
        if not response:
            return None

        elif response.status == 201:
            return None

        _json = await response.json()
        log.info("Route failed: %s", _json["message"])

    async def update_thread(
        self,
        *,
        thread_id: int,
        closed_by: Optional[int] = None,
        generic_topic: Optional[str] = None,
        specific_topic: Optional[str] = None,
        time_closed: Optional[datetime.datetime] = None
    ) -> None:
        """Called during things like the topic command."""
        # We do this so as to *not* modify other params
        data = {}
        if closed_by:
            data["closed_by"] = closed_by

        if generic_topic:
            data["generic_topic"] = generic_topic

        if specific_topic:
            data["specific_topic"] = specific_topic

        if time_closed:
            data["time_closed"] = time_closed

        response: Optional[ClientResponse] = await self.try_patch(
            self.route(f"thread/{thread_id}"),
            data=data
        )
        if not response:
            return None

        elif response.status == 200:
            return None

        _json = await response.json()
        log.info("Route failed: %s", _json["message"])

    def route(self, route: str) -> str:
        """Create a fully formed route from an API endpoint."""
        return self.base_url + route

    async def try_get(self, url: str, **kwargs) -> Optional[ClientResponse]:
        if not self.session:
            log.warning("Session was not set before attempted usage.")
            return None

        try:
            async with self.session.get(
                url,
                headers=self.base_headers,
                **kwargs
            ) as resp:
                return resp

        except HTTPException:
            log.debug("Failed: GET %s", url)
            return None

    async def try_post(self, url: str, data: Dict, **kwargs) -> Optional[ClientResponse]:
        if not self.session:
            log.warning("Session was not set before attempted usage.")
            return None

        try:
            async with self.session.post(
                url,
                data=data,
                headers=self.base_headers,
                **kwargs
            ) as resp:
                return resp

        except HTTPException:
            log.debug("Failed: POST %s", url)
            return None

    async def try_patch(self, url: str, data: Dict, **kwargs) -> Optional[ClientResponse]:
        if not self.session:
            log.warning("Session was not set before attempted usage.")
            return None

        try:
            async with self.session.patch(
                url,
                data=data,
                headers=self.base_headers,
                **kwargs
            ) as resp:
                return resp

        except HTTPException:
            log.debug("Failed: PATCH %s", url)
            return None

    async def try_delete(self, url: str, **kwargs) -> Optional[ClientResponse]:
        if not self.session:
            log.warning("Session was not set before attempted usage.")
            return None

        try:
            async with self.session.delete(
                url,
                headers=self.base_headers,
                **kwargs
            ) as resp:
                return resp

        except HTTPException:
            log.debug("Failed: DELETE %s", url)
            return None
