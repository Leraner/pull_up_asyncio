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
        hi_jeff = process_pool.apply(say_hello, args=("Jeff",))
        hi_john = process_pool.apply(say_hello, args=("John",))

        # Есть проблема, функция apply блокирует дальнейшее выполнение кода.
        # То есть, если бы функция say_hello, работала бы 10 с, то весь код работал бы 20 с.
        # Эта проблема решается с помощью функции apply_async
        print(hi_jeff)
        print(hi_john)
