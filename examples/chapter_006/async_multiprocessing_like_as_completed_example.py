import time
from concurrent.futures import ProcessPoolExecutor


def count(count_to: int) -> int:
    start = time.time()
    counter = 0
    while counter < count_to:
        counter += 1

    end = time.time()
    print(f"Закончен подсчет до {count_to} за время {end - start}")
    return counter


if __name__ == "__main__":
    # Количество процессов, равно количеству ядер на машине,
    # на которой запускается этот код
    # Всё ровно так же как и при multiprocessing (Pool)
    with ProcessPoolExecutor() as process_pool:
        numbers = [1, 3, 5, 22, 100000000]

        for result in process_pool.map(count, numbers):
            # Хоть и кажется, что эта реализация работает как asyncio.as_completed, но
            # это не совсем так. Порядок выполнения процессов такой же, как и входящие данные.
            # То есть, если бы сначала было число 100000000, то мы бы ждали 2 с, а только потом
            # появилась бы возможность напечатать остальные результаты.
            # Получается process_pool.map - не такая гибкая штука как asyncio.as_completed
            print(result)
