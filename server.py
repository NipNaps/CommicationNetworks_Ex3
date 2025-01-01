import socket

HOST = '127.0.0.1'
PORT = 65432


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((HOST, PORT))
    print(f"Server initialised on {HOST}:{PORT}")

    server_socket.listen(1)
    print("Waiting for a client to connect...")

    conn, addr = server_socket.accept()
    print(f" Connected from {addr}")

    handle_client(conn)
    conn.close()
    server_socket.close()
    print(" Connection closed")


def handle_client(conn):
    max_message_size = 100
    conn.sendall(str(max_message_size).encode('utf-8'))
    print(f"Max message size is {max_message_size} bytes")
    highest_ack = -1
    received = {}

    while True:
        data = conn.recv(1024)
        if not data:
            break

        try:
            seq, message = process_message(data.decode('utf-8'))
            received[seq] = message
            print(f" Received message from client: {message}")
        except ValueError:
            print("Invalid message format")
            continue
        while highest_ack + 1 in received:
            highest_ack += 1

        ack = f"ACK {highest_ack}"
        conn.sendall(ack.encode('utf-8'))
        print(f" Sent ACK to client: {ack}")


def process_message(message):
    if not message.startswith('M') or ':' not in message:
        raise ValueError("Invalid message format")

    seq, content = message.split(':', 1)
    seq_num = int(seq[1:])
    return seq_num, content.strip()


if __name__ == "__main__":
    start_server()
