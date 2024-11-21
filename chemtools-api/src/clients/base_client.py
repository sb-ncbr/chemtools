import logging
import httpx

from fastapi import HTTPException, status


class BaseClient:
    def __init__(self, base_url: str, api_key: str, logger: logging.Logger, client: httpx.AsyncClient):
        self.base_url = base_url
        self.api_key = api_key
        self.__logger = logger
        self.__client = client

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

    async def _post(self, endpoint: str, data: dict, files: list | None = None) -> dict:
        self.__logger.info(f"Requesting POST on {endpoint} with data={data}, count(files)={len(files or [])}")
        return await self._request("POST", endpoint, data=data, files=files)

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), **kwargs)
            response_json = response.json()
            if not response.is_success:
                self.__logger.error(
                    f"Request failed with status code {response.status_code}: {response_json.get('detail')}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response_json.get("detail")
                )
            return response_json
