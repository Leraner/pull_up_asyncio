import asyncio


class HTTPGetClientProtocol(asyncio.Protocol):
    def __init__(self, host: str, loop: asyncio.AbstractEventLoop):
        self._host: str = host
        self._future: asyncio.Future = loop.create_future()
        self._transport: asyncio.Transport | None = None
        self._response_buffer: bytes = b""

    async def get_response(self):
        # Ждём, пока в объект future положат результат
        return await self._future

    def _get_request_bytes(self) -> bytes:
        request = (
            f"GET / HTTP/1.1\r\n" f"Connection: close\r\n" f"Host: {self._host}\r\n\r\n"
        )

        return request.encode()

    def connection_made(self, transport: asyncio.Transport):
        # Транспорт вызывает этот метод, когда сокет успешно подключен к HTTP серверу
        # Метод принимает в себя экземпляр asyncio.Transport, с помощью которого
        # можно взаимодействовать с сервером.
        print(f"Создано подключение к {self._host}")
        self._transport = transport
        self._transport.write(self._get_request_bytes())

    def data_received(self, data):
        # Транспортный механизм вызывает его, когда приходят данные.
        # Данные (data) приходят в виде массива байтов.
        # Метод может быть вызван несколько раз, поэтому нужно создать внутри буффер,
        # для хранения этих данных.
        print("Получены данные!")
        self._response_buffer += data

    def eof_received(self) -> bool | None:
        # Метод вызывается, когда мы получаем конец данных.
        # Таким образом мы понимаем, что передача данных окончена.
        # Гарантируется, что если этот метод был вызван, то метод data_received больше
        # никогда не вызовется.

        # Каким же образом потребители нашего протокола получат результат после завершения запроса?
        # Для этого мы создадим объект Future, где будет храниться полностью полученный результат.
        # Затем в конце метода eof_received сделаем результат будущего объекта результатом HTTP-ответа.
        self._future.set_result(self._response_buffer.decode())
        # Возвращает True, False, что определяет как останавливать транспорт.
        # False - транспорт остановит сам себя
        # True - обязанность остановки лежит на нашей реализации протокола
        return False

    def connection_lost(self, exc: Exception | None) -> None:
        if exc is None:
            print("Подключение закрыто без ошибок")
            return
        self._future.set_exception(exc)


async def make_request(host: str, port: int, loop: asyncio.AbstractEventLoop) -> str:
    def protocol_factory():
        return HTTPGetClientProtocol(host, loop)

    # create_connection принимает в себя protocol_factory, то есть функцию,
    # которая создаёт экземпляры протоколов.
    _, protocol = await loop.create_connection(protocol_factory, host=host, port=port)

    return await protocol.get_response()


async def main():
    loop = asyncio.get_running_loop()
    result = await make_request("www.example.com", 80, loop)
    print(result)


asyncio.run(main())
