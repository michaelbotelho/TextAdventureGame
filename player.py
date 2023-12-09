# Author: Michael Botelho
# Assignment 4
# Computer Science 3357
# December 8, 2022

from socket import *
from signal import *
from urllib import parse
import sys, os, signal, pickle, selectors, argparse

# Making serverAddress global to be able to switch communication to other servers
global serverAddress
serverAddress = ('', '')

# FUNCTIONS
def join(address):
    """This function sends a join command to the server 
    along with the clients username and receives room description.
    User is denied if the username is taken.
    
    Args:
        address (tuple): a hostname and port number pair
        
    Returns:
        Boolean: to represent successful execution 
    """  
    try:    
        clientSocket.sendto("join".encode(), address)
        clientSocket.sendto(playerName.encode(), address)
        auth, add = clientSocket.recvfrom(2048)
        if auth.decode() == "null":
            print("Username taken")
            return False
        else:
            recvDescription()
            global serverAddress
            serverAddress = address
            return True
    except Exception as e:
        print(e)
        return False
    
def recvDescription():
    """This function receives the room description, items, and players in lobby from the 
    server and displays it to the client.
    """
    try:    
        name, serverAddress = clientSocket.recvfrom(2048)
        description, serverAddress = clientSocket.recvfrom(2048)
        data, serverAddress = clientSocket.recvfrom(2048)
        lobby, serverAddress =  clientSocket.recvfrom(2048)
        print(name.decode() + "\n\n" + description.decode() + "\n")
        items = pickle.loads(data)
        players = pickle.loads(lobby)
        if len(items) == 0 and len(players) == 0:
            print("There are no items or players in this room.")
        else:
            print("In this room, there is:")
            for i in range(0, len(items)):
                print("\t" + items[i])
            for i in range(0, len(players)):
                if players[i][0].decode() != playerName:
                    print("\t" + players[i][0].decode())
        return True
    except Exception as e:
        print(e)
        
def take():
    """This function receives an item from the server (or null) and either 
    adds that item to the client inventory, or produces an error message.
    """    
    item, serverAddress = clientSocket.recvfrom(2048)
    if item.decode() == "null":
        print("Cannot pick up an item that does not exist.")
    else:
        inventory.append(item.decode())
        print(item.decode(), "taken")        
    
def drop(item):
    """This function checks if the given item exists in inventory and removes 
    it from client inventory. If item is not in inventory, throws error.

    Args:
        item (String): an item represented by the second part of the command 

    Returns:
        Boolean: to decide whether to send the server a drop command or not
    """    
    try:
        if item == "all":
            dropAll(inventory)
            return True
        inventory.index(item)
        inventory.remove(item)
        print(item, "dropped")
        return True
    except:
        print("You are not holding", item + ".")
        return False

def dropAll(list):
    """This function removes all items in the players inventory in succession.
    Calls on drop() function.

    Args:
        list (String Array): a list of items representing the players inventory

    Returns:
        Boolean: to represent successful execution 
    """ 
    for i in range(0, len(list)):
        if len(list) == 0:
            clientSocket.sendto("done".encode(), serverAddress)
            return True
        else:
            command = "drop " + list[0]
            clientSocket.sendto(command.encode(), serverAddress)
            drop(list[0])
    clientSocket.sendto("done".encode(), serverAddress)
    return True
    
def getInventory():
    """This function displays user inventory.
    """    
    if len(inventory) <= 0:
        print("Inventory is empty.")
    else:
        print("You are holding:")
        for i in range(0, len(inventory)):
            print("\t" + inventory[i])

def switchServer(name):
    """This function receives an address from the server and either produces and error
    if the room does not exist, or connects the client to the other room server.
    """ 
    discovery_add = ('127.0.0.1', 6000)
    clientSocket.sendto(("LOOKUP" + " " + name).encode(), discovery_add)
    response, discovery_add = clientSocket.recvfrom(2048)
    if response.decode() == "NOTOK":
        print(clientSocket.recvfrom(2048)[0].decode())
        return False
    elif response.decode() == "OK":
        newAdd, add = clientSocket.recvfrom(2048)
        print(newAdd.decode())
        global inventory
        dropAll(inventory)
        updateRoom(newAdd.decode()[0])
        join(newAdd)
        return True

