import socket
import threading

def handle_client(client_socket, client_address):
    try:
        while True:
            message = client_socket.recv(4096).decode('utf-8')
            if not message:
                break
            if message.startswith("IMG_START"):
                sender_port = client_address[1]
                broadcast(client_socket, f"Image sent by client on port {sender_port}")
                receive_photo(client_socket)
            else:
                broadcast(client_socket, f"Client {client_address[1]}: {message}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def broadcast(sender_socket, message):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message: {e}")

def receive_photo(client_socket):
    file_data = b""
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        file_data += data
        if data.endswith(b"IMG_END"):
            break
    save_photo(client_socket, file_data)

def save_photo(client_socket, file_data):
    file_path = "received_image.png"
    with open(file_path, 'wb') as file:
        file.write(file_data)
    client_socket.send(b"IMG_END")
    print("Received and saved a photo.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(5)
    print("Chat Server started, listening on port 12345")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address[0]}:{client_address[1]}")
        clients.append(client_socket)
        broadcast(client_socket, f"Client {client_address[1]} joined the chat.")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

clients = []

if __name__ == "__main__":
    start_server()
