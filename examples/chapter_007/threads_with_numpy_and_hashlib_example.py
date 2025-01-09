import numpy as np
import time
import asyncio
from utils import async_timed


# Вычисляем среднее по всем строкам в матрице.

# !!!!!!!!!!!!!!!!
# Надо иметь в виду, что до экспериментов с многопоточностью или многопроцессностью код с применением NumPy
# должен быть максимально векторизован. Это означает, что нужно избегать циклов Python
# или функций типа apply_along_axis, которые просто скрывают цикл.
# Часто NumPy позволяет достичь гораздо большего, если перенести максимум вычислений на уровень библиотеки.

data_points = 4000000000
rows = 50
columns = int(data_points / rows)


matrix = np.arange(data_points).reshape(rows, columns)


# ---- THREADS ------
def mean_for_row(arr, row):
    return np.mean(arr[row])


# main завершилась за 5.2953 с
@async_timed()
async def main():
    tasks = [asyncio.to_thread(mean_for_row, matrix, i) for i in range(rows)]
    await asyncio.gather(*tasks)


asyncio.run(main())


# s = time.time()

# Удобная функция mean, которая помогает это сделать без цикла. axis = 1, говорит,
# что среднее надо вычислить по всем строкам
# res = np.mean(matrix, axis=1)

# e = time.time()
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 44.648926973342896
# print(e - s)
