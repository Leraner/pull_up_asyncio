import asyncio
import logging

import aiohttp

from utils import async_timed, fetch_status


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [
            asyncio.create_task(fetch_status(session, "asd://example.com")),
            asyncio.create_task(fetch_status(session, "https://example.com")),
            asyncio.create_task(fetch_status(session, "https://example.com")),
        ]

        # wait - похожа на gather, но даёт более точный контроль над ситуацией
        # У неё есть несколько параметров, который позволяют решить,
        # когда мы хотим получить результаты

        # Также она возвращает два множества,
        # задачи, которые завершились успешно или в результате исключения.
        # И задачи, которые продолжают выполняться.

        # return_when - ALL_COMPLETED, FIRST_EXCEPTION и FIRST_COMPLETED

        done, pending = await asyncio.wait(fetchers)
        # В книге написано, что исключения не возбуждается, а возвращается как результат
        # Так и есть, но исключение выскакивает в терминале

        print(f"Число завершившихся задач: {len(done)}")
        print(f"Число ожидающих задач: {len(pending)}")

        for done_task in done:
            # Тут возбуждалось исключение по книге
            # result = await done_task
            if done_task.exception() is None:
                print(done_task.result())
            else:
                logging.error("При выполнении запроса возникло исключение", exc_info=done_task.exception())


asyncio.run(main())

