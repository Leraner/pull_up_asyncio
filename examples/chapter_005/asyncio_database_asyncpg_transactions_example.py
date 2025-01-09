import asyncio
import logging

import asyncpg


async def main():
    connection = await asyncpg.connect(
        host="127.0.0.1",
        port=5432,
        user="user",
        password="password",
        database="db",
    )

    # Транзакции - включает в себя одну или несколько sql команд, которые выполняются как неделимое целое.
    # То есть в примере ниже, мы пытаемся вставить брэнд с одинаковым primary_key
    # Если мы бы делали это без транзакции, то тогда вставился бы один брэнд и после вывода ошибки в print(brands)
    # Мы бы увидели одну запись с наименованием big_brand и айди - 9999

    # Благодаря транзакции такого не случилось. Если хоть в одном sql запросе появилась ошибка, все предыдущие
    # запросы откатываются

    try:
        async with connection.transaction():
            insert_brand = "INSERT INTO brand VALUES(9999, 'big_brand')"
            await connection.execute(insert_brand)
            await connection.execute(insert_brand)
    except Exception:
        logging.exception("Ошибка выполнения транзакции")
    finally:
        query = """SELECT brand_name FROM brand WHERE brand_name LIKE 'brand%'"""
        brands = await connection.fetch(query)
        print(brands)

    await connection.close()


asyncio.run(main())
