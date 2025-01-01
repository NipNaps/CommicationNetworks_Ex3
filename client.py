import socket
import time

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65432


def read_config(file_name):
    """
    Reads config from values from a formatted .txt file
    format was provided in the pdf file
    """

    config = {}
    try:
      with open(file_name, 'r') as file:
         for line in file:
            key, value = line.strip().split(':', 1)
            config[key.strip()] = value.strip().strip('"')
    except FileNotFoundError:
        raise FileNotFoundError(f"config file {file_name} not found")
    except ValueError:
        raise ValueError(f"Invalid format in the config file: {file_name}")
    return config



def start_client():
    """
    Connects to the server, sends a segmented message as needed, and handles acknowledgments.

    """
    config_option = input("Choose configuration option: 1 for manual input, 2 config file ").strip()
    if config_option == '1':
        message = input("Enter message to send: ").strip()
        max_msg_size = int(input("Enter max message size: "))
        window_size = int(input("Enter window size: "))
        timeout = int(input("Enter timeout (in seconds): "))
    elif config_option == '2':
        file_name = input("Enter the config's file name: ").strip()
        config = read_config(file_name)
        message = config["message"]
        max_msg_size = int(config["max_msg_size"])
        window_size = int(config["window_size"])
        timeout = int(config["timeout"])
    else:
        print("Invalid config option")
        return



    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

        client_socket.sendall(config_option.encode('utf-8'))
        print(f"Sent configuration option: {config_option}")

        if config_option == '1':
            ack = client_socket.recv(1024).decode('utf-8')
            print(f"Received ACK for config option: {ack}")

            client_socket.sendall(str(max_msg_size).encode('utf-8'))

        server_max_msg_size = int(client_socket.recv(1024).decode('utf-8'))
        max_msg_size = min(max_msg_size, server_max_msg_size)
        print(f"Received max message size: {server_max_msg_size} bytes from server")

        segments = [message[i:i + max_msg_size] for i in range(0, len(message), max_msg_size)]
        print(f"Message divided into {len(segments)} segments")


        next_seq_num = 0
        base = 0
        timer_start = None


        while base < len(segments):

            while next_seq_num < base + window_size and next_seq_num < len(segments):
                msg_with_seq = f"M{next_seq_num}:{segments[next_seq_num]}"
                client_socket.send(msg_with_seq.encode('utf-8'))
                print(f" Sent: {msg_with_seq}")
                next_seq_num += 1

            if timer_start is None:
                timer_start = time.time()

            try:
                client_socket.settimeout(timeout - (time.time() - timer_start))
                ack = client_socket.recv(1024).decode('utf-8')
                print(f"Received ack: {ack}")

                if ack.startswith("ACK"):
                    ack_num = int(ack[3:])
                    base = ack_num + 1
                    print(f"Windows base move to {base}")
                    timer_start = None  # Reset time when acknowledgment is received
                else:
                    print(f"Invalid ack format received: {ack}")
            except socket.timeout:
                print("Timeout, Resending unacknowledged messages.")
                next_seq_num = base
                timer_start = None
        print(" All segments sent and acknowledged.")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client_socket.close()
        print("Connection closed.")


if __name__ == '__main__':
    start_client()

