import asyncio
import random
import string
import time
from asyncio.subprocess import Process


# Скачать gpg - https://gnupg.org/download/

# Не тестировал, доверюсь наслово, что это всё работает.

# Смысл: конкурентное выполнение подпроцессов.

# Создаём 100 сопрограмм, которые выполняются конкурентно внутри себя создают 100 подпроцессов.

# Сами подпроцессы выполняются не параллельно, потому что они выполняются в одном потоке, в одном процессе.
# Но управление подпроцессами происходит неблокирующим способом.

# То есть тут мало того, что мы создали кучу процессов,
# пожирающих ресурсы, так эти процессы еще и блокируются при доступе к разделяемому состоянию.

# Вот отличный случай воспользоваться семафором.
# Поскольку программа ограничена быстродействием процессора, имеет смысл добавить семафор,
# чтобы число процессов не превышало число доступных ядер.


async def encrypt(text: str) -> bytes:
    program = [
        "gpg",
        "-c",
        "--batch",
        "--passphrase",
        "3ncryptm3",
        "--cipher-algo",
        "TWOFISH",
    ]

    process: Process = await asyncio.create_subprocess_exec(
        *program,
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )

    stdout, _ = await process.communicate(text.encode())

    return stdout


async def main():
    text_list = [
        "".join(random.choice(string.ascii_letters) for _ in range(1000))
        for _ in range(100)
    ]

    s = time.time()

    tasks = [asyncio.create_task(encrypt(text)) for text in text_list]

    encrypted_text = await asyncio.gather(*tasks)

    e = time.time()

    print(f"Время работы {e - s}")
    print(encrypted_text)


asyncio.run(main())
