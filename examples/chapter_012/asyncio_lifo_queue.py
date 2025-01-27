import asyncio
from dataclasses import dataclass, field


@dataclass(order=True)
class WorkItem:
    priority: int
    order: int
    data: str = field(compare=False)


async def worker(queue: asyncio.Queue):
    while not queue.empty():
        work_item: WorkItem = await queue.get()
        print(f"Обрабатывается элемент {work_item}")
        queue.task_done()



async def main():
    # Last In First Out -  LIFO
    lifo_queue = asyncio.LifoQueue()

    work_items = [
        WorkItem(3, 1, "Lowest priority first"),
        WorkItem(3, 2, "Lowest priority second"),
        WorkItem(3, 3, "Lowest priority third"),
        WorkItem(2, 4, "Medium priority"),
        WorkItem(1, 5, "Hight priority"),
    ]

    worker_tasks = asyncio.create_task(worker(lifo_queue))

    for work in work_items:
        lifo_queue.put_nowait(work)

    await asyncio.gather(lifo_queue.join(), worker_tasks)


asyncio.run(main())
