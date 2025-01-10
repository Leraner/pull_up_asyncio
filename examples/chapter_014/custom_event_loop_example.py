import functools
import selectors


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


class EventLoop:
    _tasks_to_run: list[CustomTask] = []

    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.current_result = None

    def _register_socket_to_read(self, sock, callback):
        future = CustomFuture()

        try:
            self.selector.get_key(sock)
        except KeyError:
            sock.setblocking(False)
            self.selector.register(
                sock, selectors.EVENT_READ, functools.partial(callback, future)
            )
        else:
            self.selector.modify(
                sock, selectors.EVENT_READ, functools.partial(callback, future)
            )

            return future

    def _set_current_result(self, result):
        self.current_result = result

    async def sock_recv(self, sock):
        print("Регистрируется сокет для прослушивания данных...")
        return await self._register_socket_to_read(sock, self.recieved_data)

    async def sock_accept(self, sock):
        print("Регистрируется сокет для приема подключений...")
        return await self._register_socket_to_read(sock, self.accept_connection)

    def sock_close(self, sock):
        self.selector.unregister(sock)
        sock.close()

    def register_task(self, task):
        self._tasks_to_run.append(task)

    def recieved_data(self, sock, future):
        data = sock.recv(1024)
        future.set_result(data)

    def accept_connection(self, sock, future):
        result = sock.accept()
        future.set_result(result)

    def run(self, coro):
        self.current_result = coro.send(None)

        while True:
            try:
                if isinstance(self.current_result, CustomFuture):
                    self.current_result.add_done_callback(self._set_current_result)

                    if self.current_result.result() is not None:
                        self.current_result = coro.send(self.current_result.result())

                    else:
                        self.current_result = coro.send(self.current_result)
            except StopIteration as si:
                return si.value

            for task in self._tasks_to_run:
                task.step()

            self._tasks_to_run = [
                task for task in self._tasks_to_run if not task.is_finished()
            ]

            events = self.selector.select()

            print("В селекторе есть событие, обрабатывается...")

            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
