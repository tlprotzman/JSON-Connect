import hashlib
import logging
import socket
import json


class client:

    def __init__(self, args):
        
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

        logging.info("Connecting to server at " + str(self.ip) + " on port " + str(self.port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        logging.info("Connection made, authenticating...")
        self.authenticate(args["user"])


    def authenticate(self, user):
        # Expects a tulpe containing the username and password

        name = user[0]
        token = user[1]

        logging.debug("Authenticating with user " + str(name))
        hasher = hashlib.sha256()
        hasher.update(token.encode())
        hashedToken = hasher.hexdigest()
        auth = {"mode" : "authenticate", 
                "user" : name, "token" : hashedToken}
        self.send(auth)
        if self.socket.recv(1):
            return True
        return False


    def send(self, obj):
        payload = json.dumps(obj)
        size = len(payload)
        logging.info("Sending message of size " + str(size))
        logging.debug("Sending " + payload)
        size = self.ensureSize(size, 9999, 4)
        self._send(size)
        self._send(payload)
        return


    def _send(self, message):
        totalSent = 0
        message = str(message).encode()
        while totalSent < len(message):
            totalSent += self.socket.send(message[totalSent:])
            logging.debug("Sent " + str(totalSent) + " of " + str(len(message)) + "bytes")
        return


    def receive(self):
        logging.debug("Waiting to receive message")
        size = self.socket.recv(4)
        logging.debug("Receiving message of size " + str(size))
        data = self.socket.recv(int(size)).decode()
        logging.debug("Received " + str(data))
        obj = json.loads(data)
        logging.info("Received message from server")
        return obj


    def ensureSize(self, message, maximum, length):
        message = str(message)
        if float(message) > maximum:
            logging.critical("ERROR: Value larger than maximum size. Behavior may not be defined")
            message = str(maximum)
        if len(message) >= length:
            message = message[:length]
        while len(message) < length:
            message = '0' + message
        return message