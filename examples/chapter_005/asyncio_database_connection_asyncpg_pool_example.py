import asyncpg
import asyncio
import random
from utils import async_timed

# TODO: Смотреть сразу вниз к комментариям

CREATE_BRAND_TABLE = """
CREATE TABLE IF NOT EXISTS brand( brand_id SERIAL PRIMARY KEY, brand_name TEXT NOT NULL
);"""

CREATE_PRODUCT_TABLE = """
CREATE TABLE IF NOT EXISTS product( product_id SERIAL PRIMARY KEY, product_name TEXT NOT NULL, brand_id INT NOT NULL,
FOREIGN KEY (brand_id) REFERENCES brand(brand_id) );"""


CREATE_PRODUCT_COLOR_TABLE = """
CREATE TABLE IF NOT EXISTS product_color( product_color_id SERIAL PRIMARY KEY, product_color_name TEXT NOT NULL
);"""

CREATE_PRODUCT_SIZE_TABLE = """
CREATE TABLE IF NOT EXISTS product_size( product_size_id SERIAL PRIMARY KEY, product_size_name TEXT NOT NULL
);"""

CREATE_SKU_TABLE = """
CREATE TABLE IF NOT EXISTS sku(
sku_id SERIAL PRIMARY KEY,
product_id INT NOT NULL,
product_size_id INT NOT NULL, product_color_id INT NOT NULL,
FOREIGN KEY (product_id)
REFERENCES product(product_id),
FOREIGN KEY (product_size_id)
REFERENCES product_size(product_size_id), FOREIGN KEY (product_color_id)
REFERENCES product_color(product_color_id) );"""


COLOR_INSERT = """
INSERT INTO product_color VALUES(1, 'Blue');
INSERT INTO product_color VALUES(2, 'Black');;
"""

SIZE_INSERT = """
INSERT INTO product_size VALUES(1, 'Small');
INSERT INTO product_size VALUES(2, 'Medium');
INSERT INTO product_size VALUES(3, 'Large');
"""


product_query = """
SELECT
p.product_id, p.product_name, p.brand_id,
s.sku_id, pc.product_color_name, ps.product_size_name FROM product as p
JOIN sku as s on s.product_id = p.product_id
JOIN product_color as pc on pc.product_color_id = s.product_color_id JOIN product_size as ps on ps.product_size_id = s.product_size_id WHERE p.product_id = 100"""


def load_common_words() -> list[str]:
    with open("data/words_alpha.txt", "r") as f:
        return f.readlines()


def generate_brand_names(words: list[str]) -> list[tuple[str | None]]:
    return [(words[index],) for index in random.sample(range(100), 100)]


async def insert_brands(common_words, connection) -> int:
    brands = generate_brand_names(common_words)
    insert_brands = "INSERT INTO brand VALUES(DEFAULT, $1)"
    return await connection.executemany(insert_brands, brands)


def gen_products(
    common_words: list[str],
    brand_id_start: int,
    brand_id_end: int,
    products_to_create: int,
) -> list[tuple[str, int]]:
    products = []

    for _ in range(products_to_create):
        description = [common_words[index] for index in random.sample(range(1000), 10)]
        brand_id = random.randint(brand_id_start, brand_id_end)
        products.append((" ".join(description), brand_id))

    return products


def gen_skus(
    product_id_start: int, product_id_end: int, skus_to_create: int
) -> list[tuple[int, int, int]]:
    skus = []

    for _ in range(skus_to_create):
        product_id = random.randint(product_id_start, product_id_end)
        size_id = random.randint(1, 3)
        color_id = random.randint(1, 2)
        skus.append((product_id, size_id, color_id))

    return skus


async def query_product(pool):
    async with pool.acquire() as connection:
        return await connection.execute(product_query)


@async_timed()
async def query_products_sync(pool, queries):
    return [await query_product(pool) for _ in range(queries)]


@async_timed()
async def query_products_conc(pool, queries):
    queries = [query_product(pool) for _ in range(queries)]
    return await asyncio.gather(*queries)


async def main():
    # Создание данных в базе

    # ------------------------------------------------------------

    # common_words = load_common_words()
    # connection = await asyncpg.connect(
    #     host="127.0.0.1",
    #     port=5432,
    #     user="user",
    #     password="password",
    #     database="db",
    # )
    # statements = [
    #     CREATE_BRAND_TABLE,
    #     CREATE_PRODUCT_TABLE,
    #     CREATE_PRODUCT_COLOR_TABLE,
    #     CREATE_PRODUCT_SIZE_TABLE,
    #     CREATE_SKU_TABLE,
    #     SIZE_INSERT,
    #     COLOR_INSERT,
    # ]
    # print("Создаётся база данных product...")
    # for statement in statements:
    #     status = await connection.execute(statement)
    #     print(status)
    # print("База данных создана!")

    # await connection.execute("""INSERT INTO brand VALUES(DEFAULT, 'Levis')""")
    # await connection.execute("""INSERT INTO brand VALUES(DEFAULT, 'Seven')""")
    #
    # brand_query = "SELECT brand_id, brand_name FROM brand"
    # results: list[asyncpg.Record] = await connection.fetch(brand_query)
    #
    # for brand in results:
    #     print(f'id: {brand["brand_id"]}, name: {brand["brand_name"]}')

    # # Добавление данных в базу данных

    # await insert_brands(common_words, connection)

    # product_tuples = gen_products(
    #     common_words,
    #     brand_id_start=1,
    #     brand_id_end=100,
    #     products_to_create=1000,
    # )
    #
    # await connection.executemany(
    #     "INSERT INTO product VALUES(DEFAULT, $1, $2)", product_tuples
    # )
    #
    # sku_tuples = gen_skus(
    #     product_id_start=1,
    #     product_id_end=1000,
    #     skus_to_create=100000,
    # )
    #
    # await connection.executemany(
    #     "INSERT INTO sku VALUES(DEFAULT, $1, $2, $3)", sku_tuples
    # )

    # ------------------------------------------------------------

    # Пул подключений - по сути закешированные подключения к базе данных, которые можно занять и другие таски будут
    # ждать, пока подключение вернётся, обратно в пул подключений

    # Пул нужен для того, чтобы несколько запросов в базу могли выполняться и
    # при этом не тратить много ресурсов на создание подключения к базе

    async with asyncpg.create_pool(
        host="127.0.0.1",
        port=5432,
        user="user",
        password="password",
        database="db",
        min_size=6,
        max_size=6,
    ) as pool:
        print("Creating the product database ...")

        await query_products_sync(pool, 10000)
        await query_products_conc(pool, 10000)
        """
        выполняется query_products_sync с аргументами args=(<asyncpg.pool.Pool object at 0x103c77ac0>, 10000), kwargs={}
        query_products_sync завершилась за 27.4225 с
        выполняется query_products_conc с аргументами args=(<asyncpg.pool.Pool object at 0x103c77ac0>, 10000), kwargs={}
        query_products_conc завершилась за 4.5665 с
        """


asyncio.run(main())
