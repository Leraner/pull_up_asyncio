import asyncio


async def do_work(condition: asyncio.Condition):
    while True:
        print("Ожидаю блокировку условия...")
        async with condition:
            print("Блокировка захвачена, жду выполнения условия...")
            await condition.wait()
            print(
                "Условие выполнено, вновь захватываю блокировку и начинаю работать..."
            )
            await asyncio.sleep(2)

        print("Работа закончена, блокировка освобождена")


async def fire_event(condition: asyncio.Condition):
    while True:
        await asyncio.sleep(5)
        print("Перед уведомлением, захватываю блокировку условия..")

        async with condition:
            print("Блокировка захвачена, уведомляю всех исполнителей.")
            condition.notify_all()
        print("Исполнители уведомлены, освобождаю блокировку")


async def main():
    condition = asyncio.Condition()
    asyncio.create_task(fire_event(condition))

    await asyncio.gather(do_work(condition), do_work(condition))


asyncio.run(main())
