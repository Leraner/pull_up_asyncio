import asyncio


# Блокировка это частный случай семафора с пределом - 1
# Семафор можно захватывать не один раз. Грубо говоря это штука, 
# которая ограничивает одновременное выполнение 
# определенного количества (которое задаётся семафору) сопрограмм.


async def operation(semaphore: asyncio.Semaphore):
    print("Жду возможности захватить семафор...")
    async with semaphore:
        print("Семафор захвачен")
        await asyncio.sleep(2)

    print("Семафор освобожден")


async def main():
    semaphoer = asyncio.Semaphore(value=2)
    await asyncio.gather(*[operation(semaphore=semaphoer) for _ in range(4)])


asyncio.run(main())
