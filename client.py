import socket

HOST = '127.0.0.1'
PORT = 65432

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print("Команды: /add <текст>, /list, /done <номер>, /delete <номер>, /quit\n")

        while True:
            command = input("> ").strip()
            if not command:
                continue

            client_socket.sendall(command.encode('utf-8'))

            response = client_socket.recv(4096).decode('utf-8')
            print(response)

            if command.lower() == "/quit":
                break

    except ConnectionRefusedError:
        print("Ошибка: Не удалось подключиться к серверу. Убедитесь, что server.py запущен.")
    except (ConnectionResetError, KeyboardInterrupt):
        print("\nСоединение с сервером разорвано.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
