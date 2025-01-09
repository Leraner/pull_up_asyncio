import asyncio
from utils import delay

# Ни в коем случае не делать lock = asyncio.Lock - глобальной переменной
# Иначе все сопрограммы упадут в ошибку о том, что есть несколько евент луп
# Всегда передавать её в качестве параметра в функцию

# Это происходит из-за того, что asyncio.Lock объект имеет параметр loop, 
# и если он пустой, то захочет создать event loop.


async def a(lock: asyncio.Lock):
    # Можно блокировки ещё использовать так, вместо контекстных менеджеров
    # Но предпочтительнее использовать контекстные менеджеры
    
    # await lock.acquire()
    # try:
    #     # Do something
    #     pass
    # finally:
    #     lock.release()

    print("Сопрограмма а ждёт возможности захватить блокировку")
    async with lock:
        print("Сопрограмма а находится в критической секции")
        await delay(2)
    
    print("Сопрограмма a освободила блокировку")


async def b(lock: asyncio.Lock):
    print("Сопрограмма b ждёт возможности захватить блокировку")
    async with lock:
        print("Сопрограмма b находится в критической секции")
        await delay(2)
    
    print("Сопрограмма b освободила блокировку")


async def main():
    lock = asyncio.Lock()
    await asyncio.gather(a(lock), b(lock))

asyncio.run(main())