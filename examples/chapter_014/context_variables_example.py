import asyncio
from asyncio import StreamReader, StreamWriter
from contextvars import ContextVar

# Контекстные переменные

# Это глобальные переменные на уровне одного потока.

# Данные, хранящиеся в поточно-локальной переменной,
# будут видны только потоку, сохранившему их,
# и таким образом решается как проблема сопоставления данных потоку,
# так и проблема синхронизации доступа.


# Разумеется, в приложениях asyncio обычно имеется только один поток,
# поэтому любая поточно-локальная переменная доступна в любом месте приложения.

# Контекстные переменные похожи на поточно-локальные,
# но локальны для задачи, а не для потока.
# Это означает, что если задача создает контекстную переменную,
# то к ней будет иметь доступ любая внутренняя сопрограмма или задача,
# созданная внутри задачи-создателя. А никакие задачи вне этой цепочки не смогут ни увидеть,
# ни модифицировать эту переменную. Это позволяет хранить состояние, связанное с конкретной задачей,
# не передавая его явно в виде аргумента.


class Server:
    user_address = ContextVar("user_address")

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def start_server(self):
        server = await asyncio.start_server(
            self._client_connected, self.host, self.port
        )

        await server.serve_forever()

    def _client_connected(self, reader: StreamReader, writer: StreamWriter):
        self.user_address.set(writer.get_extra_info("peername"))
        asyncio.create_task(self.listen_for_messages(reader))

    async def listen_for_messages(self, reader: StreamReader):
        while data := reader.readline():
            print(f"Получено сообщение {data} от {self.user_address.get()}")


async def main():
    server = Server("127.0.0.1", 9000)
    await server.start_server()


asyncio.run(main())