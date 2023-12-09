Client-Server Game
===============================================================
You are given 3 files for this game to work...
room.py - which is the server side of the game
player.py - which is the client side of the game
discovery.py - which allows a room to be looked up by name (name to address conversion)

To Play:
1. Start a server:
	- run room.py with command line options following this syntax: python3 room.py [port] [room name] [room description] [room items] [-n] [-s] [-e] [-w] [-u] [-d]
		- [port]: an integer number to recieve/send packets from/to
		- [room name]: any string that you want the room to be called
		- [room description]: any string which will describe the room
		- [room items]: any string that will represent an item in the room (list multiple by separating with spaces)
		- [-n], [-s], [-e], [-w], [-u], [-d]: these flags should be followed by a host servername in the format of 'room://host:port' and they represent a new room in each direction (north, south, east, west, up, and down).
2. Run the game client:
	- run player.py with command line options following this syntax: python3 player.py [username] [host servername]
		- [username]: any one word string that you want to been seen as on the server
		- [host servername]: a server that you want to connect to in the format of 'room://host:port'
3. Play the game using these commands:
	- look: displays the room name, description, and items in the room.
	- take [item]: moves an existing item from the room to the users inventory
	- drop [item]: moves an existing item from the users inventory to the room
	- inventory: displays the contents of the users inventory
	- say: followed by a message after the prompt, this command sends your message to all players in the lobby
	- north: moves the player into the room to the north, if it exists, and leaves all items behind that were in the users inventory
	- south: moves the player into the room to the south, if it exists, and leaves all items behind that were in the users inventory
	- east: moves the player into the room to the east, if it exists, and leaves all items behind that were in the users inventory
	- west: moves the player into the room to the west, if it exists, and leaves all items behind that were in the users inventory
	- up: moves the player into the room above, if it exists, and leaves all items behind that were in the users inventory
	- down: moves the player into the room below, if it exists, and leaves all items behind that were in the users inventory
	- exit: disconnects the user from the server and leaves all items behind that were in the users inventory