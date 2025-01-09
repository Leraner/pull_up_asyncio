from threading import Lock, RLock

# Тут наглядно показано, чем отличается Lock от RLock.

# Мы делаем две блокировки, одна в методе indices_of, потому что если там не делать блокировку,
# то поток может изменять self._inner_list во выполнения метода indices_of, что может привести к
# неправильному результату.

# И делаем блокировку в find_and_replace, по тем же причинам. Если использовать Lock, то в функции
# indices_of мы будем ожидать пока не освободиться блокировка,
# но этого никогда не случится, поэтому программа просто зависнет


class IntListThreadsafe:
    def __init__(self, wrapped_list: list[int]):
        # self._lock = Lock()
        self._lock = RLock()
        self._inner_list = wrapped_list

    def indices_of(self, to_find: int) -> list[int]:
        with self._lock:
            enumerator = enumerate(self._inner_list)
            return [index for index, value in enumerator if value == to_find]

    def find_and_replace(self, to_replace: int, replace_with: int) -> None:
        with self._lock:
            indices = self.indices_of(to_replace)
            for index in indices:
                self._inner_list[index] = replace_with


thread_safe_list = IntListThreadsafe([1, 2, 1, 2, 1])
thread_safe_list.find_and_replace(1, 2)