def updateRoom(new_address):
    global serverAddress
    serverAddress = new_address

def create_handler(obj):
    """Handles keyboard interruption
    """
    def _handler(signum, frame):
        clientSocket.sendto("exit".encode(), serverAddress)
        dropAll(inventory)
        clientSocket.sendto("done".encode(), serverAddress)
        print('Interrupt received, shutting down ...')
        obj.close()
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
    return _handler

def sockIn(sock, mask):
    """This function handles any socket input.
    """ 
    msg, addr = sock.recvfrom(2048)
    print(msg.decode())
    if msg.decode() == "\n" + "Disconnected from server ... exiting!":
        exit()


def keyIn(conn, mask):
    """This function handles any keyboard input.
    """ 
    command = input()
    command = command.strip()
    
    if command == "":
        print("Enter a valid command or '" + "exit" + "' to leave")
        
    elif command == "look":
        clientSocket.sendto(command.encode(), serverAddress)
        recvDescription()
        
    elif command.split()[0] == "take":
        clientSocket.sendto(command.encode(), serverAddress)
        take()
        
    elif command.split()[0] == "drop":
        try:
            if command.split()[1] == "all":
                drop(command.split()[1])
                
            elif drop(command.split()[1]):
                clientSocket.sendto(command.encode(), serverAddress)
                
        except:
            print("Cannot drop and item that does not exist.")
            
    elif command == "inventory":
        getInventory()
        
    elif command == "say":
        clientSocket.sendto(command.encode(), serverAddress)
        print("What did you want to say?")
        clientSocket.sendto(input().encode(), serverAddress)
    
    elif command == "north":
        clientSocket.sendto(command.encode(), serverAddress)
        room, serverAdd = clientSocket.recvfrom(2048)
        switchServer(room.decode())
        
    elif command == "south":
        clientSocket.sendto(command.encode(), serverAddress)
        switchServer()
        
    elif command == "east":
        clientSocket.sendto(command.encode(), serverAddress)
        switchServer()
        
    elif command == "west":
        clientSocket.sendto(command.encode(), serverAddress)
        switchServer()
            
    elif command == "up":
        clientSocket.sendto(command.encode(), serverAddress)
        switchServer()
    
    elif command == "down":
        clientSocket.sendto(command.encode(), serverAddress)
        switchServer()
                    
    elif command == "exit":
        clientSocket.sendto(command.encode(), serverAddress)
        dropAll(inventory)
        
        clientSocket.sendto("done".encode(), serverAddress)
        print("Bye!")
        exit() 
    
    elif command == "kill":
        # I could not implement the signal class to work in VS Code on Windows 11 so 
        # this will suffice for testing on windows.
        clientSocket.sendto(command.encode(), serverAddress)
        print("server terminated.")
        exit()
    
    else:
        print("'"+ command + "'", "is not a valid command")
    
    
# MAIN
# Reading required command line options and initializing inventory
global inventory
inventory = []

parser = argparse.ArgumentParser()
parser.add_argument("name", help="username to be associated")
parser.add_argument("room", help="name of the room")
args = parser.parse_args()

playerName = args.name
room = args.room

discovery_add = ('127.0.0.1', 6000)

# Opening UDP connection
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(("localhost", 0))
clientSocket.settimeout(2.5)
# Handle Ctrl + C interruption
signal.signal(signal.SIGINT, create_handler(clientSocket))

# Handle selection of stdin and socket input
sel = selectors.DefaultSelector()
sel.register(clientSocket, selectors.EVENT_READ, sockIn)
sel.register(sys.stdin, selectors.EVENT_READ, keyIn)

# Sending join message
clientSocket.sendto(("LOOKUP" + " " + room).encode(), discovery_add)
response, discovery_add = clientSocket.recvfrom(2048)
if response.decode() == "NOTOK":
    print(clientSocket.recvfrom(2048)[0].decode())
    exit()
elif response.decode() == "OK":
    serverAddress = pickle.loads(clientSocket.recvfrom(2048)[0])

try:
    if not join(serverAddress):
        exit()
except Exception as e:
    print(e)
    exit()

# Waiting for event from keyboard or socket
running = True
while running:
    print("> ", end='', flush=True)
    
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
        


# End of program