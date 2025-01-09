import asyncio
from random import randrange


# TODO: Кассир, покупатель - ожидание добавления в очередь 
# и ожидение получения из очереди


class Product:
    def __init__(self, name: str, checkout_time: float):
        self.name = name
        self.checkout_time = checkout_time


class Customer:
    def __init__(self, customer_id: int, products: list[Product]):
        self.customer_id = customer_id
        self.products = products


async def checkout_customer(queue: asyncio.Queue, cashier_number: int):
    while True:
        # while not queue.empty():
        # queue.get_nowait() - возвращает управление моментально, и в случае, если в очереди нет никого - выдаёт исключение asyncio.queues.QueueEmpty
        # await queue.get() - наоборот, отдаёт управление другой сопрограмме, если в очереди нет никого.

        # Лучше использовать await queue.get() для ожидания, чем try except с queue.get_nowait(),
        # потому что try_except будет жрать процессорное время.

        customer: Customer = await queue.get()
        # customer: Customer = queue.get_nowait()

        print(f"Кассир {cashier_number} обслуживает покупателя {customer.customer_id}")

        for product in customer.products:
            print(
                f"Кассир {cashier_number} обслуживает покупателя {customer.customer_id}: {product.name}"
            )
            await asyncio.sleep(product.checkout_time)

        print(
            f"Кассир {cashier_number} закончил обслуживать покупателя {customer.customer_id}"
        )
        queue.task_done()


def generate_customer(customer_id: int) -> Customer:
    all_products = [
        Product("пиво", 2),
        Product("бананы", 0.2),
        Product("колбаса", 0.5),
        Product("подгузники", 0.2),
    ]

    products = [
        all_products[randrange(len(all_products))] for _ in range(randrange(10))
    ]

    return Customer(customer_id, products)


async def customer_generator(queue: asyncio.Queue):
    customer_count = 0

    while True:
        customers: list[Customer] = [
            generate_customer(i)
            for i in range(customer_count, customer_count + randrange(5))
        ]

        for customer in customers:
            print("Ожидаю возможности поставить покупателя в очередь...")
            await queue.put(customer)

            print("Покупатель поставлен в очередь!")

        customer_count = customer_count + len(customers)
        await asyncio.sleep(1)


async def main():
    # У любой системы есть ограничения. Также можно ограничить количество элементов в очереди (maxsize = int number),
    # Если мы захотим добавить элемент с помощью queue.put_nowait(element) и очередь будет заполнена,
    # то выведется исключение asyncio.queues.QueueFull.
    # await queue.put(element) - будет дожидаться, пока очередь освободиться и не будет выводить исключение

    customer_queue = asyncio.Queue(5)

    customer_producer = asyncio.create_task(customer_generator(customer_queue))

    cashiers = [
        asyncio.create_task(checkout_customer(customer_queue, i)) for i in range(3)
    ]
    await asyncio.gather(customer_producer, *cashiers)


asyncio.run(main())
