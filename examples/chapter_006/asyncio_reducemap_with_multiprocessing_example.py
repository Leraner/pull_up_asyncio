import asyncio
import functools
import time
from concurrent.futures import ProcessPoolExecutor

freqs = {}


# Какой чанк сделать по размеру для метода ReduceMap?
# Так тяжело сказать, главное чтобы порция была не слишком большой и не слишком маленькой,
# потому что созданные порции сериализуются в формат pickle, а потом обратно десериализуются.
# Слишком большая порция - тоже плохо, потому что это не даст нам в полной мере использовать ресурсы
# нашего компьютера.

# Можно написать свою функцию, которая будет рассчитывать какое количество данных брать за чанк.
# Считается просто: сделать примерно так, чтобы одновременно были загружены все ядра компьютера.
# << или разработайте эвристический алгоритм определения правильного размера >>


def partition(data: list, chunk_size: int) -> list:
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


def map_frequencies(chunk: list[str]) -> dict[str, int]:
    counter = {}

    for line in chunk:
        word, _, count, _ = line.split("\t")
        if counter.get(word):
            counter[word] = counter[word] + int(count)
        else:
            counter[word] = int(count)

    return counter


def merge_dictionaries(
    first: dict[str, int],
    second: dict[str, int],
) -> dict[str, int]:
    merged = first

    for key in second:
        merged[key] = merged.get(key, 0) + second.get(key, 0)

    return merged


async def reduce(loop, pool, counters, chunk_size) -> dict[str, int]:
    chunks: list[list[dict]] = list(partition(counters, chunk_size))
    reducers = []

    while len(chunks[0]) > 1:
        for chunk in chunks:
            reducer = functools.partial(functools.reduce, merge_dictionaries, chunk)
            reducers.append(loop.run_in_executor(pool, reducer))

        reducer_chunks = await asyncio.gather(*reducers)

        chunks = list(partition(reducer_chunks, chunk_size))
        reducers.clear()

    return chunks[0][0]


async def main(partition_size: int):
    with open("data/googlebooks-eng-all-1gram-20120701-a", encoding="utf-8") as f:
        contents = f.readlines()
        tasks = []
        loop = asyncio.get_event_loop()

        start = time.time()

        with ProcessPoolExecutor() as process_pool:
            for chunk in partition(contents, partition_size):
                tasks.append(
                    loop.run_in_executor(
                        process_pool, functools.partial(map_frequencies, chunk)
                    )
                )

            intermediate_results = await asyncio.gather(*tasks)

            # Время MapReduce: 18.5618 секунд
            final_result = await reduce(loop, process_pool, intermediate_results, 500)

            # Время MapReduce: 17.2722 секунд
            # final_result = functools.reduce(merge_dictionaries, intermediate_results)

            # Распараллеливание функции reduce - не даёт выйгрыша на macbook pro m3
            # Слишком много ресурсов тратится на накладные расходы

            print(f"Aardvark встречается {final_result['Aardvark']} раз.")

            end = time.time()

            print(f"Время MapReduce: {(end - start):.4f} секунд")


if __name__ == "__main__":
    asyncio.run(main(partition_size=60000))


# 22.5961 секунд

# with open("data/googlebooks-eng-all-1gram-20120701-a", encoding="utf-8") as f:
#     lines = f.readlines()
#
#     start = time.time()
#
#     for line in lines:
#         data = line.split("\t")
#         word = data[0]
#
#         count = int(data[2])
#
#         freqs[word] = freqs.get(word, 0) + 1
#
#     end = time.time()
#
# print(f"{end - start :.4f}")
