import multiprocessing
from multiprocessing import Pool


def say_hello(name: str) -> str:
    return f"Hello, {name}"


if __name__ == "__main__":
    print(multiprocessing.cpu_count())
    # Создаём пул процессов. Без указания количество процессов, создаётся столько процессов,
    # сколько ядер у процессора с запускаемого устройства.
    with Pool() as process_pool:
        # Выполняем функцию say_hello в отдельном процессе
        hi_jeff = process_pool.apply_async(say_hello, args=("Jeff",))
        hi_john = process_pool.apply_async(say_hello, args=("John",))

        # Основной процесс не блокируется, программа идёт дальше
        # Но допустим, если первая функция будет работать за 1 с, а вторая за 10 с.
        # Тогда при получении результата программа зависнет на 10 с, а что если
        # мы хотим обрабатывать результат при поступлении,
        # как с помощью as_completed из asyncio?
        # Нам надо реализовать что-то похожее на функцию as_completed


        print(hi_jeff.get())
        print(hi_john.get())
