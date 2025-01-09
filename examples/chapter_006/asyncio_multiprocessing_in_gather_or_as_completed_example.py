import time
import asyncio
from functools import partial
from concurrent.futures import ProcessPoolExecutor


def count(count_to: int) -> int:
    start = time.time()
    counter = 0
    while counter < count_to:
        counter += 1

    end = time.time()
    print(f"Закончен подсчет до {count_to} за время {end - start}")
    return counter


async def main():
    # Создаём пул процессов
    with ProcessPoolExecutor() as process_pool:
        # Создаём евент лупу
        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        nums = [1, 3, 5, 22, 100000000]

        # Оборачиваем функции в partial, тем самым закрепляем за ними их аргументы
        calls: list[partial[int]] = [partial(count, num) for num in nums]
        call_coros = []

        for call in calls:
            # loop.run_in_executor - принимает executor, в нашем случе это пул процессов, и список функций.
            # Возвращает этот метод объект Future, то есть объект, который ожидает в будущем результат
            call_coros.append(loop.run_in_executor(process_pool, call))

        # Передаём наш список футур (Future), и ждём выполнения всех наших функций.
        # При желании можно было бы использовать asyncio.as_completed вместо asyncio.gather.
        results = await asyncio.gather(*call_coros)

        for result in results:
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
