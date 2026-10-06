import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

tasks = []
tasks_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"Подключился клиент: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8').strip()
            if not message:
                continue

            parts = message.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            response = ""

            if command == "/add":
                if not args:
                    response = "Ошибка: Укажите текст задачи"
                else:
                    with tasks_lock:
                        tasks.append({"text": args, "done": False})
                    response = f"Задача '{args}' добавлена."

            elif command == "/list":
                with tasks_lock:
                    if not tasks:
                        response = "Список пуст."
                    else:
                        lines = []
                        for idx, task in enumerate(tasks, 1):
                            status = "[x]" if task["done"] else "[ ]"
                            lines.append(f"{idx}. {status} {task['text']}")
                        response = "\n".join(lines)

            elif command == "/done":
                if not args.isdigit():
                    response = "Ошибка: Укажите корректный номер задачи"
                else:
                    task_num = int(args)
                    with tasks_lock:
                        if 1 <= task_num <= len(tasks):
                            tasks[task_num - 1]["done"] = True
                            response = f"Задача №{task_num} отмечена как выполненная."
                        else:
                            response = f"Ошибка: Задачи с номером {task_num} не существует."

            elif command == "/delete":
                if not args.isdigit():
                    response = "Ошибка: Укажите корректный номер задачи (например, /delete 1)"
                else:
                    task_num = int(args)
                    with tasks_lock:
                        if 1 <= task_num <= len(tasks):
                            removed = tasks.pop(task_num - 1)
                            response = f"Задача '{removed['text']}' удалена."
                        else:
                            response = f"Ошибка: Задачи с номером {task_num} не существует."

            elif command == "/quit":
                response = "До свидания!"
                conn.sendall(response.encode('utf-8'))
                break

            else:
                response = "Ошибка: Некорректная команда. Доступные команды: /add, /list, /done, /delete, /quit"

            conn.sendall(response.encode('utf-8'))

    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        print(f"Отключился клиент: {addr}")
        conn.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Сервер запущен на {HOST}:{PORT}...")

    try:
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nЗавершение работы сервера.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
