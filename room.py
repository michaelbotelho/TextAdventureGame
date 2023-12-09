# Author: Michael Botelho
# Assignment 4
# Computer Science 3357
# December 8, 2022

from socket import *
from signal import *
from urllib import parse
import sys, os, signal, pickle, selectors, argparse

# GLOBAL VARIABLES
global discovery_add
discovery_add = ('127.0.0.1', 6000)

# FUNCTIONS
def join():
    """Gets a username and client address, adds them to the lobby, 
    notifies others, and sends room description to the client.
    """
    command, clientAddress = serverSocket.recvfrom(2048)
    for i in range(0, len(lobby)):
        if lobby[i][0].decode() == command.decode():
            serverSocket.sendto("null".encode(), clientAddress)
            return
    serverSocket.sendto("valid".encode(), clientAddress)
    sendDescription()
    lobby.append((command, clientAddress))
    print("User", command.decode(), "joined from address", clientAddress)
    notifyLobby(command.decode() + " entered the room", clientAddress)
    
def notifyLobby(msg, address):
    """Takes a message and address, searched through the lobby list and sends
    the message to every client in the lobby that does not match the given address.
    """ 
    for i in range(0, len(lobby)):
        if lobby[i][1] != address:
            message = "\n" + msg
            serverSocket.sendto(message.encode(), lobby[i][1])
            
def sendDescription():
    """Sends all the room details to the client socket.
    """    
    serverSocket.sendto(name.encode(), clientAddress)
    serverSocket.sendto(description.encode(), clientAddress)
    serverSocket.sendto(pickle.dumps(items), clientAddress)
    serverSocket.sendto(pickle.dumps(lobby), clientAddress)

def roomDescription():
    """Displays room details.
    """ 
    print("Room Starting Description:\n")
    print(name + "\n\n" + description + "\n")
    if len(items) == 0:
        print("There are no items in this room")
    else:
        print("In this room, there is:")
        for i in range(0, len(items)):
            print("\t" + items[i])
    
def clientExit(msg):
    """Check if client is holding any items, if so a protocol is run until the
    server is told that the client has no more items. Then, removes the client
    from the lobby list and notifies others of where the player went (given msg).
    """
    droppedItem, clientAddress = serverSocket.recvfrom(2048)
    while droppedItem.decode().split()[0] == "drop":
        item = droppedItem.decode().split()[1]
        items.append(item)
        droppedItem, clientAddress = serverSocket.recvfrom(2048)
    for i in range(0, len(lobby)):
        if (lobby[i][1] == clientAddress):
            print("User", lobby[i][0].decode(), "with address", clientAddress, "left")
            notifyLobby(lobby[i][0].decode() + msg, clientAddress)
            del lobby[i] 
            return True
            
def create_handler(obj):
    """Handles keyboard interruption
    """
    def _handler(signum, frame):
        discovery_add = ('127.0.0.1', 6000)
        print('Interrupt received, shutting down ...')
        serverSocket.settimeout(1.5)
        serverSocket.sendto(("DEREGISTER" + " " + name).encode(), discovery_add)
        response, discovery_add = serverSocket.recvfrom(2048)
        if response.decode() == "NOTOK":
            print(serverSocket.recvfrom(2048)[0].decode())
            serverSocket.settimeout(1.5)
        notifyLobby("Disconnected from server ... exiting!", None)
        obj.close()
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
        
        # Closing UDP connection
        serverSocket.close()
    return _handler
    
# MAIN 
# Reading required command line options and initializing lobby
lobby = []
items = []
nroom = None
sroom = None
eroom = None
wroom = None
uroom = None
droom = None

parser = argparse.ArgumentParser()
parser.add_argument("name", help="name of the room")
parser.add_argument("description", help="description of the room")
parser.add_argument("item", nargs='*', help="items found in the room by default")
parser.add_argument("-n", dest="north", help="room in north direction")
parser.add_argument("-s", dest="south", help="room in south direction")
parser.add_argument("-e", dest="east", help="room in east direction")
parser.add_argument("-w", dest="west", help="room in west direction")
parser.add_argument("-u", dest="up", help="room in up direction")
parser.add_argument("-d", dest="down", help="room in down direction")
args = parser.parse_args()

