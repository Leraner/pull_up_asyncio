import asyncio
from random import randrange


class Product:
    def __init__(self, name: str, checkout_time: float):
        self.name = name
        self.checkout_time = checkout_time


class Customer:
    def __init__(self, customer_id: int, products: list[Product]):
        self.customer_id = customer_id
        self.products = products


async def checkout_customer(queue: asyncio.Queue, cashier_number: int):
    # Если мы хотим, чтобы кассиры ожидали покупателей, 
    # а не завершали свою работу, когда в очереди никого нет - нужно использовать закомменитированный код

    # while True:
    while not queue.empty():
        # queue.get_nowait() - возвращает управление моментально, и в случае, если в очереди нет никого - выдаёт исключение asyncio.queues.QueueEmpty
        # await queue.get() - наоборот, отдаёт управление другой сопрограмме, если в очереди нет никого.
        
        # Лучше использовать await queue.get() для ожидания, чем try except с queue.get_nowait(), 
        # потому что try_except будет жрать процессорное время.

        # customer: Customer = await queue.get()
        customer: Customer = queue.get_nowait()

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


async def main():
    # У любой системы есть ограничения. Также можно ограничить количество элементов в очереди (maxsize = int number),
    # Если мы захотим добавить элемент с помощью queue.put_nowait(element) и очередь будет заполнена, 
    # то выведется исключение asyncio.queues.QueueFull. 
    # await queue.put(element) - будет дожидаться, пока очередь освободиться и не будет выводить исключение

    customer_queue = asyncio.Queue()

    all_products = [
        Product("пиво", 2),
        Product("бананы", 0.2),
        Product("колбаса", 0.5),
        Product("подгузники", 0.2),
    ]

    for customer_id in range(10):
        products = [
            all_products[randrange(len(all_products))] for _ in range(randrange(10))
        ]
        customer_queue.put_nowait(Customer(customer_id, products))

    cashiers = [
        asyncio.create_task(checkout_customer(customer_queue, i)) for i in range(3)
    ]
    await asyncio.gather(customer_queue.join(), *cashiers)


asyncio.run(main())