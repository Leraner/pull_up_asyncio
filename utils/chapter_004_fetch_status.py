import aiohttp
from .delay_functions import delay


async def fetch_status(
    session: aiohttp.ClientSession, url: str, delay_seconds: int | None = None
) -> int:
    if delay_seconds is not None:
        await delay(delay_seconds)

    async with session.get(url) as result:
        return result.status