name = args.name
description = args.description
items = args.item
nroom = args.north
sroom = args.south
eroom = args.east
wroom = args.west
uroom = args.up
droom = args.down

# Opening UDP connection
serverSocket = socket(AF_INET, SOCK_DGRAM) 
serverSocket.bind(("localhost", 0))
serverSocket.settimeout(1.5)
# Handle Ctrl + C interruption
signal.signal(signal.SIGINT, create_handler(serverSocket))

# Registering with discovery service
serverSocket.sendto(("REGISTER" + " " + name).encode(), discovery_add)
response, discovery_add = serverSocket.recvfrom(2048)
if response.decode() == "NOTOK":
    print(serverSocket.recvfrom(2048)[0].decode())
    exit()

# Displaying starting description
roomDescription()
print("\nRoom will wait for players at port:", serverSocket.getsockname()[1])

# Waiting for input from client
while True:  
    serverSocket.settimeout(86400)
    command, clientAddress = serverSocket.recvfrom(2048)
    serverSocket.settimeout(1.5)
    if command.decode() == "join":
        join()
        
    elif command.decode() == "look":
        sendDescription()
        
    elif command.decode().split()[0] == "take":
        try:
            item = command.decode().split()[1]
            if item in items:
                serverSocket.sendto(item.encode(), clientAddress)
                items.remove(item)
            else:
                serverSocket.sendto("null".encode(), clientAddress)
        except:
            serverSocket.sendto("null".encode(), clientAddress)
            
    elif command.decode().split()[0] == "drop":
        item = command.decode().split()[1]
        items.append(item)
        
    elif command.decode() == "say":
        msg, clientAddress = serverSocket.recvfrom(2048)
        for i in range(0, len(lobby)):
            if lobby[i][1] == clientAddress:
                client = lobby[i][0]
        notifyLobby((client.decode() + " said \"" + msg.decode() + "\""), clientAddress)
    
    elif command.decode() == "north":
        if nroom == None:
            serverSocket.sendto("null".encode(), clientAddress)
        else:
            serverSocket.sendto(nroom.encode(), clientAddress)
            clientExit(" left the room, heading north")
        
    elif command.decode() == "south":
        if sroom == None:
            serverSocket.sendto("null".encode(), clientAddress)
        else:
            serverSocket.sendto(sroom.encode(), clientAddress)
            clientExit(" left the room, heading south")
            
    elif command.decode() == "east":
        if eroom == None:
            serverSocket.sendto("null".encode(), clientAddress)
        else:
            serverSocket.sendto(eroom.encode(), clientAddress)
            clientExit(" left the room, heading east")
        
    elif command.decode() == "west":
        if wroom == None:
            serverSocket.sendto("null".encode(), clientAddress)
        else:
            serverSocket.sendto(wroom.encode(), clientAddress)
            clientExit(" left the room, heading west")
        
    elif command.decode() == "up":
        if uroom == None:
            serverSocket.sendto("null".encode(), clientAddress)
        else:   
            serverSocket.sendto(uroom.encode(), clientAddress)
            clientExit(" left the room, heading up")
        
    elif command.decode() == "down":
        if droom == None:
            serverSocket.sendto("null".encode(), clientAddress)
        else:
            serverSocket.sendto(droom.encode(), clientAddress)
            clientExit(" left the room, heading down")  
            
    elif command.decode() == "exit":
        clientExit(" left the game")
          
    elif command.decode() == "kill":
        # I could not implement the signal class to work in VS Code on Windows 11 so this will suffice
        # for testing on windows.
        print("Kill command given, shutting down ...")
        break
        
# Closing UDP connection
serverSocket.close()


# End of program