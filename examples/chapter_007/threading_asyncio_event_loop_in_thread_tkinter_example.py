import asyncio
from threading import Thread
from concurrent.futures import Future
from typing import Callable

from aiohttp import ClientSession

from queue import Queue
from tkinter import Tk, Label, Entry, ttk


# call_soon_threadsafe - принимает функцию (не корутину) и потокобезопасным образом планирует её выполнение
# на следующей итерации цикла
# run_coroutine_threadsafe - принимает сопрограмму, потокобезопасным образом подает ее для выполнения и
# сразу же возвращает будущий объект, который позволит получить доступ к результату сопрограммы.
# Важно, что этот будущий объект является не будущим объектом asyncio, а
# экземпляром класса future из модуля concurrent.futures. Объясняется это тем,
# что будущие объекты asyncio потоконебезопасны, в отличие от будущих объектов из concurrent.futures.
# Впрочем, этот класс future обладает той же функциональностью, что и будущие объекты из модуля asyncio.


class StressTest:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        url: str,
        total_requests: int,
        callback: Callable[[int, int], None],
    ):
        self.completed_requests: int = 0
        self._load_test_future: Future | None = None
        self._loop = loop
        self._url = url
        self._total_requests = total_requests
        self._callback = callback
        self._refresh_rate = total_requests // 100

    def start(self):
        # Отправляем нашу корутину _make_requests в нашу лупу, которая крутится в отдельном потоке
        future = asyncio.run_coroutine_threadsafe(self._make_requests(), self._loop)
        self._load_test_future = future

    def cancel(self):
        if self._load_test_future:
            # Планируем потокобезопасное выполнение функции cancel
            # у нашей Future из concurrent.futures
            self._loop.call_soon_threadsafe(self._load_test_future.cancel)

    async def _get_url(self, session, url: str):
        try:
            await session.get(url)
        except Exception as e:
            print(e)

        self.completed_requests += 1

        if (
            self.completed_requests % self._refresh_rate == 0
            or self.completed_requests == self._refresh_rate
        ):
            self._callback(self.completed_requests, self._total_requests)

    async def _make_requests(self):
        async with ClientSession() as session:
            reqs = [
                self._get_url(session, self._url) for _ in range(self._total_requests)
            ]
            await asyncio.gather(*reqs)


class LoadTester(Tk):
    def __init__(self, loop, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self._queue = Queue()
        self._refresh_ms = 25

        self._loop = loop
        self._load_test: StressTest | None = None
        self.title("URL Requester")

        self._url_label = Label(self, text="URL")
        self._url_label.grid(column=0, row=0)

        self._url_field = Entry(self, width=10)
        self._url_field.grid(column=1, row=0)

        self._request_label = Label(self, text="Number of requests:")
        self._request_label.grid(column=0, row=1)

        self._request_field = Entry(self, width=10)
        self._request_field.grid(column=1, row=1)

        self._submit = ttk.Button(self, text="Submit", command=self._start)
        self._submit.grid(column=2, row=1)

        self._pb_label = Label(self, text="Progress:")
        self._pb_label.grid(column=0, row=3)

        self._pb = ttk.Progressbar(
            self, orient="horizontal", length=200, mode="determinate"
        )
        self._pb.grid(column=1, row=3, columnspan=2)

    def _update_bar(self, pct: int):
        if pct == 100:
            self._load_test = None
            self._submit["text"] = "Submit"
        else:
            self._pb["value"] = pct
            self.after(self._refresh_ms, self._poll_queue)

    def _queue_update(self, completed_requests: int, total_requests: int):
        self._queue.put(int(completed_requests / total_requests * 100))

    def _poll_queue(self):
        if not self._queue.empty():
            percent_complete = self._queue.get()
            self._update_bar(percent_complete)
        else:
            if self._load_test:
                self.after(self._refresh_ms, self._poll_queue)

    def _start(self):
        if self._load_test is None:
            self._submit["text"] = "Cancel"
            # Создаётся наш экземпляр класса StressTest.
            # В него добавляется наша евент лупа, которая крутится в отдельном потоке.
            # И callback функция _queue_update, которая будет обновлять наш прогресс бар.
            test = StressTest(
                self._loop,
                self._url_field.get(),
                int(self._request_field.get()),
                self._queue_update,
            )
            self.after(self._refresh_ms, self._poll_queue)
            test.start()
            self._load_test = test
        else:
            self._load_test.cancel()
            self._load_test = None
            self._pb["value"] = 0
            self._submit["text"] = "Submit"


class ThreadedEventLoop(Thread):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self._loop = loop
        self.daemon = True

    def run(self):
        self._loop.run_forever()


loop = asyncio.new_event_loop()

# Создали евент лупу, отправили её крутиться в отдельном треде
asyncio_thread = ThreadedEventLoop(loop)
asyncio_thread.start()

app = LoadTester(loop)
app.mainloop()
