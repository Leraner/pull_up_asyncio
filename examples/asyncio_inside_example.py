import asyncio
import time
import typing
from queue import Queue

event_loop = Queue()


_PENDING = "PENDING"
_FINISHED = "FINISHED"
_CANCELED = "CANCELED"


class Future:
    def __init__(self):
        self._state = _PENDING
        self._result = None
        self._exception = None

    def done(self):
        if self._state != _PENDING:
            return True
        return False

    def set_exception(self, exception: Exception):
        self._exception = exception
        self._state = _CANCELED

    def set_result(self, result: typing.Any):
        self._result = result
        self._state = _FINISHED

    def result(self):
        if self.done():
            if self._exception:
                return self._exception
            return self._result
        raise Exception("Task does not done")

    def __await__(self):
        while not self.done():
            yield self

        return self.result()


class Task(Future):
    def __init__(self, generator):
        self.iter = generator
        super().__init__()

    def cancel(self):
        # Func for canceling task
        pass

    def wait_for(self):
        pass


def create_task(generator):
    task = Task(generator)
    event_loop.put(task)

    return task


def _sleep(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        yield


async def sleep(seconds):
    task = create_task(_sleep(seconds))
    result = await task
    return result


async def test():
    return "123"


async def main():
    result = create_task(test())
    print(await result)


def run(main):
    event_loop.put(Task(main))

    while not event_loop.empty():
        task = event_loop.get()
        try:
            task.iter.send(None)
        except StopIteration as e:
            task.set_result(e.value)
        except Exception as e:
            task.set_exception(e)
        else:
            event_loop.put(task)


run(sleep(1))
run(main())
