"""API client for Wakatime."""

import logging
from datetime import datetime, timedelta

import aiohttp

_LOGGER = logging.getLogger(__name__)

class WakatimeApiClient:
    """API client for Wakatime."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession, base_url:str="https://wakatime.com/api/v1") -> None:
        """Initialize the API client."""
        self._api_key = api_key
        self._session = session
        self._headers = {"Authorization": f"Basic {api_key}"}
        self._base_url = base_url

    async def _fetch_data(self, endpoint: str) -> dict:
        """Fetch data from the API."""
        url = f"{self._base_url}/{endpoint}"

        async with self._session.get(url, headers=self._headers) as response:
            if response.status != 200:
                _LOGGER.error(
                    "Error fetching data from Wakatime API: %s", response.status
                )
                return {}

            data = await response.json()
            return data

    async def get_user_info(self) -> dict:
        """Get user information."""
        return await self._fetch_data("users/current")

    async def get_summary(self) -> dict:
        """Get summary for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return await self._fetch_data(
            f"users/current/summaries?start={yesterday}&end={today}"
        )

    async def get_stats(self) -> dict:
        """Get stats for the current user."""
        return await self._fetch_data("users/current/stats")

    async def get_last_7_days(self) -> dict:
        """Get stats for the last 7 days."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        return await self._fetch_data(
            f"users/current/summaries?start={start_date}&end={end_date}"
        )

    async def get_all_time_since_today(self) -> dict:
        """Get all time stats."""
        return await self._fetch_data("users/current/all_time_since_today")

    async def get_categories(self) -> dict:
        """Get category information."""
        return await self._fetch_data("users/current/categories")
