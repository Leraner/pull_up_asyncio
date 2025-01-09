import asyncio

import aiohttp

from utils import async_timed, fetch_status


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [
            fetch_status(session, "https://example.com", 1),
            fetch_status(session, "https://example.com", 3),
            fetch_status(session, "https://example.com", 10),
        ]

        # Недостатки as_completed:
        # 1) Мы получаем результат по мере поступления, но не может понять откуда этот результат
        # 2) Если возбуждается исключение, то задачи продолжают работать в фоновом режиме
        #   А если мы захотим их снять, то нам трудно понять, какие из задачи,
        #   который мы передавали ешё работают

        for finished_task in asyncio.as_completed(fetchers, timeout=2):
            try:
                result = await finished_task
                print(result)
            except asyncio.TimeoutError:
                print("Произошёл timeout")

        for task in asyncio.all_tasks():
            print(task)


asyncio.run(main())
