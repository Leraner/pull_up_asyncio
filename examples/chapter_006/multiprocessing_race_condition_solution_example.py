from multiprocessing import Process, Value, Array


# Состояние гонки можно исправить с помощью блокировок.
# То есть мы помечаем места, где будет работать только один процесс.
# (Блокируем в места параллельную работу нескольких процессов)

# В multiprocessing есть get_lock.acquire() - место начала блокировки,
# get_lock.release() - место конца блокировки


def increment_value(shared_int: Value):
    # вместо acquire, release, можно использовать контекстный менеджер
    with shared_int.get_lock():
        shared_int.value += 1

    # shared_int.get_lock().acquire()
    # shared_int.value += 1
    # shared_int.get_lock().release()


if __name__ == "__main__":
    # type and value of var
    integer = Value("i", 0)

    procs = [
        Process(target=increment_value, args=(integer,)),
        Process(target=increment_value, args=(integer,)),
    ]

    [p.start() for p in procs]
    [p.join() for p in procs]

    print(integer.value)
