import asyncio
import hashlib
import os
import string
import time
import random
from concurrent.futures import ThreadPoolExecutor
import functools
from utils import async_timed

# Поскольку hashlib освобождает GIL, мы получаем вполне приличный выигрыш
# Всё потому, что hashlib, NumPy выполняют счётную работу на чистом C, в этот момент GIL освобождается


def random_password(length: int) -> bytes:
    ascii_lowercase = string.ascii_lowercase.encode()
    return b"".join(bytes(random.choice(ascii_lowercase)) for _ in range(length))


passwords = [random_password(10) for _ in range(10000)]


def hash(password: bytes) -> str:
    salt = os.urandom(16)
    return str(hashlib.scrypt(password, salt=salt, n=2048, p=1, r=8))


# main завершилась за 3.2680 с
@async_timed()
async def main():
    loop = asyncio.get_running_loop()
    tasks = []

    with ThreadPoolExecutor() as pool:
        for password in passwords:
            tasks.append(loop.run_in_executor(pool, functools.partial(hash, password)))

        await asyncio.gather(*tasks)


asyncio.run(main())

# 24.407660007476807
# start = time.time()
#
# for password in passwords:
#     hash(password)
#
# end = time.time()
#
# print(end - start)
