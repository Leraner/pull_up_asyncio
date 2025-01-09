import functools
import time
from typing import Callable, Any


def async_timed():
    """
    Декоратор для подсчета времени выполнения асинхронных функций
    """
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f"выполняется {func.__name__} с аргументами args={args}, kwargs={kwargs}")
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f"{func.__name__} завершилась за {total:.4f} с")

        return wrapped

    return wrapper
