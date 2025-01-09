import asyncio
import aiohttp

from utils import async_timed


async def fetch_status(session: aiohttp.ClientSession, url: str) -> int:
    ten_millis = aiohttp.ClientTimeout(total=.01)
    # Переопределяем таймаут для нашего get запроса. Теперь для этого запроса таймаут
    # составляет 10 мс
    # Если время ожидания превысит 10 мс, то выведется ошибка asyncio.TimeoutError
    async with session.get(url, timeout=ten_millis) as result:
        return result.status


@async_timed()
async def main():
    # Ограничение на создание кол-ва подключений у ClientSession - 100 подключений.
    # Чтобы увеличить это количество, нужно создать экземпляр класса TCPConnector и
    # передать аргументом в ClientSession
    session_timeout = aiohttp.ClientTimeout(total=1, connect=.1)
    # Таймаут на уровне клиентского сеанса, полный таймаут равен 1 секунде, а таймаут для
    # установления соединения - 100 мс
    # Если время ожидания превысит 1 с, то выведется ошибка asyncio.TimeoutError
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        url = "https://www.example.com"
        status = await fetch_status(session, url)
        print(f"Состояние для {url} было равно {status}")


asyncio.run(main())
