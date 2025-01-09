import asyncio
import functools


def trigger_event(event: asyncio.Event):
    print("Активируется событие!")
    event.set()


async def do_work_on_event(event: asyncio.Event):
    print("Ожидаю события...")
    await event.wait()

    print("Работаю!")
    await asyncio.sleep(1)

    print("Работа закончена")
    event.clear()


async def main():
    event = asyncio.Event()
    asyncio.get_running_loop().call_later(5.0, functools.partial(trigger_event, event))
    await asyncio.gather(do_work_on_event(event), do_work_on_event(event))


asyncio.run(main())
