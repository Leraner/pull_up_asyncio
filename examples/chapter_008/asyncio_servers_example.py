import asyncio
import logging


"""
Когда пользователь подключается к серверу, 
вызывается сопрограмма client_connected, 
которой передаются читатель и писатель для этого пользователя, а та, 
в свою очередь, вызывает метод-сопрограмму состояния сервера add_client. 
В add_client мы сохраняем объект StreamWriter, 
чтобы можно было отправлять сообщения всем подключенным клиентам, 
а при отключении клиента удаляем этот объект. 
Далее вызывается метод _on_connect, который отправляет сообщение клиенту, 
информируя его о количестве подключенных пользователей. 
В _on_connect мы также уведомляем всех остальных клиентов о подключении нового пользователя.

Сопрограмма _echo похожа на то, что мы делали раньше, 
только теперь мы еще уведомляем всех пользователей о том, 
что какой-то клиент отключился. В результате мы получили эхо-сервер, 
уведомляющий всех своих клиентов о подключении и отключении пользователей.
"""


class ServerState:
    def __init__(self):
        self._writers = []

    async def add_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        self._writers.append(writer)
        await self._on_connect(writer)
        asyncio.create_task(self._echo(reader, writer))

    async def _on_connect(self, writer: asyncio.StreamWriter):
        writer.write(
            f"Добро пожаловать! Число подключенных пользователей {len(self._writers)}!\n".encode()
        )
        await writer.drain()
        await self._notify_all("Подключился новый пользователь!\n")

    async def _echo(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while (data := await reader.readline()) != b"":
                writer.write(data)
                await writer.drain()
            self._writers.remove(writer)
            await self._notify_all(
                f"Клиент отключился. Осталось пользователей: {len(self._writers)}!\n"
            )
        except Exception as e:
            logging.exception("Ошибка чтения данных от клиента.", exc_info=e)
            self._writers.remove(writer)

    async def _notify_all(self, message: str):
        for writer in self._writers:
            try:
                writer.write(message.encode())
                await writer.drain()
            except ConnectionError as e:
                logging.exception("Ошибка записи данных клиенту.", exc_info=e)
                self._writers.remove(writer)


async def main():
    server_state = ServerState()

    async def client_connected(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        await server_state.add_client(reader, writer)

    server = await asyncio.start_server(client_connected, "127.0.0.1", 8000)

    async with server:
        await server.serve_forever()


asyncio.run(main())
