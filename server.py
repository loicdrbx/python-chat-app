from pyexpat.errors import messages
import socket
from threading import Thread

# Variables for holding information about connections
connections = {}

# Client class: a new instance created for each connected client
# Each instance has the socket and address that is associated with,
# along with a unique username
class Client():
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address

    def __str__(self):
        return str(self.id) + " " + str(self.address)

# Handle messages to and from a connected client
def handleClientMessages(clientInfo):
    # Gather and store client data in connections dict
    clientSock, address = clientInfo
    startStr = str(clientSock.recv(144).decode())
    while startStr != 'Request to send':
        clientSock.sendall(str.encode("Type 'Request to send' to begin:"))
        startStr = str(clientSock.recv(144).decode())
    connections[clientSock] = Client(clientSock, address)
    
    # Welcome client to the app
    clientSock.sendall(str.encode("\nWelcome to The B8ZS App! Type a binary string to encode it in B8ZS. Type {quit} to leave.\n"))
    clientSock.sendall(str.encode("Ready to recieve:"))

    # Continuously monitor for meassages from the client
    while True:
        message = clientSock.recv(144)
        if message == str.encode("{quit}"):
            clientSock.close()
            connections.pop(clientSock)
            print("Client " + str(address) + " has disconnected")
            break
        elif isB8ZS(message):
            print(decodeB8ZS(message))
        else:
            clientSock.sendall(str.encode("E: Invalid b8zs string. Try again or type {quit} to leave.\n"))            

# Check if a string is in B8ZS format
def isB8ZS(message):
    messageStr = str(message.decode())
    for char in messageStr:
        if (char != '0' and char != '+' and char != '-'):
            return False
    return True


# Decode a B8ZS string to binary
def decodeB8ZS(b8zs):
    b8zsStr = str(b8zs.decode())
    binary = b8zsStr.replace("000-+0+-", "00000000")
    binary = binary.replace("000+-0-+", "00000000")
    binary = binary.replace("+", "1")
    binary = binary.replace("-", "1")

    return binary

# Monitor for new connections
def newConnections(serverSock):
    try:
        while True:
            # Continuously listen for connections
            clientSock, address = serverSock.accept()
            print("New connection with address " + str(address))
            clientSock.sendall(str.encode("Welcome B8ZS App. Type 'Request to send' to begin:"))

            # Create new thread to listen to each client's messages
            handleClientThread = Thread(target = handleClientMessages, args = ((clientSock, address),))
            handleClientThread.daemon = True
            handleClientThread.start()
    except (KeyboardInterrupt, SystemExit):
        return
    
def main():
    # Hardcoded for testing
    host = "localhost"
    port = 3585

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print("Server listening at " + str(host) + ":" + str(port) + "...")

    # Listen for new connections
    newConnections(sock)

    sock.close()
    
main()