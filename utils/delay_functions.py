import asyncio


async def delay(delay_seconds: int) -> int:
    print(f"засыпаю на {delay_seconds}")
    await asyncio.sleep(delay_seconds)
    print(f"поспал {delay_seconds}")
    return delay_seconds
