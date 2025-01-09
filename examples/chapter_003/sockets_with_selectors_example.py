import socket
import selectors

selector = selectors.DefaultSelector()

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
# Слушаем запросы от клиентов

selector.register(server_socket, selectors.EVENT_READ)

try:
    while True:
        # Смотрим, пришли ли события или нет
        events: list[tuple[selectors.SelectorKey, int]] = selector.select(timeout=1)

        if len(events) == 0:
            print("Событий никаких нет")
            continue

        for event, _ in events:
            event_socket = event.fileobj

            if event_socket == server_socket:
                connection, address = server_socket.accept()
                connection.setblocking(False)
                print(f"Получен запрос на подключение {address}")
                selector.register(connection, selectors.EVENT_READ)
            else:
                data = event_socket.recv(1024)
                print(f"Получены данные {data}")
                event_socket.send(data)
finally:
    server_socket.close()
