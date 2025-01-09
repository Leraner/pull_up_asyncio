import asyncio
import asyncpg


async def main():
    connection = await asyncpg.connect(
        host="127.0.0.1",
        port=5432,
        user="user",
        password="password",
        database="db",
    )

    query = "SELECT product_id, product_name FROM product"

    # Достаём по 50 записей (при доставании с помощью курсора, дефолтное значение 50) из базы
    # и проходимся по ним с помощью асинхронного генератора

    # async with connection.transaction():
    #     async for product in connection.cursor(query):
    #         await asyncio.sleep(1)
    #         print(product)

    # Передвигаем курсор на 500 записей вперед.
    # Получаем следующие 100 записей после передвижения на 500 записей вперед.
    # Мы не можем задать количество выбираемых записей за одно обращение к базе

    async with connection.transaction():
        cursor = await connection.cursor(query)
        await cursor.forward(500)
        products = await cursor.fetch(100)
        for product in products:
            print(product)

    await connection.close()


asyncio.run(main())
