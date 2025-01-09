import asyncio
from typing import AsyncGenerator


async def read_until_empty(
    stream_reader: asyncio.StreamReader,
) -> AsyncGenerator[str, None]:
    while response := await stream_reader.readline():
        yield response.decode()


async def main():
    host: str = "www.example.com"
    request: str = (
        f"GET / HTTP/1.1\r\n" f"Connection: close\r\n" f"Host: {host}\r\n\r\n"
    )

    stream_reader, stream_writer = await asyncio.open_connection(host, 80)

    try:
        stream_writer.write(request.encode())

        # Эта сопрограмма блокирует выполнение, пока все находящиеся в очереди данные не будут отправлены в сокет.
        await stream_writer.drain()

        responses = [response async for response in read_until_empty(stream_reader)]

        print("".join(responses))
    finally:
        # Зачем здесь нужно вызывать метод и сопрограмму?
        # Потом что в ходе вызова close выполняется несколько действий,
        # в частности отмена регистрации сокета и вызов метода connection_lost нижележащего транспортного механизма.
        # Все это происходит асинхронно на более поздней итерации цикла событий,
        # а значит, сразу после вызова close наше подключение еще не закрыто, это случится немного позже.

        stream_writer.close()
        await stream_writer.wait_closed()


asyncio.run(main())
