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


class CustomTask(CustomFuture):
    def __init__(self, coro, loop):
        # Получаем сопрограмму
        self._coro = coro
        # Получаем наш цикл событий (Event loop)
        self._loop = loop
        self._current_result = None
        self._task_state = None
        # Регистрируем в цикле событий нашу задачу
        loop.register_task(self)

    def step(self):
        # Вызывается наша сопрограмма, выполняется ровно на один шаг и
        # результат выполнения записывается
        try:
            if self._task_state is None:
                # Если состояние задачи - None,
                # то запускаем сопрограмму первый раз с помощью send(None)
                self._task_state = self._coro.send(None)

            if isinstance(self._task_state, CustomFuture):
                # Если сопрограмма отдаёт какой-то результат типа CustomFuture,
                # то вызываем callback функцию
                self._task_state.add_done_callback(self._future_done)

        except StopIteration as si:
            self.set_result(si.value)

    def _future_done(self, result):
        # Когда будущий объект будет готов, отправить результат сопрограмме
        self._current_result = result

        try:
            self._task_state = self._coro.send(self._current_result)
        except StopIteration as si:
            self.set_result(si.value)
