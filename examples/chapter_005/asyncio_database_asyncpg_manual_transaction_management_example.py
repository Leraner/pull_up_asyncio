import asyncio

import asyncpg
from asyncpg.transaction import Transaction


async def main():
    connection = await asyncpg.connect(
        host="127.0.0.1",
        port=5432,
        user="user",
        password="password",
        database="db",
    )

    transaction: Transaction = connection.transaction()

    await transaction.start()
    # await transaction.start() - выполняет запрос к PostgreSQL, необходимый для того, чтобы начать транзакцию
    try:
        await connection.execute("INSERT INTO brand VALUES(DEFAULT, 'brand_1')")
        await connection.execute("INSERT INTO brand VALUES(DEFAULT, 'brand_2')")
    except asyncpg.PostgresError:
        print("Ошибка, транзакции отказываются!!!")
        await transaction.rollback()
    else:
        print("Ошибки нет, транзакции фиксируются")
        await transaction.commit()

    query = """SELECT brand_name FROM brand WHERE brand_name LIKE 'brand%'"""

    brands = await connection.fetch(query)
    print(brands)

    await connection.close()


asyncio.run(main())
