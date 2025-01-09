import asyncio
import aiohttp

from utils import async_timed, fetch_status


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [
            asyncio.create_task(fetch_status(session, "https://example.com", 1)),
            asyncio.create_task(fetch_status(session, "https://example.com", 2)),
            asyncio.create_task(fetch_status(session, "https://example.com", 3)),
        ]

        # wait - похожа на gather, но даёт более точный контроль над ситуацией
        # У неё есть несколько параметров, который позволяют решить,
        # когда мы хотим получить результаты

        # Также она возвращает два множества,
        # задачи, которые завершились успешно или в результате исключения.
        # И задачи, которые продолжают выполняться.

        # return_when - ALL_COMPLETED, FIRST_EXCEPTION и FIRST_COMPLETED

        done, pending = await asyncio.wait(fetchers, return_when=asyncio.FIRST_COMPLETED)
        # Возвращает первую задачу, которая выполнилась

        print(f"Число завершившихся задач: {len(done)}")
        print(f"Число ожидающих задач: {len(pending)}")

        for done_task in done:
            print(await done_task)

asyncio.run(main())

