import socket

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

connections = []

try:
    while True:
        try:
            connection, client_address = server_socket.accept()
            # Ждем запроса на подключение. Этот метод блокирует программу до получения запроса, после чего возвращает
            # Объект подключения и адрес запроса
            print(f"Получен запрос на подключение {client_address}")

            connection.setblocking(False)
            # Помечаем клиентский сокет как неблокирующий

            connections.append(connection)
        except BlockingIOError:
            # Отлавливать эту ошибку нужно, потому что сокет не блокирующий и при запуске приложения
            # К сокету никто не подключается, нет данных для обработки. Сразу подключиться не представляется возможным
            pass

        buffer = b""

        for connection in connections:
            try:
                while buffer[-2:] != b"\r\n":
                    data = connection.recv(2)
                    if not data:
                        break
                    else:
                        print(f"Получены данные {data}")
                        buffer += data

                print(f"Все данные {buffer}")

                connection.send(buffer)
            except BlockingIOError:
                # Идентичная ситуация, что и выше
                pass

finally:
    server_socket.close()

# Резюме: Из-за перехвата исключений в бесконечном цикле потребление процессора быстро доходит до 100 %
# и на этом уровне остается

# При запуске на macbook pro M3 - 99.3 %
