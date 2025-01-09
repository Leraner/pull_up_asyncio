import asyncio
import logging


# Чат пользователей

class ChatServer:
    def __init__(self):
        self._username_to_writer = {}

    async def start_chat_server(self, host: str, port: int):
        server = await asyncio.start_server(self.client_connected, host, port)

        async with server:
            await server.serve_forever()

    async def client_connected(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        command = await reader.readline()
        print(f"CONNECTED {reader} {writer}")

        command, arg = command.decode().split(" ")

        if command == "CONNECTED":
            username = arg.replace("\n", "")
            self._add_user(username, reader, writer)
            await self._on_connected(username, writer)
        else:
            logging.error("Получена недопустимая команда от клиента, отключается.")
            writer.close()
            await writer.wait_closed()

    def _add_user(
        self, username: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        self._username_to_writer[username] = writer
        asyncio.create_task(self._listen_for_messages(username, reader))

    async def _on_connected(self, username: str, writer: asyncio.StreamWriter):
        writer.write(
            f"Добро пожаловать! Подключено пользователей: {len(self._username_to_writer)}!\n".encode()
        )
        await writer.drain()

        await self._notify_all(f"Подключился {username}!\n")

    async def _remove_user(self, username):
        writer = self._username_to_writer[username]
        del self._username_to_writer[username]

        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logging.exception(
                "Ошибка при закрытии клиентского писателя, игнорируется.",
                exc_info=e,
            )

    async def _listen_for_messages(self, username: str, reader: asyncio.StreamReader):
        try:
            while (data := await asyncio.wait_for(reader.readline(), 60)) != b"":
                await self._notify_all(f"{username}: {data.decode()}\n")

            await self._notify_all(f"{username} has left the chat\n")
        except Exception as e:
            logging.exception("Ошибка при чтении данных от клиента.", exc_info=e)
            await self._remove_user(username)

    async def _notify_all(self, message: str):
        inactive_users = []

        for username, writer in self._username_to_writer.items():
            try:
                print(message)
                writer.write(message.encode())
                await writer.drain()
            except ConnectionError as e:
                logging.exception("Ошибка при записи данных клиенту.", exc_info=e)
                inactive_users.append(username)

        [await self._remove_user(username) for username in inactive_users]


async def main():
    chat_server = ChatServer()
    await chat_server.start_chat_server("127.0.0.1", 8000)


asyncio.run(main())
