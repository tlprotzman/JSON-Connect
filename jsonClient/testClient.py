import logging

import client

logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
logging.info("Logging started...")

username = ("tristan", "test")

args = dict()
args["ip"] = "127.0.0.1"
args["port"] = 4285
args["user"] = username

#message = input("What message would you like to send? ")
message = "Hello World!"

server = client.client(args)
server.send({"message":message})
message = server.receive()
print(message["message"])
