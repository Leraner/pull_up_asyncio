from threading import Thread
import socket


# Переопределяем класс Thread, для того, чтобы закрыть все потоки, после остановки приложения.
# Или же закрыть поток, когда клиент закрыл подключение. Это нужно для того, чтобы после нажатия CTRL + C
# программа завершалась и не оставляла работать потоки.

# Поток считается работающим (активным) пока его метод run исполняется.
# Если он перестаёт быть активным, то поток завершается.

class ClientEchoThread(Thread):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        try:
            while True:
                data = self.client.recv(1024)
                if not data:
                    raise BrokenPipeError("Подключение закрыто!")
                print(f"Получено {data}, отправляю!")
                self.client.sendall(data)
        except OSError as e:
            print(e)
            print(f"Поток прерван исключением {e}, производится остановка")

    def close(self):
        if self.is_alive():
            self.client.sendall(bytes("Останавливаюсь", encoding="utf-8"))
            self.client.shutdown(socket.SHUT_RDWR)


# def echo(client: socket):
#     while True:
#         data = client.recv(1024)
#         print(f"Получено {data}, отправляю!")
#         client.sendall(data)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 8000))
    server.listen()
    thread_connections = []

    try:
        while True:
            connection, addr = server.accept()
            thread = ClientEchoThread(connection)
            thread_connections.append(thread)
            thread.start()
    except KeyboardInterrupt:
        print("Останавливаюсь!")
        [thread.close() for thread in thread_connections]