# Нестандартные объекты, допускающие ожидание


# __await__ - всегда должен возвращать итератор.

# Итератор - это объект, который позволяет последовательно перебирать элементы коллекции
# (например, списка, кортежа, словаря) или другой последовательности.

# То есть может вернуть генератор, что мы и делаем

# def __await__(self):
# if not self._is_finished:
# yield self
# return self.result()


class CustomFuture:
    def __init__(self):
        self._result = None
        self._is_finished = False
        self._done_callback = None

    def result(self):
        return self._result

    def is_finished(self):
        return self._is_finished

    def set_result(self, result):
        self._result = result
        self._is_finished = True
        if self._done_callback:
            self._done_callback(result)

    def add_done_callback(self, func):
        self._done_callback = func

    def __await__(self):
        if not self._is_finished:
            yield self

        return self.result()


# Создали объект CustomFuture
future = CustomFuture()

i = 0

while True:
    try:
        print("Проверяется будущий объект...")
        # Вызываем дандер метод __await__
        gen = future.__await__()
        # Пытаемся продвинуть итератор. gen.send(None) - способ запустить генератор или 
        # продолжить его выполнение с точки остановки (yield)
        gen.send(None)
        print("Будущий объект не готов")
        if i == 2:
            print("Устанавливается значение будущего объекта...")
            future.set_result(2)
        i += 1
    except StopIteration as si:
        print(f"Значение равно {si.value}")
        break
