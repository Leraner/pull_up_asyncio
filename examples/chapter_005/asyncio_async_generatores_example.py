import asyncio
from utils import delay, async_timed


# Асинхронный генератор отличается от обычного генератора в питоне тем,
# что отдаёт не объекты, а генерирует сопрограммы (корутины),
# которые могут ждать получения результата с помощью await

# Асинхронный генератор не выполняет порождённые сопрограммы(корутины) конкурентно,
# а порождает и ждёт их одну за другой

async def positive_integers_async(until: int):
    for integer in range(1, until):
        await delay(integer)
        yield integer


@async_timed()
async def main():
    async_generator = positive_integers_async(3)

    print(type(async_generator))

    async for number in async_generator:
        print(f"Получено число {number}")


asyncio.run(main())
