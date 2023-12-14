import aiohttp
import asyncio

ST_API_KEY="55c5450b-62c3-40ac-8b44-9882c220bcbd"
ST_BASE_URL="https://api.smartthings.com/v1/devices/a06bcc7c-7b61-4fea-54a5-7990b5706702/states"

class AirMonitorClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def make_authenticated_get_request(self, endpoint):
        url = f'{self.base_url}/{endpoint}'
        async with self.session.get(url, headers=self.headers) as response:
            return await response.json()

async def main():
    base_url = "https://api.smartthings.com/v1/devices/a06bcc7c-7b61-4fea-54a5-7990b5706702"
    token = "55c5450b-62c3-40ac-8b44-9882c220bcbd"

    async with AirMonitorClient(base_url, token) as client:
        # GET 요청 예제
        response_get = await client.make_authenticated_get_request('states')
        print('GET Response:', response_get)

if __name__ == "__main__":
    asyncio.run(main())
