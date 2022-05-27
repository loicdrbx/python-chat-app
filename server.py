import socket
from threading import Thread

# Variables for holding information about connections
connections = {}

# Client class: a new instance created for each connected client
# Each instance has the socket and address that is associated with,
# along with a unique username
class Client():
    def __init__(self, socket, address, name):
        self.socket = socket
        self.address = address
        self.name = name

    def __str__(self):
        return str(self.id) + " " + str(self.address)

# Handle messages to and from a connected client
def handleClientMessages(clientInfo):
    # Gather and store client data in connections dict
    clientSock, address = clientInfo
    name = str(clientSock.recv(144).decode())
    while name in connections:
        clientSock.sendall(str.encode("This username is taken, choose another one and press Enter:"))
        name = str(clientSock.recv(144).decode())
    connections[name] = Client(clientSock, address, name)
    
    # Welcome client into the chat room
    clientSock.sendall(str.encode("Welcome to The Chat App %s! Tips: Prefix your messages with @{username} to send a direct message. Type {quit} to leave the app.\n" % name))
    broadcast(str.encode("%s has joined the room." % name))

    # Continuously monitor for meassages from the client
    while True:
        message = clientSock.recv(144)
        if message == str.encode("{quit}"):
            clientSock.close()
            connections.pop(name)
            broadcast(str.encode("%s has left the chat." % name))
            print("Client " + str(address) + " has disconnected")
            break
        else:
            broadcast(message, name)

# Broadcast message to other clients
def broadcast(message, senderName = ""):
    # Check if direct message
    recipientName = parseUsername(message)
    if len(recipientName) > 0:
        message = message.replace(str.encode("@{" + recipientName + "}"), b"")
        if recipientName in connections:
            connections[recipientName].socket.sendall(str.encode(senderName + "(private): ") + message)
        else:
            connections[senderName].socket.sendall(str.encode(recipientName + " is not a user on The Chat App."))       
    else:
        for Client in connections.values():
            # From server to entire chat room
            if not senderName:
                Client.socket.sendall(message)
            elif senderName and Client.name != senderName:
                Client.socket.sendall(str.encode(senderName + ": ") + message)

# Extract username from message
def parseUsername(message):
    username = ""
    messageStr = str(message.decode())
    if messageStr.startswith("@{"):
        for i in range(2, len(messageStr)):
            if messageStr[i] == "{":
                break
            elif messageStr[i] == "}":
                return username
            else:
                username += messageStr[i]
    return ""

# Monitor for new connections
def newConnections(serverSock):
    while True:
        # Continuously listen for connections
        clientSock, address = serverSock.accept()
        print("New connection with address " + str(address))
        clientSock.sendall(str.encode("Welcome to The Chat App. Type your name and press Enter to continue:"))

        # Create new thread to listen to each client's messages
        handleClientThread = Thread(target = handleClientMessages, args = ((clientSock, address),))
        handleClientThread.daemon = True
        handleClientThread.start()

def main():
    # Get host and port
    host = input("Host: ")
    port = input("Port: ")
    if not host: host = "localhost"
    if not port: 
        port = 3585
    else:
        port = int(port)

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print("Server listening at " + str(host) + ":" + str(port) + "...")

    # Listen for new connections
    newConnections(sock)
    
main()