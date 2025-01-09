import asyncio
from utils import delay

# Принудительный запуск итерации цикла событий

# Вызов await asyncio.sleep(0) после создания каждой задачи принудительно запускает следующую итерацию цикла

"""
--- Без asyncio.sleep(0) ---
К задачам применяется gather:
засыпаю на 1
засыпаю на 2
поспал 1
поспал 2
--- С asyncio.sleep(0) ---
засыпаю на 1
засыпаю на 2
К задачам применяется gather:
поспал 1
поспал 2
"""


async def create_tasks_no_sleep():
    task1 = asyncio.create_task(delay(1)) 
    task2 = asyncio.create_task(delay(2))

    print('К задачам применяется gather:')
    await asyncio.gather(task1, task2)


async def create_tasks_sleep():
    task1 = asyncio.create_task(delay(1))
    await asyncio.sleep(0)
    task2 = asyncio.create_task(delay(2))
    await asyncio.sleep(0)

    print('К задачам применяется gather:')
    await asyncio.gather(task1, task2)

async def main():
    print('--- Без asyncio.sleep(0) ---')
    await create_tasks_no_sleep()

    print('--- С asyncio.sleep(0) ---')
    await create_tasks_sleep()

asyncio.run(main())