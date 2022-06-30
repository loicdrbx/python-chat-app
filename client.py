import socket
import sys
from threading import Thread

# Wait for incoming data from server
def receive(clientSocket):
    while True:
        try:
            data = clientSocket.recv(144)
            print(str(data.decode("utf-8")))
        except:
            print("You have been disconnected from The Chat App")
            break

# Encode binary string to B8ZS
# Inspired by: https://github.com/PotatoSpudowski/PyB8ZS/blob/master/utils.py
def encodeB8ZS(binStr):
    consecZeros = 0
    sequence = {
        "+" : '000+-0-+',
        "-" : '000-+0+-'
    }

    bamiStr = binaryToBAMI(binStr)
    for i in range(len(bamiStr)):
        if bamiStr[i] == '+':
            prevNonZero = '+'
            consecZeros = 0
        elif bamiStr[i] == '-':
            prevNonZero = '-'
            consecZeros = 0
        elif bamiStr[i] == '0':
            consecZeros += 1
            if consecZeros == 8:
                bamiStr = bamiStr[0:i-7] + sequence[prevNonZero] + bamiStr[i+1:]
                consecZeros = 0

    return bamiStr

# Convert binary to Bipolar AMI
# Inspired by: https://github.com/PotatoSpudowski/PyB8ZS/blob/master/utils.py
def binaryToBAMI(binStr):
    prevNonZero = '-'
    binStr = list(binStr)
    b8zs = [0] * len(binStr)
    for i in range(len(binStr)):
        if binStr[i] == '1' and prevNonZero == '+':
            b8zs[i] = '-'
            prevNonZero = '-'
        elif binStr[i] == '1' and prevNonZero == '-':
            b8zs[i] = '+'
            prevNonZero = '+'
    return ''.join(map(str, b8zs))  

# Check if a string is in binary format
def isBinary(str):
    for char in str:
        if (char != '0' and char != '1'):
            return False
    return True


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

# Create new thread to wait for data
receiveThread = Thread(target = receive, args = (clientSocket, ))
receiveThread.daemon = True
receiveThread.start()

# Send data to server
while True:
    message = input()

    if (isBinary(message)):
        message = encodeB8ZS(message)
        print(message)

    clientSocket.sendall(str.encode(message))

    if (message == "{quit}"):
        break

clientSocket.close()
sys.exit(0)