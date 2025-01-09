import asyncio

import aiohttp

from utils import async_timed, fetch_status


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        urls = ["https://example.com" for _ in range(1000)]
        requests = [fetch_status(session, url) for url in urls]
        # Все запросы выполняются конкурентно
        status_codes = await asyncio.gather(*requests)
        # Запросы выполнятся в неправильном порядке, но вернутся в в том порядке,
        # в котором мы передавали в gather
        print(status_codes)

asyncio.run(main())