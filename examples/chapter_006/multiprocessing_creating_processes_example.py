import time
from multiprocessing import Process


def count(count_to: int) -> int:
    start = time.time()

    counter = 0

    while counter < count_to:
        counter += 1

    end = time.time()

    print(f"Закончен подсчёт до {count_to} за время {end - start}")
    return counter


if __name__ == "__main__":
    start_time = time.time()

    to_one_hundred_million = Process(target=count, args=(100000000,))
    to_two_hundred_million = Process(target=count, args=(200000000,))

    to_one_hundred_million.start()
    to_two_hundred_million.start()

    to_one_hundred_million.join()
    to_two_hundred_million.join()

    # Недостатки:
    # Мы в этой реализации никак не можем получить результат работы процессов,
    # из-за разделенной памяти процессов.

    # << Этот API годится для простых случаев, но, очевидно, не работает,
    # если нужно получать возвращенное функцией значение или обрабатывать результаты по мере готовности.
    # По счастью, проблему позволяют решить пулы процессов. >>

    # Эту проблему решает пул процессов

    end_time = time.time()

    print(f"Полное время работы {end_time - start_time}")
