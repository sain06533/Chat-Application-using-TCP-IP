import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, END, filedialog

def receive_messages(client_socket):
    try:
        while True:
            message = client_socket.recv(4096).decode('utf-8')
            if not message:
                break
            if message.startswith("IMG_START"):
                sender_port = int(message.split(":")[1])
                save_photo(client_socket, sender_port)
            else:
                display_message(f"Server: {message}")
    except Exception as e:
        print(f"Error receiving message: {e}")
    finally:
        client_socket.close()

def send_message():
    try:
        message = input_box.get()
        client_socket.send(message.encode('utf-8'))
        display_message(f"You: {message}")
        input_box.delete(0, END)
    except Exception as e:
        print(f"Error sending message: {e}")

def send_photo():
    file_path = filedialog.askopenfilename()
    if file_path:
        client_socket.send(f"IMG_START:{client_socket.getsockname()[1]}".encode('utf-8'))
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                client_socket.send(data)
        client_socket.send(b"IMG_END")
        display_message("You sent a photo.")
    else:
        print("No file selected.")

def save_photo(client_socket, sender_port):
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        with open(file_path, 'wb') as file:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                if data == b"IMG_END":
                    break
                file.write(data)
        display_message(f"Received and saved a photo from sender port {sender_port}.")
    else:
        print("No file selected.")

def display_message(message):
    chat_log.configure(state='normal')
    chat_log.insert(tk.END, message + "\n")
    chat_log.configure(state='disabled')
    chat_log.see(tk.END)

def start_client():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    root.mainloop()

# Create the GUI
root = tk.Tk()
root.title("Chat Client")

chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=20)
chat_log.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

input_box = tk.Entry(root, width=40)
input_box.grid(row=1, column=0, padx=10, pady=10)

send_button = tk.Button(root, text="Send", width=10, command=send_message)
send_button.grid(row=1, column=1, padx=5, pady=10)

send_photo_button = tk.Button(root, text="Send Photo", width=10, command=send_photo)
send_photo_button.grid(row=2, column=0, padx=5, pady=10)

if __name__ == "__main__":
    start_client()
