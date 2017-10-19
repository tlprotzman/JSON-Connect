import json
import logging
import os
import socket
import sys
import time



class serverFunctions:
    # Sends data to a client using a dictionary
    def send(self, obj):
        payload = json.dumps(obj)   # Converts the dictionary to a JSON file
        size = len(payload)     # Determines the length of the message
        logging.info("Sending message of size " + str(size))
        logging.debug("Sending " + payload)
        size = self.ensureSize(size, 9999, 4)
        self._send(size)
        self._send(payload)
        return

    # Sends a message to the client
    def _send(self, message):
        totalSent = 0   # Tracks how much of the message has been sent
        message = str(message).encode() # Encodes the message as a utf-8
        while totalSent < len(message): # Continues sending while the message isn't fully set
            totalSent = self.clientSocket.send(message[totalSent:])    # Sends the remainder of the string
        return

    # Listens for a message from the client
    def receive(self):
        logging.debug("Waiting to receive message")
        size = self.clientSocket.recv(4).decode()   # Listens for a message of size 4 to give size of incoming message
        logging.debug("Receiving message of size " + str(size))
        data = self.clientSocket.recv(int(size)).decode()   # Recieves the actual message
        logging.debug("Received " + data)
        obj = json.loads(data)  # Converts the received json file into a python dictionary
        logging.info("Received message from client")
        logging.debug(str(obj))
        return obj

    #  Verifies that the size of the message being sent is within the expected limits
    def ensureSize(self, num, maximum, length):
        num = str(num)  # treats the number as a string
        if float(num) > maximum:    #  See if the value of the num is larger 
            logging.critical("ERROR: Value larger than maximum size. Behavior may not be defined")
            raise ValueError()      # Raise an error if the value is too large
            num = str(maximum)
        if len(num) >= length:
            num = num[:length]
            logging.crirical("ERROR: Length of num longer than maximum allowed length")
            raise ValueError()      # Raise an error if the value is too long
        while len(num) < length:
            num = '0' + num         # Pads the number so that it's the correct length
        return num
    

class server(serverFunctions):

    # Initializes the server, starting it an the specified ip and port
    def __init__(self, args):

        # True while the server is to continue running
        self.running = False

        # Number of times the server will attempt to start
        self.startAttempts = 5
        if "startAttempts" in args.keys():
            self.startAttempts = args["startAttempts"]

        # Extracts the IP for the server to use
        if "ip" not in args.keys():
            logging.critical("IP address not specified in arguments")
            sys.exit(1)
        self.ip = args["ip"]

        # Extracts the port for the server to use
        if "port" not in args.keys():
            logging.critical("Port not specified in arguments")
            sys.exit(1)
        self.port = args["port"]

        # Sets the file that holds the usernames and passwords for users
        self.userFile = "users.txt"
        if "userFile" in args.keys():
            self.userFile = args["userFile"]
        if not os.path.isfile(self.userFile):   # If the file doesn't already exist, create it
            f = open(self.userFile, "w")    # I suppose that's useless because then no one can authenticate...
            f.close

        # Defines the server type
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Starts the server
        self.start()

        self.index = 0  # Tracks the number of connections established

    # Attempts to start the server
    def start(self):
        logging.info("Starting server")
        for i in range(self.startAttempts):
            try:
                self.server.bind((self.ip, self.port)) # Attempts to bind the server to the port and IP
                break
            except: # Catches all errors and waits a second before trying again
                if i == 0:
                    logging.error("Error: Unable to start server at " + self.ip + " on port " + str(self.port))
                    logging.error("Perhaps the server did not go down cleanly and the port hasn't been released?")
                elif i == self.startAttempts - 1:
                    logging.critical("Exiting...")
                    sys.exit(1)
                logging.error("Trying again...")
                time.sleep(1)
        # Success! 
        self.running = True
        logging.info("Started server at " + self.ip + " on port " + str(self.port))
        return

    # Stops the server
    # TODO: Cleanly close the connections
    def stop(self):
        logging.info("Stopping the server...")
        self.running = False
        self.server.close()

    # Listens for new connections to the server
    def listen(self):
        logging.info("Listening for new connection...")
        self.server.listen(1)   # Will listen for a new user connection
        self.clientSocket, address = self.server.accept()

        user = None
        while not user:
            user = self.authenticate()
        name = "clientThread-" + str(self.index) + "-" + str(user)
        self.index += 1
        connection = serverThread(name, self.clientSocket)
        return connection



    def authenticate(self):
        logging.info("New connection made, waiting for authentication...")
        # Sets a short timeout to force quick authentication 
        self.clientSocket.settimeout(4)
        message = self.receive()
        user = message["user"]
        auth = message["token"]
        self.clientSocket.settimeout(None)
        # Uses sha256 hash
        logging.debug("User is " + str(user))
        logging.debug("Auth is " + str(auth))

        accounts = dict()

        with open(self.userFile) as file:
            for data in file.readlines():
                # print(data)
                usr, passwd = data.split()
                accounts[usr] = passwd
                logging.debug("Loaded account " + usr)

        try:
            # print(auth)
            # print(accounts[user])
            if auth != accounts[user]:
                logging.info("Authentication failed.  Disconnecting user, password is incorrect")
                self._send(0)   # Sends a 0, indicating a failed authentication
                self.clientSocket.close()
                return None
        except KeyError:
            logging.info("Authentication failed.  Disconnecting user, user doesn't exist")
            self._send(0)   # Sends a 0, indicating a failed authentication
            self.clientSocket.close()
            return None

        self._send(1)       # Sends a 1, indication a successful authentication
        logging.info("Authentication successful! User " + user + " connected.")
        return user


class serverThread(serverFunctions):

    def __init__(self, name, clientSocket):
        self.name = name
        self.clientSocket = clientSocket

    def getName(self):
        return self.name
