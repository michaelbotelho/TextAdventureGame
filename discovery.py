# Author: Michael Botelho
# Assignment 4
# Computer Science 3357
# December 8, 2022

from socket import *
import pickle

#FUNCTIONS
def register(address, name):
    for i in range(0, len(rooms)):
        if rooms[i][0] == address or rooms[i][1] == name:
            return "NOTOK"
    rooms.append((address, name))
    return "OK"

def deregister(name):
    for i in range(0, len(rooms)):
        if rooms[i][1] == name:
            rooms.pop(i)
            return "OK"
    return "NOTOK"
def lookup(name):
    for i in range(0, len(rooms)):
        if rooms[i][1] == name:
            return i
    return -1

port = 6000
rooms = []

discoverySocket = socket(AF_INET, SOCK_DGRAM) 
discoverySocket.bind(("localhost", port))


while True:
    discoverySocket.settimeout(86400)
    req, address = discoverySocket.recvfrom(2048)
    discoverySocket.settimeout(1.5)

    if req.decode().split()[0] == "REGISTER":
        response = register(address, req.decode().split()[1])
        discoverySocket.sendto(response.encode(), address)
        if response == "NOTOK":
            discoverySocket.sendto("Room already exists with given name and address mapping.".encode(), address)
        print(rooms)
    elif req.decode().split()[0] == "DEREGISTER":
        response = deregister(req.decode().split()[1])
        discoverySocket.sendto(response.encode(), address)
        if response == "NOTOK":
            discoverySocket.sendto("No room exists with given name and address mapping.".encode(), address)
        print(rooms)
    elif req.decode().split()[0] == "LOOKUP":
        response = lookup(req.decode().split()[1])
        if response == -1:
            discoverySocket.sendto("NOTOK".encode(), address)
            discoverySocket.sendto(("'" + req.decode().split()[1] + "' " + "not found in rooms.").encode(), address)
        else:
            discoverySocket.sendto("OK".encode(), address)
            discoverySocket.sendto(pickle.dumps(rooms[response][0]), address)