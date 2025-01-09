from multiprocessing import Process, Value, Array


# Процесс имеет свою собственную память.
# Но можно и создать общую память для процессов.
# Например, для хранения прогресса.
#
# Код ниже создаёт переменную integer и integer_array в общей памяти для процессов.
# В библиотеке multiprocessing поддерживается только два вида разделяемых данных - Значение и Массив.
#
# !!!!!
# Если два процесса будут работать с одной и той же областью памяти (переменной в памяти),
# то может появиться состояние гонки. Когда в один и тот же момент времени оба процесса читают значение из памяти,
# (Например, оба прочли, что integer = 0), изменяют это значение (Оба добавили к нему по единице), и в результате
# в памяти будет записано то значение, которое было записано последним процессом, то-есть результат будет
# некорректным (Ожидаемый результат 2, в итоге будет число 1)
# !!!!!

def increment_value(shared_int: Value):
    shared_int.value += 1


def increment_array(shared_array: Array):
    for index, integer in enumerate(shared_array):
        shared_array[index] = integer + 1


if __name__ == "__main__":
    # type and value of var
    integer = Value("i", 0)

    integer_array = Array("i", [0, 0])

    procs = [
        Process(target=increment_value, args=(integer,)),
        Process(target=increment_array, args=(integer_array,)),
    ]

    [p.start() for p in procs]
    [p.join() for p in procs]

    print(integer.value)
    print(integer_array[:])
