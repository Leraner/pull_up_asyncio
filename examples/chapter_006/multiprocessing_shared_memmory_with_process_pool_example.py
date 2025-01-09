import asyncio
from multiprocessing import Value
from concurrent.futures import ProcessPoolExecutor


# Чтобы разделить данные в пуле процессов (То есть создать общую память для пула процессов)
# Нам нужно поместить наш счётчик в глобальную переменную и каким-то образом дать знать процессам,
# что в глобальной переменной (shared_counter) лежит разделяемый объект (объект, который находится в
# общей памяти у процессов).
#
# Для того чтобы процессам дать знать, что в shared_counter лежит разделяемый объект, создадим функцию (init),
# которая будет процессам подсказывать. Добавим функцию в параметр initializer, это значит, что при создании
# нового процесса, эта функция будет выполняться самая первая
"""
Функция init будет вызываться для каждого процесса, созданного в пуле, 
и правильно инициализировать переменную shared_counter значением, 
созданным в сопрограмме main. 
Вы спросите: «А к чему все эти хлопоты? 
Не проще ли инициализировать глобальную переменную shared_counter: Value = Value('d', 0), 
а не оставлять ее пустой?» 
Нет, так нельзя, потому что при создании каждого процесса будет по новой выполняться создающий его скрипт. 
А значит, каждый процесс будет начинаться с выполнения предложения shared_counter: Value = Value('d', 0), 
и если у нас есть 100 процессов, то мы получим 100 значений shared_counter, равных 0, 
что приведет к странному поведению.
"""

shared_counter: Value


def init(counter: Value):
    global shared_counter
    shared_counter = counter


def increment():
    with shared_counter.get_lock():
        shared_counter.value += 1


async def main():
    counter = Value("d", 0)
    with ProcessPoolExecutor(initializer=init, initargs=(counter,)) as pool:

        await asyncio.get_running_loop().run_in_executor(pool, increment)
        print(counter.value)


if __name__ == "__main__":
    asyncio.run(main())
