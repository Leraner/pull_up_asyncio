import asyncio
import functools

import requests
from concurrent.futures import ThreadPoolExecutor
from utils import async_timed

# По умолчанию количество потоков в пуле задаётся вот так min(32, os.cpu_count() + 4).
# Создавать и обслуживать потоки - дорого по ресурсам и времени.
# Часто имеет смысл создать немного больше потоков, чем имеется ядер,
# если предполагается использовать их для ввода-вывода.
# Например, на 8-ядерной машине, согласно приведенной выше формуле, будет создано 14 потоков.
# Конкурентно смогут работать только 8 потоков, а остальные будут ждать завершения ввода-вывода.


# Спорограммы всё равно быстрее для таких действий, а всё потому, что потоки обходятся дороже, потому что
# создаются на уровне операционной системы. К тому же у контекстного переключения потоков на уровне операционной системы
# тоже есть цена. Сохранение и восстановление состояния потока при переключении съедает часть выигрыша, полученного от
# использования потоков.


def get_status_code(url: str) -> int:
    response = requests.get(url)
    return response.status_code


# При max_workers = 1000, Выполнение запросов завершено за 5.6801 с
# С asyncio и max_workers = 1000 - main завершилась за 5.0649 с
# !!!!!!
# Этот подход не дает никакого выигрыша по сравнению с использованием пула потоков без asyncio,
# но, пока мы ждем await asyncio.gather, может выполняться другой код.
# !!!!!!

# (!!!!!!)
# Код можно упростить вот так, потому что в loop.run_in_executor, параметр executor
# по дефолту ставится, как ThreadPoolExecutor, если он не был переназначен с помощью loop.set_default_executor
# (!!!!!!)


@async_timed()
async def main():
    loop = asyncio.get_event_loop()
    urls = ["https://example.com" for _ in range(1000)]

    result = await asyncio.gather(
        *[
            loop.run_in_executor(None, functools.partial(get_status_code, url))
            for url in urls
        ]
    )

    print(result)


asyncio.run(main())


# Выполнение запросов завершено за 29.7169 с

# urls = ["https://example.com" for _ in range(1000)]
#
# for url in urls:
#     print(get_status_code(url))
#
# end = time.time()
#
# print(f"Выполнение запросов завершено за {end - start:.4f} с")
# Выполнение запросов завершено за 484.6426 с
