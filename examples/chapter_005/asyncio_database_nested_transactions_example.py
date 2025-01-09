import asyncpg
import asyncio
import random
import logging
from utils import async_timed


async def main():
    connection = await asyncpg.connect(
        host="127.0.0.1",
        port=5432,
        user="user",
        password="password",
        database="db",
    )

    # Вложенные транзакции работают как точки сохранения (asyncpg поддерживает их благодаря PostgreSQL).
    # Если транзакция упала, и она была во вложенной, то
    # во внешней транзакции не выполнятся только те sql запросы, которые были во внутренней

    async with connection.transaction():
        await connection.execute("INSERT INTO brand VALUES(DEFAULT, 'my_new_brand')")

        try:
            async with connection.transaction():
                await connection.execute("INSERT INTO product_color VALUES(1, 'black')")
        except Exception as ex:
            logging.exception(
                "Ошибка при вставке цвета товара игнорируется", exc_info=ex
            )

    result = await connection.fetch("SELECT * from product_color")
    print(result)

    await connection.close()


asyncio.run(main())
