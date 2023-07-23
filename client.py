import socket
import sys
from threading import Thread

def receive(clientSocket):
    """
    Continuosly receive and print messages from the server.

    Args:
        clientSocket (socket.socket): The client's socket object.

    Returns:
        None
    """
    while True:
        try:
            data = clientSocket.recv(144)
            print(str(data.decode("utf-8")))
        except Exception as e:
            print("You have been disconnected from The Chat App: ", e)
            break

def main():
    """
    Entry point for The Chat App client program

    Returns:
        None
    """

    # Get client data from the user
    host = input("Host: ")
    port = input("Port: ")

    if not host: 
        host = "localhost"
    if not port: 
        port = 3585
    else:
        port = int(port)

    # Attempt connection to the server
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
    except Exception as e:
        print("Could not make a connection to The Chat App: ", e)
        input("Press enter to quit")
        sys.exit(0)

    # Wait for incoming messages on a different thread
    receiveThread = Thread(target = receive, args = (clientSocket, ))
    receiveThread.daemon = True
    receiveThread.start()

    # Transmit user's message to the server
    while True:
        message = input()
        clientSocket.sendall(str.encode(message))
        if (message == "{quit}"):
            break

    clientSocket.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
