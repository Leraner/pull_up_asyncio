import asyncio
import functools
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Value


map_progress: Value


def init(progress: Value):
    global map_progress
    map_progress = progress


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

    with map_progress.get_lock():
        map_progress.value += 1

    return counter


def merge_dictionaries(
    first: dict[str, int],
    second: dict[str, int],
) -> dict[str, int]:
    merged = first

    for key in second:
        merged[key] = merged.get(key, 0) + second.get(key, 0)

    return merged


async def progress_reporter(total_partition: int):
    while map_progress.value < total_partition:
        print(f"Завершено операций отображения: {map_progress.value}/{total_partition}")
        await asyncio.sleep(1)


async def main(partition_size: int):
    global map_progress

    with open("data/googlebooks-eng-all-1gram-20120701-a", encoding="utf-8") as f:
        contents = f.readlines()
        tasks = []
        loop = asyncio.get_event_loop()
        map_progress = Value('i', 0)

        start = time.time()

        with ProcessPoolExecutor(
            initializer=init, initargs=(map_progress,)
        ) as process_pool:
            total_partitions = len(contents) // partition_size

            reporter = asyncio.create_task(progress_reporter(total_partitions))

            for chunk in partition(contents, partition_size):
                tasks.append(
                    loop.run_in_executor(
                        process_pool, functools.partial(map_frequencies, chunk)
                    )
                )

            intermediate_results = await asyncio.gather(*tasks)

            await reporter

            # Время MapReduce: 17.2722 секунд
            final_result = functools.reduce(merge_dictionaries, intermediate_results)

            # Распараллеливание функции reduce - не даёт выйгрыша на macbook pro m3
            # Слишком много ресурсов тратится на накладные расходы

            print(f"Aardvark встречается {final_result['Aardvark']} раз.")

            end = time.time()

            print(f"Время MapReduce: {(end - start):.4f} секунд")


if __name__ == "__main__":
    asyncio.run(main(partition_size=60000))
