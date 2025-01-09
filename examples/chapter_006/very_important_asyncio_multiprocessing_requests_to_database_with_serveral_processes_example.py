import asyncio

import asyncpg

from utils import async_timed
from concurrent.futures import ProcessPoolExecutor


# В asyncio_database_connection_asyncpg_pool_example мы посмотрели насколько быстро обрабатываются
# 10 тысяч запросов в базу с помощью асинхронного подхода. Результат: query_products_conc завершилась за 4.5665 с

# В примере ниже мы добавили процессы к обработке 50 тысяч запросов в базу. Результат: main завершилась за 2.4953 с

# !!!!!!
# Что мы сделали? Увеличили пропускную способность нашего приложения.
# Мы увеличили пропускную способность не ввода вывода, а количество результатов, которые обрабатывались одновременно.

# Для каждого чанка из 10 тысяч запросов
# создавался свой процесс, в котором эти 10 тысяч запросов обрабатывались, как и при асинхронном подходе.


#                         Рабочий процесс со своим циклом событий и пулом подключений
#                       /                                                               \
# Родительский процесс  - Рабочий процесс со своим циклом событий и пулом подключений    ----> База данных
#                       \                                                               /
#                         Рабочий процесс со своим циклом событий и пулом подключений
# !!!!!!

# Хотя код в основном занят отправкой запросов базе данных, то есть вводом выводом,
# но он всё равно потребляет много процессорного времени, потому что надо обрабатывать результаты,
# которые были получены от PostgreSQL, а для этого нужен процессор.




product_query = """
SELECT p.product_id, p.product_name, p.brand_id, s.sku_id, pc.product_color_name,
ps.product_size_name
FROM product as p
JOIN sku as s on s.product_id = p.product_id
JOIN product_color as pc on pc.product_color_id = s.product_color_id JOIN product_size as ps on ps.product_size_id = s.product_size_id WHERE p.product_id = 100"""


async def query_product(pool):
    async with pool.acquire() as connection:
        return await connection.fetchrow(product_query)


@async_timed()
async def query_products_conc(pool, queries):
    queries = [query_product(pool) for _ in range(queries)]
    return await asyncio.gather(*queries)


def run_in_new_event_loop(num_queries: int):
    async def run_queries():
        async with asyncpg.create_pool(
            host="127.0.0.1",
            port=5432,
            user="user",
            password="password",
            database="db",
            min_size=6,
            max_size=6,
        ) as pool:
            return await query_products_conc(pool, num_queries)

    results = [dict(result) for result in asyncio.run(run_queries())]

    return results


@async_timed()
async def main():
    loop = asyncio.get_running_loop()
    pool = ProcessPoolExecutor()

    tasks = [loop.run_in_executor(pool, run_in_new_event_loop, 10000) for _ in range(5)]
    all_results = await asyncio.gather(*tasks)

    total_queries = sum([len(result) for result in all_results])

    print(f"Извлечено товаров из базы данных: {total_queries}.")


if __name__ == "__main__":
    asyncio.run(main())
