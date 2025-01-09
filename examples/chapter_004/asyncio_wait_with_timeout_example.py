import asyncio
import aiohttp

from utils import async_timed, fetch_status


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        pending = [
            asyncio.create_task(fetch_status(session, "https://example.com")),
            asyncio.create_task(fetch_status(session, "https://example.com")),
            asyncio.create_task(fetch_status(session, "https://example.com", 3)),
        ]

        # wait - похожа на gather, но даёт более точный контроль над ситуацией
        # У неё есть несколько параметров, который позволяют решить,
        # когда мы хотим получить результаты

        # Также она возвращает два множества,
        # задачи, которые завершились успешно или в результате исключения.
        # И задачи, которые продолжают выполняться.

        done, pending = await asyncio.wait(pending, timeout=1)
        # !!!!!
        # С использованием timeout, asyncio.wait возвращает список завершившихся задач,
        # задач которые ждут завершения, НО asyncio.wait их не останавливает в отличие
        # от as_completed и gather
        # !!!!!

        print(f"Число завершившихся задач: {len(done)}")
        print(f"Число ожидающих задач: {len(pending)}")

        for done_task in done:
            print(await done_task)


asyncio.run(main())
