import socket
import time

HOST = '127.0.0.1'
PORT = 65432


def read_config(file_name):
    """
    Reads the config's formatted file
    the file must have the format:
    max_msg_size: integer
    """
    config = {}
    try:
        with open(file_name, 'r') as file:
            for line in file:
                key, value = line.strip().split(':', 1)
                config[key.strip()] = value.strip().strip('"')
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file {file_name} not found")
    except ValueError:
        raise ValueError(f"Invalid format in config file: {file_name}")
    return config


def start_server():
    """
    Starts the server, listens for a client connection, and handles communications.
    """
    config_option = input("Choose max message configuration method: 1 for manual config, 2 for config file  ").strip()

    if config_option == '1':
        max_msg_size = int(input("Enter max message size: "))
    elif config_option == '2':
        file_name = "config.txt"
        config = read_config(file_name)
        max_msg_size = int(config["max_msg_size"])
        print(f"Read max message size from config: {max_msg_size} bytes")
    else:
        print("Invalid config option received from client. Exiting")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    print(f"Server initialised on {HOST}:{PORT}")

    server_socket.listen(1)
    print("Waiting for a client to connect...")

    conn, addr = server_socket.accept()
    print(f" Connected to: {addr}")

    try:
        request = conn.recv(1024).decode('utf-8').strip()
        if request == 'GET_MAX_MSG_SIZE':
            conn.sendall(f"SIZE:{max_msg_size}".encode('utf-8'))
            print(f"Sent max message size to client: {max_msg_size} bytes")

        else:
            print("Invalid request received from client. Exiting")
            return

        handle_client(conn)
    finally:
        conn.close()
        print(" Connection closed")
        server_socket.close()


def handle_client(conn):


    highest_ack = -1
    received = {}

    while True:
        data = conn.recv(1024)
        if not data:
            break
        messages = data.decode('utf-8').split('M')[1:]
        for msg in messages:

            try:
                seq, message = process_message(f"M{msg}")
                received[seq] = message
                print(f" Received message from {seq}: {message}")
            except ValueError:
                print("Invalid message format")
                continue

            while highest_ack + 1 in received:
                highest_ack += 1

            ack = f"ACK{highest_ack}"
            conn.sendall(ack.encode('utf-8'))
            print(f" Sent ACK to client: {ack}")

            time.sleep(0.01)


def process_message(message):
    if not message.startswith('M') or ':' not in message:
        raise ValueError("Invalid message format")

    seq, content = message.split(':', 1)
    seq_num = int(seq[1:])
    return seq_num, content.strip()


if __name__ == "__main__":
    start_server()
