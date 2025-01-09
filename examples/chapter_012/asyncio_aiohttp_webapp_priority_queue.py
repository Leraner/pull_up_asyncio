import asyncio
from enum import IntEnum
import aiohttp
from dataclasses import field, dataclass
from aiohttp import web
from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from random import randrange


routes = web.RouteTableDef()

QUEUE_KEY = "order_queue"
TASKS_KEY = "order_tasks"


class UserType(IntEnum):
    POWER_USER = 1
    NORMAL_USER = 2


@dataclass(order=True)
class Order:
    user_type: UserType
    order_delay: int = field(compare=False)


async def process_order_worker(worker_id: int, queue: asyncio.Queue):
    while True:
        print(f"Исполнитель {worker_id}: ожидание заказа")
        order: Order = await queue.get()
        print(f"Исполнитель {worker_id}: обрабатывается заказ {order}")
        await asyncio.sleep(order.order_delay)
        print(f"Исполнитель {worker_id}: заказ {order} обработан")
        queue.task_done()


@routes.post("/order")
async def place_order(request: Request) -> Response:
    body = await request.json()
    user_type = (
        UserType.POWER_USER if body["power_user"] == "True" else UserType.NORMAL_USER
    )

    order_queue = app[QUEUE_KEY]
    await order_queue.put(Order(user_type, randrange(5)))
    return Response(body="Order placed!")


async def create_order_queue(app: Application):
    print("Creating order queue and tasks.")
    # Сделана приоритетная очередь. То есть приоритетные заказы будут обрабатываться раньше.
    # Как он понимает, какие элементы приоритетные, а какие нет?
    # Он сравнивает объекты у которых есть методы сравнения (__lt__, __gt__, __le__, __ge__, __eq__, __ne__)
    # Как он понимает, что сравниваться в @dataclass?
    # @dataclass(order=True) - говорит, что сравнение идёт по всем полям, 
    # field(compare=False) - говорит, что это поле исключается из сравнения
    queue: asyncio.Queue = asyncio.PriorityQueue(10)

    app[QUEUE_KEY] = queue
    app[TASKS_KEY] = [
        asyncio.create_task(process_order_worker(i, queue)) for i in range(5)
    ]


async def destroy_queue(app: Application):
    order_tasks: list[asyncio.Task] = app[TASKS_KEY]
    queue: asyncio.Queue = app[QUEUE_KEY]

    print("Ожидаю завершения исполнителей в очереди...")

    try:
        await asyncio.wait_for(queue.join(), timeout=10)
    finally:
        print("Обработка всех заказов завершена, отменяются задачи исполнители...")
        [task.cancel() for task in order_tasks]


app = web.Application()
app.on_startup.append(create_order_queue)
app.on_shutdown.append(destroy_queue)
app.add_routes(routes)

web.run_app(app)
