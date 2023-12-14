import asyncio
import aiohttp
import async_timeout
import socket
from urllib.parse import unquote
from typing import Any, Optional
from .exceptions import PubAirError, APIConnectionError


class PubAirAPIBase:
    def __init__(
        self,
        auth_key: str = None,
        base_url: str = None,
        session: aiohttp.ClientSession = None,
    ):
        self._auth_key = unquote(auth_key)
        self._base_url = base_url
        self._session = session
        self._return_type = "json"

    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
    ) -> Any:
        if self._session is None:
            self._session = aiohttp.ClientSession()

        try:
            # Network Request
            response = await self._session.request(method, url, params=params)
            response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise APIConnectionError(
                "Timeout occurred while connecting to Open API Server"
            ) from exception
        except (
            aiohttp.ClientError,
            aiohttp.ClientResponseError,
            socket.gaierror,
        ) as exception:
            raise APIConnectionError(
                "Error occurred while connecting to Open API Server"
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            raise PubAirError(
                "Unexpected response from the Open API Server",
                {"Content-Type": content_type, "response": text},
            )
        return await response.json()

    async def close(self) -> None:
        """Close open client session."""
        if self._session:
            await self._session.close()

    async def __aenter__(self) -> "PubAirAPIBase":
        """Asnyc enter."""
        return self

    async def __aexit__(self, *exec_info) -> None:
        """Async exit."""
        await self.close()