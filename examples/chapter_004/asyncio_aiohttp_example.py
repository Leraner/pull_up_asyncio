import asyncio
import aiohttp

from utils import async_timed


async def fetch_status(session: aiohttp.ClientSession, url: str) -> int:
    async with session.get(url) as result:
        return result.status


@async_timed()
async def main():
    # Ограничение на создание кол-ва подключений у ClientSession - 100 подключений.
    # Чтобы увеличить это количество, нужно создать экземпляр класса TCPConnector и
    # передать аргументом в ClientSession
    async with aiohttp.ClientSession() as session:
        # Создание сессии - ресурсоёмкий процесс, желательно это делать один раз в приложении
        url = "https://www.example.com"
        status = await fetch_status(session, url)
        print(f"Состояние для {url} было равно {status}")


asyncio.run(main())
