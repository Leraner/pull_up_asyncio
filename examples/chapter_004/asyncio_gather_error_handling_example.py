import asyncio

import aiohttp

from utils import async_timed, fetch_status


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        urls = ["asd://example.com" for _ in range(1000)]
        requests = [fetch_status(session, url) for url in urls]
        # Все запросы выполняются конкурентно
        status_codes = await asyncio.gather(*requests, return_exceptions=True)
        # return_exceptions=True - возвращает ошибки в списке результатов
        # return_exceptions=False - вызывает ошибка на месте, где стоит await у задачи

        # Запросы выполнятся в неправильном порядке, но вернутся в в том порядке,
        # в котором мы передавали в gather
        print(status_codes)

asyncio.run(main())