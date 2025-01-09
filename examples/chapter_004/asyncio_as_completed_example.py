import asyncio

import aiohttp

from utils import async_timed, fetch_status

# Получение результатов задач по мере их выполнения


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [
            fetch_status(session, "https://example.com", 1),
            fetch_status(session, "https://example.com", 3),
            fetch_status(session, "https://example.com", 10),
        ]

        for finished_task in asyncio.as_completed(fetchers):
            print(await finished_task)


asyncio.run(main())
