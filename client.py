import socket
import sys
from threading import Thread

# Get client data
host = input("Host: ")
port = input("Port: ")
if not host: host = "localhost"
if not port: 
    port = 3585
else:
    port = int(port)


# Attempt connection to server
try:
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((host, port))
except:
    print("Could not make a connection to The Chat App")
    input("Press enter to quit")
    sys.exit(0)

# Wait for incoming data from server
def receive(clientSocket):
    while True:
        try:
            data = clientSocket.recv(144)
            print(str(data.decode("utf-8")))
        except:
            print("You have been disconnected from The Chat App")
            break

# Create new thread to wait for data
receiveThread = Thread(target = receive, args = (clientSocket, ))
receiveThread.daemon = True
receiveThread.start()

# Send data to server
while True:
    message = input()
    clientSocket.sendall(str.encode(message))
    if (message == "{quit}"):
        break

clientSocket.close()
sys.exit(0)