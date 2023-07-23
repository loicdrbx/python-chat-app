import socket
from threading import Thread

# Stores information about connected clients
connections = {}

class Client():
    """ Class representing a connected client. """

    def __init__(self, socket, address, name):
        """
        Initialize a new Client object.

        Args:
            socket (socket.socket): The client's socket object.
            address (tuple): The client's address (host, port).
            name (str): The client's unique username.

        Returns:
            None
        """
        self.socket = socket
        self.address = address
        self.name = name

    def __str__(self):
        """
        Get a string representation of the Client object.

        Returns:
            str: A string representation of the Client object.
        """
        return str(self.id) + " " + str(self.address)


def handleClientMessages(clientInfo):
    """
    Handle messages going to and coming from a connected client.

    Args:
        clientInfo (tuple): A tuple containing the client's socket and address.

    Returns:
        None
    """
    # Gather and store client data in the connections dictionary
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

def broadcast(message, senderName = ""):
    """
    Broadcast a message to connected clients.

    Args:
        message (bytes): The message to be broadcasted.
        senderName (str, optional): The username of the message sender. Defaults to "".

    Returns:
        None
    """
    recipientName = parseUsername(message)
    if len(recipientName) > 0:
        # private message
        message = message.replace(str.encode("@{" + recipientName + "}"), b"")
        if recipientName in connections:
            connections[recipientName].socket.sendall(str.encode(senderName + "(private): ") + message)
        else:
            connections[senderName].socket.sendall(str.encode(recipientName + " is not a user on The Chat App."))       
    else:
        # group message
        for Client in connections.values():
            if not senderName:  # no senderName for messages comming from the server.
                Client.socket.sendall(message)
            elif senderName and Client.name != senderName:
                Client.socket.sendall(str.encode(senderName + ": ") + message)

def parseUsername(message):
    """
    Extract a username tag from a message.

    Args:
        message (bytes): The message from which to extract the username.

    Returns:
        str: The extracted username or an empty string if no username is found.    
    """
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

def newConnections(serverSock):
    """
    Monitor new client connections.

    Args:
        serverSock (socket.socket): The server socket to listen for connections.

    Returns:
        None
    """
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
    """
    Entry point for the chat server.

    Returns:
        None
    """
    # Get host and port
    host = input("Host: ")
    port = input("Port: ")

    if not host: 
        host = "localhost"
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
    
if __name__ == "__main__":
    main()