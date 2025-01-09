import asyncio
import logging
import socket


# tasks = []

async def listen_for_connections(
    server_socket: socket,
    loop: asyncio.AbstractEventLoop,
):
    while True:
        connection, address = await loop.sock_accept(server_socket)
        connection.setblocking(False)
        print(f"Получен запрос на подключение от {address}")
        # Если делать tasks.append, то исключение не напишется в консоль
        # tasks.append(asyncio.ensure_future(echo(connection, loop)))
        asyncio.ensure_future(echo(connection, loop))


async def echo(connection: socket, loop: asyncio.AbstractEventLoop):
    try:
        while data := await loop.sock_recv(connection, 1024):
            if data == b"boom\r\n":
                raise Exception("Неожиданная ошибка")

            await loop.sock_sendall(connection, data)
    except Exception as e:
        logging.exception(e)
    finally:
        connection.close()

async def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket.AF_INET - тип адреса (имя хоста и порт)
    # socket.SOCK_STREAM - означает, что взаимодействие будет проходить с помощью TCP

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Вызываем setsockopt для того, чтобы поставить флаг socket.SO_REUSEADDR в 1
    # Это позволит использовать номер порта повторно, после того, как мы остановим и заново запустим приложение
    # Избегнув тем самым ошибку "Адрес уже используется"

    server_socket.setblocking(False)
    # Убираем блокирование сокета. То есть если данные не готовы для обработки, то мы переходим к следующему коду

    address = ("127.0.0.1", 8000)
    server_socket.bind(address)

    server_socket.listen()

    await listen_for_connections(server_socket, loop=asyncio.get_event_loop())


asyncio.run(main())
