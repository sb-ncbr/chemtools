import logging
import aiohttp

from fastapi import HTTPException, status


class BaseClient:
    def __init__(self, base_url: str, api_key: str, logger: logging.Logger):
        self.base_url = base_url
        self.api_key = api_key
        self.__logger = logger

    def _get_headers(self):
        return {}
        # TODO auth
        # return {
        #     "Authorization": f"Bearer
        #     {self.api_key}"
        # }

    async def _get(self, endpoint: str, params: dict = None) -> dict:
        self.__logger.info(f"Requesting GET on {endpoint} with params={params}")
        return await self._request("GET", endpoint, params=params)

    async def _post(self, endpoint: str, data: dict) -> dict:
        self.__logger.info(f"Requesting POST on {endpoint} with data={data}")
        return await self._request("POST", endpoint, data=data)

    async def _request(self, method: str, endpoint: str, data: dict | None = None, params: dict | None = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                json=data or {},
                params=params or {},
            ) as response:
                response_json = await response.json()
                if not response.ok:
                    self.__logger.error(
                        f"Request failed with status code {response.status}: {response_json.get('detail')}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response_json.get("detail")
                    )
                return response_json
